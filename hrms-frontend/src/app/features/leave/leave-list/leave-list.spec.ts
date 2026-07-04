import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LeaveList } from './leave-list';

describe('LeaveList', () => {
  let component: LeaveList;
  let fixture: ComponentFixture<LeaveList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [LeaveList],
    }).compileComponents();

    fixture = TestBed.createComponent(LeaveList);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
