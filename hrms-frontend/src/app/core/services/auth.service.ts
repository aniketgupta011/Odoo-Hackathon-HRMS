import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { Router } from '@angular/router';

export interface User {
  id: string;
  email: string;
  role: 'EMPLOYEE' | 'HR_ADMIN';
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:8000/api/v1/auth';
  private readonly TOKEN_KEY = 'hrms_token';
  
  // Reactive state
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();
  
  // Using signals for modern Angular reactivity
  public isAuthenticated = signal<boolean>(false);

  constructor(private http: HttpClient, private router: Router) {
    this.checkInitialAuth();
  }

  private checkInitialAuth(): void {
    const token = localStorage.getItem(this.TOKEN_KEY);
    if (token) {
      this.decodeAndSetUser(token);
    }
  }

  login(credentials: any): Observable<AuthResponse> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    return this.http.post<AuthResponse>(`${this.apiUrl}/login`, formData).pipe(
      tap(response => {
        localStorage.setItem(this.TOKEN_KEY, response.access_token);
        this.decodeAndSetUser(response.access_token);
      })
    );
  }

  register(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/register`, data);
  }

  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    this.currentUserSubject.next(null);
    this.isAuthenticated.set(false);
    this.router.navigate(['/auth/login']);
  }

  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  private decodeAndSetUser(token: string): void {
    try {
      // Basic JWT decode (payload is base64url encoded)
      const payload = JSON.parse(atob(token.split('.')[1]));
      
      const user: User = {
        id: payload.sub,
        email: payload.email || payload.sub, // Depends on token payload structure
        role: payload.role || 'EMPLOYEE'
      };
      
      this.currentUserSubject.next(user);
      this.isAuthenticated.set(true);
    } catch (e) {
      console.error('Invalid token format');
      this.logout();
    }
  }

  hasRole(requiredRoles: string[]): boolean {
    const user = this.currentUserSubject.value;
    if (!user) return false;
    return requiredRoles.includes(user.role);
  }
}
