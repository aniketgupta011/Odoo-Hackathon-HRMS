import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { AttendanceRoutingModule } from './attendance-routing.module';
import { SharedModule } from '../../shared/shared.module';
import { AttendanceHistory } from './attendance-history/attendance-history';

@NgModule({
  declarations: [AttendanceHistory],
  imports: [
    CommonModule,
    AttendanceRoutingModule,
    SharedModule
  ]
})
export class AttendanceModule { }
