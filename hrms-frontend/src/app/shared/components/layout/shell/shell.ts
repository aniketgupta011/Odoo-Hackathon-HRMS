import { Component, OnDestroy, OnInit } from '@angular/core';
import { AuthService, User } from '../../../../core/services/auth.service';
import { Subscription } from 'rxjs';
import { SharedModule } from '../../../shared.module';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [SharedModule, RouterModule, CommonModule],
  templateUrl: './shell.html',
  styleUrls: ['./shell.scss']
})
export class Shell implements OnInit, OnDestroy {
  currentUser: User | null = null;
  private sub = new Subscription();

  constructor(public authService: AuthService) {}

  ngOnInit(): void {
    this.sub.add(
      this.authService.currentUser$.subscribe(user => {
        this.currentUser = user;
      })
    );
  }

  logout(): void {
    this.authService.logout();
  }

  ngOnDestroy(): void {
    this.sub.unsubscribe();
  }
}
