import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LeaveList } from './leave-list/leave-list';

const routes: Routes = [
  { path: '', component: LeaveList }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class LeaveRoutingModule { }
