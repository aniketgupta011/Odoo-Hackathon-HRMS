import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';

export interface LeaveRequest {
  id: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  status: string;
  reason?: string;
  admin_remarks?: string;
}

@Component({
  selector: 'app-leave-list',
  standalone: false,
  templateUrl: './leave-list.html',
  styleUrls: ['./leave-list.scss']
})
export class LeaveList implements OnInit {
  displayedColumns: string[] = ['leave_type', 'start_date', 'end_date', 'status', 'reason', 'admin_remarks'];
  dataSource: LeaveRequest[] = [];
  isLoading = true;
  isApplying = false;

  leaveForm!: FormGroup;

  leaveTypes = ['PAID', 'SICK', 'UNPAID'];

  constructor(
    private http: HttpClient,
    private fb: FormBuilder,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.leaveForm = this.fb.group({
      leave_type: ['', Validators.required],
      start_date: ['', Validators.required],
      end_date: ['', Validators.required],
      reason: ['', Validators.required]
    });

    this.loadLeaves();
  }

  loadLeaves(): void {
    this.isLoading = true;
    this.http.get<LeaveRequest[]>('http://localhost:8000/api/v1/leaves/my-requests').subscribe({
      next: (data) => {
        this.dataSource = data;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  formatDate(dateObj: Date): string {
    return dateObj.toISOString().split('T')[0];
  }

  applyLeave(): void {
    if (this.leaveForm.invalid) return;

    this.isApplying = true;
    const formValues = this.leaveForm.value;
    
    const payload = {
      ...formValues,
      start_date: this.formatDate(formValues.start_date),
      end_date: this.formatDate(formValues.end_date)
    };

    this.http.post('http://localhost:8000/api/v1/leaves/apply', payload).subscribe({
      next: () => {
        this.isApplying = false;
        this.snackBar.open('Leave application submitted successfully', 'Close', { duration: 3000 });
        this.leaveForm.reset();
        this.loadLeaves();
      },
      error: () => {
        this.isApplying = false;
      }
    });
  }
}
