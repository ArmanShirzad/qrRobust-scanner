#!/usr/bin/env python3
"""
Migration script from SQLite to PostgreSQL
Run this once to migrate your existing data
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URLs
SQLITE_URL = "sqlite:///./qr_reader.db"
POSTGRES_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/qr_app")

def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    
    # Create engines
    sqlite_engine = create_engine(SQLITE_URL)
    postgres_engine = create_engine(POSTGRES_URL)
    
    # Create sessions
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    PostgresSession = sessionmaker(bind=postgres_engine)
    
    sqlite_session = SQLiteSession()
    postgres_session = PostgresSession()
    
    try:
        # Migrate Users
        print("Migrating users...")
        users = sqlite_session.execute(text("SELECT * FROM users")).fetchall()
        for user in users:
            postgres_session.execute(text("""
                INSERT INTO users (id, email, password_hash, tier, is_active, is_verified, created_at)
                VALUES (:id, :email, :password_hash, :tier, :is_active, :is_verified, :created_at)
                ON CONFLICT (id) DO NOTHING
            """), dict(user._mapping))
        
        # Migrate QR Codes
        print("Migrating QR codes...")
        qr_codes = sqlite_session.execute(text("SELECT * FROM qr_codes")).fetchall()
        for qr in qr_codes:
            postgres_session.execute(text("""
                INSERT INTO qr_codes (id, user_id, short_url, destination_url, title, description,
                                    error_correction_level, size, border, foreground_color, background_color,
                                    logo_url, scan_count, last_scanned_at, created_at, updated_at, expires_at, is_active)
                VALUES (:id, :user_id, :short_url, :destination_url, :title, :description,
                       :error_correction_level, :size, :border, :foreground_color, :background_color,
                       :logo_url, :scan_count, :last_scanned_at, :created_at, :updated_at, :expires_at, :is_active)
                ON CONFLICT (id) DO NOTHING
            """), dict(qr._mapping))
        
        postgres_session.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        postgres_session.rollback()
    finally:
        sqlite_session.close()
        postgres_session.close()

if __name__ == "__main__":
    migrate_data()
