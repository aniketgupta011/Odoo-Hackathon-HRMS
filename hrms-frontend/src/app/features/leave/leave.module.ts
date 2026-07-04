import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';

import { LeaveRoutingModule } from './leave-routing.module';
import { SharedModule } from '../../shared/shared.module';
import { LeaveList } from './leave-list/leave-list';

@NgModule({
  declarations: [LeaveList],
  imports: [
    CommonModule,
    LeaveRoutingModule,
    SharedModule,
    ReactiveFormsModule
  ]
})
export class LeaveModule { }
