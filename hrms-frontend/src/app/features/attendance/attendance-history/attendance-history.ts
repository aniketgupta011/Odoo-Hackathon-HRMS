import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';

export interface AttendanceRecord {
  id: string;
  date: string;
  check_in?: string;
  check_out?: string;
  status: string;
  hours_worked?: number;
}

@Component({
  selector: 'app-attendance-history',
  standalone: false,
  templateUrl: './attendance-history.html',
  styleUrls: ['./attendance-history.scss']
})
export class AttendanceHistory implements OnInit {
  displayedColumns: string[] = ['date', 'check_in', 'check_out', 'status', 'hours_worked'];
  dataSource: AttendanceRecord[] = [];
  isLoading = true;
  isActionLoading = false;

  constructor(private http: HttpClient, private snackBar: MatSnackBar) {}

  ngOnInit(): void {
    this.loadHistory();
  }

  loadHistory(): void {
    this.isLoading = true;
    this.http.get<AttendanceRecord[]>('http://localhost:8000/api/v1/attendance/my-history').subscribe({
      next: (data) => {
        this.dataSource = data;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  checkIn(): void {
    this.isActionLoading = true;
    this.http.post('http://localhost:8000/api/v1/attendance/check-in', {}).subscribe({
      next: () => {
        this.isActionLoading = false;
        this.snackBar.open('Checked in successfully', 'Close', { duration: 3000 });
        this.loadHistory();
      },
      error: (err) => {
        this.isActionLoading = false;
      }
    });
  }

  checkOut(): void {
    this.isActionLoading = true;
    this.http.post('http://localhost:8000/api/v1/attendance/check-out', {}).subscribe({
      next: () => {
        this.isActionLoading = false;
        this.snackBar.open('Checked out successfully', 'Close', { duration: 3000 });
        this.loadHistory();
      },
      error: (err) => {
        this.isActionLoading = false;
      }
    });
  }
}
