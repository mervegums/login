#!/usr/bin/env python3
"""
Database setup script for Customer Management API
Run this script to initialize the database with optimized settings
"""

import os
from dotenv import load_dotenv
from sqlalchemy import text, Index
from database import engine, Base
import models

# Load environment variables
load_dotenv()

def create_indexes():
    """Create additional database indexes for better performance"""
    with engine.connect() as conn:
        try:
            # Composite indexes for better query performance
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_musteri_owner_category 
                ON musteri(owner_id, kategori);
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_musteri_owner_durum 
                ON musteri(owner_id, durum);
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_musteri_owner_sales_date 
                ON musteri(owner_id, ilkSatisYili, sonSatisYili);
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_musteri_search 
                ON musteri(firmaAdi, email, yetkili);
            """))
            
            conn.commit()
            print("✓ Additional indexes created successfully")
            
        except Exception as e:
            print(f"Note: Some indexes may already exist - {e}")

def setup_database():
    """Initialize database with tables and indexes"""
    try:
        print("Creating database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")
        
        # Create additional indexes
        print("Creating performance indexes...")
        create_indexes()
        
        # Verify tables exist
        print("Verifying database setup...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%';
            """))
            tables = [row[0] for row in result]
            
            if 'users' in tables and 'musteri' in tables:
                print("✓ Database setup completed successfully")
                print(f"✓ Created tables: {', '.join(tables)}")
            else:
                print("⚠ Warning: Not all expected tables were created")
                
    except Exception as e:
        print(f"✗ Error setting up database: {e}")
        raise

def optimize_sqlite_settings():
    """Apply SQLite-specific optimizations"""
    if engine.url.drivername == 'sqlite':
        with engine.connect() as conn:
            try:
                # Enable WAL mode for better concurrency
                conn.execute(text("PRAGMA journal_mode=WAL;"))
                
                # Optimize for better performance
                conn.execute(text("PRAGMA synchronous=NORMAL;"))
                conn.execute(text("PRAGMA cache_size=10000;"))
                conn.execute(text("PRAGMA temp_store=memory;"))
                
                conn.commit()
                print("✓ SQLite performance optimizations applied")
                
            except Exception as e:
                print(f"Note: SQLite optimization warning - {e}")

if __name__ == "__main__":
    print("🚀 Setting up Customer Management Database...")
    print(f"Database URL: {engine.url}")
    
    setup_database()
    optimize_sqlite_settings()
    
    print("\n✅ Database setup complete!")
    print("\nNext steps:")
    print("1. Copy .env.example to .env and configure your settings")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the application: python main.py")
    print("4. Visit http://localhost:8000/docs for API documentation")