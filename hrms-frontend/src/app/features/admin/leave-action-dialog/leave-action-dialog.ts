import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

export interface LeaveActionData {
  leave_id: string;
  action: 'APPROVE' | 'REJECT';
}

@Component({
  selector: 'app-leave-action-dialog',
  standalone: false,
  templateUrl: './leave-action-dialog.html',
  styleUrls: ['./leave-action-dialog.scss']
})
export class LeaveActionDialog {
  actionForm: FormGroup;

  constructor(
    public dialogRef: MatDialogRef<LeaveActionDialog>,
    @Inject(MAT_DIALOG_DATA) public data: LeaveActionData,
    private fb: FormBuilder
  ) {
    this.actionForm = this.fb.group({
      admin_remarks: ['', data.action === 'REJECT' ? Validators.required : null]
    });
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  onSubmit(): void {
    if (this.actionForm.invalid) return;
    this.dialogRef.close({
      action: this.data.action,
      admin_remarks: this.actionForm.value.admin_remarks
    });
  }
}
