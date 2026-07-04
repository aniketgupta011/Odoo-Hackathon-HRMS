import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { LeaveActionDialog } from '../leave-action-dialog/leave-action-dialog';

export interface AdminLeaveRequest {
  id: string;
  employee_id: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  status: string;
  reason?: string;
  admin_remarks?: string;
}

@Component({
  selector: 'app-admin-dashboard',
  standalone: false,
  templateUrl: './admin-dashboard.html',
  styleUrls: ['./admin-dashboard.scss']
})
export class AdminDashboard implements OnInit {
  displayedColumns: string[] = ['employee_id', 'leave_type', 'start_date', 'end_date', 'status', 'reason', 'actions'];
  dataSource: AdminLeaveRequest[] = [];
  isLoading = true;

  constructor(
    private http: HttpClient,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadAllLeaves();
  }

  loadAllLeaves(): void {
    this.isLoading = true;
    this.http.get<AdminLeaveRequest[]>('http://localhost:8000/api/v1/leaves/').subscribe({
      next: (data) => {
        // Simple client side sort: Pending requests first
        this.dataSource = data.sort((a, b) => {
          if (a.status === 'PENDING' && b.status !== 'PENDING') return -1;
          if (a.status !== 'PENDING' && b.status === 'PENDING') return 1;
          return 0;
        });
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  openActionDialog(leaveId: string, action: 'APPROVE' | 'REJECT'): void {
    const dialogRef = this.dialog.open(LeaveActionDialog, {
      width: '400px',
      data: { leave_id: leaveId, action }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.processAction(leaveId, result.action, result.admin_remarks);
      }
    });
  }

  private processAction(leaveId: string, action: string, adminRemarks: string): void {
    this.isLoading = true;
    const payload = { action, admin_remarks: adminRemarks };
    
    this.http.patch(`http://localhost:8000/api/v1/leaves/${leaveId}/action`, payload).subscribe({
      next: () => {
        this.snackBar.open(`Leave request ${action.toLowerCase()}d`, 'Close', { duration: 3000 });
        this.loadAllLeaves();
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }
}
