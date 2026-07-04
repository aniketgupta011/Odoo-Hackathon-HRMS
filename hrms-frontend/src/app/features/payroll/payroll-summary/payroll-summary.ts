import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../../../core/services/auth.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

export interface PayrollData {
  id: string;
  employee_id: string;
  base_salary: number;
  bonus: number;
  deductions: number;
  net_salary?: number;
}

export interface EmployeeData {
  id: string;
  full_name: string;
  email: string;
  role: string;
}

@Component({
  selector: 'app-payroll-summary',
  standalone: false,
  templateUrl: './payroll-summary.html',
  styleUrls: ['./payroll-summary.scss']
})
export class PayrollSummary implements OnInit {
  isAdmin = false;
  isLoading = true;
  isSaving = false;
  
  myPayroll: PayrollData | null = null;
  employees: EmployeeData[] = [];
  
  // For admin updates
  selectedEmployeeId = '';
  payrollForm!: FormGroup;

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private snackBar: MatSnackBar,
    private fb: FormBuilder
  ) {
    this.isAdmin = this.authService.hasRole(['HR_ADMIN']);
  }

  ngOnInit(): void {
    if (this.isAdmin) {
      this.payrollForm = this.fb.group({
        base_salary: [0, [Validators.required, Validators.min(0)]],
        bonus: [0, Validators.min(0)],
        deductions: [0, Validators.min(0)]
      });
      this.loadEmployees();
    } else {
      this.loadMyPayroll();
    }
  }

  loadMyPayroll(): void {
    this.isLoading = true;
    this.http.get<PayrollData>('http://localhost:8000/api/v1/payroll/me').subscribe({
      next: (data) => {
        this.myPayroll = data;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  loadEmployees(): void {
    this.isLoading = true;
    this.http.get<EmployeeData[]>('http://localhost:8000/api/v1/employees/').subscribe({
      next: (data) => {
        this.employees = data;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  selectEmployee(empId: string): void {
    this.selectedEmployeeId = empId;
    // Just reset form. In a real app we might fetch the specific employee's current payroll first if available
    this.payrollForm.reset({ base_salary: 0, bonus: 0, deductions: 0 });
  }

  updatePayroll(): void {
    if (this.payrollForm.invalid || !this.selectedEmployeeId) return;

    this.isSaving = true;
    this.http.put(`http://localhost:8000/api/v1/payroll/${this.selectedEmployeeId}`, this.payrollForm.value).subscribe({
      next: () => {
        this.isSaving = false;
        this.snackBar.open('Payroll updated successfully', 'Close', { duration: 3000 });
        this.selectedEmployeeId = '';
        this.payrollForm.reset();
      },
      error: () => {
        this.isSaving = false;
      }
    });
  }
}
