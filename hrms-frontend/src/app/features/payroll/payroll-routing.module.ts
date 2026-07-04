import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { PayrollSummary } from './payroll-summary/payroll-summary';

const routes: Routes = [
  { path: '', component: PayrollSummary }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class PayrollRoutingModule { }
