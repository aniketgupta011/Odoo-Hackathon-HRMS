import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { DashboardRoutingModule } from './dashboard-routing.module';
import { SharedModule } from '../../shared/shared.module';
import { Profile } from './profile/profile';
import { ReactiveFormsModule } from '@angular/forms';

@NgModule({
  declarations: [Profile],
  imports: [
    CommonModule,
    DashboardRoutingModule,
    SharedModule,
    ReactiveFormsModule
  ]
})
export class DashboardModule { }
