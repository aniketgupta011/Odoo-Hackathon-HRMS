import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';

import { PayrollRoutingModule } from './payroll-routing.module';
import { SharedModule } from '../../shared/shared.module';
import { PayrollSummary } from './payroll-summary/payroll-summary';

@NgModule({
  declarations: [PayrollSummary],
  imports: [
    CommonModule,
    PayrollRoutingModule,
    SharedModule,
    ReactiveFormsModule
  ]
})
export class PayrollModule { }
