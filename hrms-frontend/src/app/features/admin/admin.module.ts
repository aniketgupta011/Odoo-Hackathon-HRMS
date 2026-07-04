import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';

import { AdminRoutingModule } from './admin-routing.module';
import { SharedModule } from '../../shared/shared.module';
import { AdminDashboard } from './admin-dashboard/admin-dashboard';
import { LeaveActionDialog } from './leave-action-dialog/leave-action-dialog';

@NgModule({
  declarations: [AdminDashboard, LeaveActionDialog],
  imports: [
    CommonModule,
    AdminRoutingModule,
    SharedModule,
    ReactiveFormsModule
  ]
})
export class AdminModule { }
