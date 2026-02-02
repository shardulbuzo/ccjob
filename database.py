"""
Database Module for Web3 Job Board
Handles all database operations for jobs, job boards, and scraper logs
"""

import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
import json


class Database:
    """Database manager for Web3 job board"""
    
    def __init__(self, db_path: str = "web3_jobs.db"):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        
        # Companies table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                website_url TEXT,
                logo_url TEXT,
                job_board_url TEXT UNIQUE NOT NULL,
                ats_type TEXT,
                description TEXT,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Jobs table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_hash TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                company_id INTEGER,
                company_name TEXT NOT NULL,
                location TEXT,
                salary TEXT,
                sector TEXT,
                description TEXT,
                full_description TEXT,
                requirements TEXT,
                skills TEXT,
                job_url TEXT NOT NULL,
                ats_type TEXT,
                posted_date TEXT,
                scraped_at TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        # Scrape logs table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS scrape_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_scraped INTEGER,
                new_jobs_added INTEGER,
                duplicates_skipped INTEGER,
                boards_processed INTEGER,
                status TEXT,
                error_message TEXT,
                timestamp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User saved jobs table (for future use)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                job_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs(id),
                UNIQUE(user_id, job_id)
            )
        """)
        
        # Superadmin table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS superadmins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better query performance
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_hash ON jobs(job_hash)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_sector ON jobs(sector)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_posted_date ON jobs(posted_date DESC)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_company_id ON jobs(company_id)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_company_name ON jobs(company_name)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_companies_active ON companies(active)
        """)
        
        self.conn.commit()
        
        # Initialize superadmin if not exists
        self._init_superadmin()
    
    def _init_superadmin(self):
        """Initialize superadmin account if it doesn't exist"""
        import hashlib
        
        email = "shardulbuzo@gmail.com"
        password = "birdisthewordA1$"
        
        # Check if superadmin exists
        existing = self.cursor.execute(
            "SELECT id FROM superadmins WHERE email = ?", 
            (email,)
        ).fetchone()
        
        if not existing:
            # Hash the password
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            self.cursor.execute("""
                INSERT INTO superadmins (email, password_hash)
                VALUES (?, ?)
            """, (email, password_hash))
            
            self.conn.commit()
            print(f"✅ Superadmin account created: {email}")
        
        self.conn.commit()
    
    def insert_job(self, job_data: Dict) -> Optional[int]:
        """
        Insert a new job into the database
        
        Args:
            job_data: Dictionary containing job information
            
        Returns:
            Job ID if successful, None otherwise
        """
        try:
            # Convert skills list to JSON string
            skills_json = json.dumps(job_data.get('skills', []))
            
            self.cursor.execute("""
                INSERT INTO jobs (
                    job_hash, title, company_id, company_name, location, salary,
                    sector, description, full_description, requirements, skills, job_url,
                    ats_type, posted_date, scraped_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_data['job_hash'],
                job_data['title'],
                job_data.get('company_id'),
                job_data['company_name'],
                job_data.get('location', 'Remote'),
                job_data.get('salary'),
                job_data.get('sector', 'other'),
                job_data.get('description', ''),
                job_data.get('full_description', ''),
                job_data.get('requirements', ''),
                skills_json,
                job_data['job_url'],
                job_data.get('ats_type', 'unknown'),
                job_data.get('posted_date', datetime.now().strftime('%Y-%m-%d')),
                job_data.get('scraped_at', datetime.now().isoformat())
            ))
            
            self.conn.commit()
            return self.cursor.lastrowid
            
        except sqlite3.IntegrityError:
            # Job already exists (duplicate job_hash)
            return None
        except Exception as e:
            print(f"Error inserting job: {e}")
            self.conn.rollback()
            return None
    
    def get_all_jobs(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get all jobs ordered by posted date (newest first) with company logos
        
        Args:
            limit: Maximum number of jobs to return
            offset: Number of jobs to skip
            
        Returns:
            List of job dictionaries
        """
        self.cursor.execute("""
            SELECT 
                j.*,
                c.logo_url,
                c.website_url
            FROM jobs j
            LEFT JOIN companies c ON j.company_id = c.id
            ORDER BY j.posted_date DESC, j.scraped_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        rows = self.cursor.fetchall()
        return [self._row_to_dict(row) for row in rows]
    
    def search_jobs(self, query: str, sector: str = None, limit: int = 100) -> List[Dict]:
        """
        Search jobs by keyword and/or sector
        
        Args:
            query: Search query string
            sector: Job sector filter
            limit: Maximum number of results
            
        Returns:
            List of matching job dictionaries
        """
        sql = """
            SELECT 
                j.*,
                c.logo_url,
                c.website_url
            FROM jobs j
            LEFT JOIN companies c ON j.company_id = c.id
            WHERE (j.title LIKE ? OR j.company_name LIKE ? OR j.description LIKE ?)
        """
        params = [f"%{query}%", f"%{query}%", f"%{query}%"]
        
        if sector and sector != 'all':
            sql += " AND j.sector = ?"
            params.append(sector)
        
        sql += " ORDER BY j.posted_date DESC, j.scraped_at DESC LIMIT ?"
        params.append(limit)
        
        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()
        return [self._row_to_dict(row) for row in rows]
    
    def get_jobs_by_sector(self, sector: str, limit: int = 100) -> List[Dict]:
        """Get jobs filtered by sector"""
        self.cursor.execute("""
            SELECT 
                j.*,
                c.logo_url,
                c.website_url
            FROM jobs j
            LEFT JOIN companies c ON j.company_id = c.id
            WHERE j.sector = ?
            ORDER BY j.posted_date DESC, j.scraped_at DESC
            LIMIT ?
        """, (sector, limit))
        
        rows = self.cursor.fetchall()
        return [self._row_to_dict(row) for row in rows]
    
    # ==================== COMPANY MANAGEMENT ====================
    
    def add_company(self, name: str, job_board_url: str, logo_url: str = '', 
                   website_url: str = '', ats_type: str = '', description: str = '') -> Optional[int]:
        """
        Add a new company to the database
        
        Args:
            name: Company name
            job_board_url: URL to company's job board
            logo_url: URL to company logo
            website_url: Company website URL
            ats_type: ATS platform type
            description: Company description
            
        Returns:
            Company ID if successful
        """
        try:
            self.cursor.execute("""
                INSERT INTO companies (name, job_board_url, logo_url, website_url, ats_type, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, job_board_url, logo_url, website_url, ats_type, description))
            
            self.conn.commit()
            return self.cursor.lastrowid
            
        except sqlite3.IntegrityError:
            print(f"Company already exists: {name}")
            return None
        except Exception as e:
            print(f"Error adding company: {e}")
            self.conn.rollback()
            return None
    
    def get_all_companies(self, active_only: bool = True) -> List[Dict]:
        """Get all companies"""
        sql = "SELECT * FROM companies"
        if active_only:
            sql += " WHERE active = 1"
        sql += " ORDER BY name"
        
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_company_by_id(self, company_id: int) -> Optional[Dict]:
        """Get company by ID"""
        self.cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_company_by_name(self, name: str) -> Optional[Dict]:
        """Get company by name"""
        self.cursor.execute("SELECT * FROM companies WHERE name = ?", (name,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_company(self, company_id: int, **kwargs) -> bool:
        """Update company information"""
        try:
            fields = []
            values = []
            
            for key, value in kwargs.items():
                if key in ['name', 'job_board_url', 'logo_url', 'website_url', 'ats_type', 'description', 'active']:
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if not fields:
                return False
            
            fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(company_id)
            
            sql = f"UPDATE companies SET {', '.join(fields)} WHERE id = ?"
            self.cursor.execute(sql, values)
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error updating company: {e}")
            self.conn.rollback()
            return False
    
    def delete_company(self, company_id: int) -> bool:
        """Delete a company (sets active = 0)"""
        try:
            self.cursor.execute("""
                UPDATE companies SET active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (company_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting company: {e}")
            return False
    
    def get_active_job_boards(self) -> List[Dict]:
        """Get all active companies for scraping"""
        return self.get_all_companies(active_only=True)
    
    def update_company_last_scraped(self, company_id: int):
        """Update the last scraped timestamp for a company"""
        self.cursor.execute("""
            UPDATE companies
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (company_id,))
        self.conn.commit()
    
    # ==================== SUPERADMIN AUTHENTICATION ====================
    
    def verify_superadmin(self, email: str, password: str) -> bool:
        """
        Verify superadmin credentials
        
        Args:
            email: Admin email
            password: Admin password
            
        Returns:
            True if credentials are valid
        """
        import hashlib
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        result = self.cursor.execute("""
            SELECT id FROM superadmins 
            WHERE email = ? AND password_hash = ?
        """, (email, password_hash)).fetchone()
        
        return result is not None
    
    def log_scrape_run(self, summary: Dict):
        """
        Log a scraping run
        
        Args:
            summary: Dictionary containing scrape statistics
        """
        try:
            self.cursor.execute("""
                INSERT INTO scrape_logs (
                    total_scraped, new_jobs_added, duplicates_skipped,
                    boards_processed, status, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                summary['total_scraped'],
                summary['new_jobs_added'],
                summary['duplicates_skipped'],
                summary['boards_processed'],
                'success',
                summary['timestamp']
            ))
            
            self.conn.commit()
            
        except Exception as e:
            print(f"Error logging scrape run: {e}")
            self.conn.rollback()
    
    def get_scrape_history(self, limit: int = 10) -> List[Dict]:
        """Get recent scrape logs"""
        self.cursor.execute("""
            SELECT * FROM scrape_logs
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def query(self, sql: str, params: tuple = ()) -> List[Dict]:
        """
        Execute a custom query
        
        Args:
            sql: SQL query string
            params: Query parameters
            
        Returns:
            List of result dictionaries
        """
        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """Convert a database row to a dictionary with parsed JSON fields"""
        job_dict = dict(row)
        
        # Parse skills JSON
        if 'skills' in job_dict and job_dict['skills']:
            try:
                job_dict['skills'] = json.loads(job_dict['skills'])
            except json.JSONDecodeError:
                job_dict['skills'] = []
        
        return job_dict
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Example usage and testing
if __name__ == "__main__":
    # Initialize database
    db = Database("test_web3_jobs.db")
    
    # Add sample job boards
    db.add_job_board(
        "https://jobs.lever.co/crypto",
        "Crypto.com",
        "https://example.com/crypto-logo.png",
        "lever"
    )
    
    db.add_job_board(
        "https://job-boards.greenhouse.io/fireblocks/",
        "Fireblocks",
        "https://example.com/fireblocks-logo.png",
        "greenhouse"
    )
    
    # Get active job boards
    boards = db.get_active_job_boards()
    print(f"\nActive job boards: {len(boards)}")
    for board in boards:
        print(f"  - {board['company']}: {board['url']}")
    
    # Sample job data
    sample_job = {
        'job_hash': 'abc123',
        'title': 'Senior Blockchain Engineer',
        'company': 'Crypto.com',
        'logo': 'https://example.com/logo.png',
        'location': 'Remote',
        'salary': '$150k - $220k',
        'sector': 'engineering',
        'description': 'Build scalable blockchain infrastructure',
        'requirements': '5+ years experience',
        'skills': ['Solidity', 'Rust', 'Blockchain'],
        'job_url': 'https://jobs.lever.co/crypto/job123',
        'ats_type': 'lever',
        'posted_date': '2026-01-30',
        'scraped_at': datetime.now().isoformat()
    }
    
    # Insert job
    job_id = db.insert_job(sample_job)
    print(f"\nInserted job with ID: {job_id}")
    
    # Get all jobs
    jobs = db.get_all_jobs(limit=10)
    print(f"\nTotal jobs in database: {len(jobs)}")
    
    # Close database
    db.close()
