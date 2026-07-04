import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LeaveActionDialog } from './leave-action-dialog';

describe('LeaveActionDialog', () => {
  let component: LeaveActionDialog;
  let fixture: ComponentFixture<LeaveActionDialog>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [LeaveActionDialog],
    }).compileComponents();

    fixture = TestBed.createComponent(LeaveActionDialog);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
