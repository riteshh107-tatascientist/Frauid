#!/usr/bin/env python
"""
Create an admin user for FraudGuard AI

Usage:
    python -m backend.scripts.create_admin
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from getpass import getpass
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.models import User, UserRole


def create_admin():
    """Create an admin user interactively"""
    print("\n" + "="*60)
    print("FraudGuard AI - Admin User Creation")
    print("="*60 + "\n")
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # Get email
        email = input("Enter admin email: ").strip()
        
        if not email:
            print("❌ Email cannot be empty")
            return False
        
        # Check if email already exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"❌ Email {email} already registered")
            return False
        
        # Get username
        username = input("Enter admin username: ").strip()
        
        if not username or len(username) < 3:
            print("❌ Username must be at least 3 characters")
            return False
        
        # Check if username already exists
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"❌ Username {username} already taken")
            return False
        
        # Get password securely
        print("\nPassword requirements:")
        print("  - Minimum 8 characters")
        print("  - Should be strong and unique")
        
        while True:
            password = getpass("Enter admin password (hidden): ")
            
            if len(password) < 8:
                print("❌ Password must be at least 8 characters")
                continue
            
            password_confirm = getpass("Confirm password (hidden): ")
            
            if password != password_confirm:
                print("❌ Passwords do not match")
                continue
            
            break
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create admin user
        admin = User(
            username=username,
            email=email,
            hashed_password=password_hash,
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("\n" + "="*60)
        print("✅ Admin user created successfully!")
        print("="*60)
        print(f"Username: {admin.username}")
        print(f"Email: {admin.email}")
        print(f"Role: {admin.role.value}")
        print(f"Active: {admin.is_active}")
        print(f"ID: {admin.id}")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating admin: {str(e)}")
        db.rollback()
        return False
    
    finally:
        db.close()


if __name__ == "__main__":
    success = create_admin()
    sys.exit(0 if success else 1)
