import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';
import { Shell } from './shared/components/layout/shell/shell';

export const routes: Routes = [
  { 
    path: 'auth', 
    loadChildren: () => import('./features/auth/auth.module').then(m => m.AuthModule) 
  },
  {
    path: '',
    component: Shell,
    canActivate: [authGuard],
    children: [
      { 
        path: 'dashboard', 
        loadChildren: () => import('./features/dashboard/dashboard.module').then(m => m.DashboardModule)
      },
      { 
        path: 'attendance', 
        loadChildren: () => import('./features/attendance/attendance.module').then(m => m.AttendanceModule)
      },
      { 
        path: 'leave', 
        loadChildren: () => import('./features/leave/leave.module').then(m => m.LeaveModule)
      },
      {
        path: 'payroll',
        loadChildren: () => import('./features/payroll/payroll.module').then(m => m.PayrollModule)
      },
      { 
        path: 'admin', 
        loadChildren: () => import('./features/admin/admin.module').then(m => m.AdminModule),
        canActivate: [roleGuard(['HR_ADMIN'])]
      },
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' }
    ]
  },
  { path: '**', redirectTo: '/auth/login' }
];
