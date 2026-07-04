import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../../../core/services/auth.service';

export interface EmployeeProfile {
  id: string;
  email: string;
  full_name: string;
  role: string;
  phone_number?: string;
  address?: string;
}

@Component({
  selector: 'app-profile',
  standalone: false,
  templateUrl: './profile.html',
  styleUrls: ['./profile.scss']
})
export class Profile implements OnInit {
  profileForm!: FormGroup;
  profileData!: EmployeeProfile;
  isLoading = true;
  isSaving = false;
  isEditing = false;
  isAdmin = false;

  constructor(
    private http: HttpClient,
    private fb: FormBuilder,
    private authService: AuthService
  ) {
    this.isAdmin = this.authService.hasRole(['HR_ADMIN']);
  }

  ngOnInit(): void {
    this.profileForm = this.fb.group({
      full_name: ['', Validators.required],
      email: [{ value: '', disabled: !this.isAdmin }, [Validators.required, Validators.email]],
      phone_number: [''],
      address: ['']
    });

    this.loadProfile();
  }

  loadProfile(): void {
    this.http.get<EmployeeProfile>('http://localhost:8000/api/v1/employees/me').subscribe({
      next: (data) => {
        this.profileData = data;
        this.profileForm.patchValue(data);
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  toggleEdit(): void {
    this.isEditing = !this.isEditing;
    if (!this.isEditing) {
      // Revert changes
      this.profileForm.patchValue(this.profileData);
    }
  }

  saveProfile(): void {
    if (this.profileForm.invalid) return;
    
    this.isSaving = true;
    const updateData = this.profileForm.getRawValue(); // gets disabled fields too if needed
    
    this.http.put('http://localhost:8000/api/v1/employees/me', updateData).subscribe({
      next: () => {
        this.isSaving = false;
        this.isEditing = false;
        this.loadProfile();
      },
      error: () => {
        this.isSaving = false;
      }
    });
  }
}
