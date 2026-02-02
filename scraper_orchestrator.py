"""
Web3 Job Board Scraper - Main Orchestrator
Automatically detects ATS type and runs specialized scrapers
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional
import hashlib

# Import specialized scrapers
from scrapers.lever_scraper import LeverScraper
from scrapers.greenhouse_scraper import GreenhouseScraper
from scrapers.ashby_scraper import AshbyScraper
from scrapers.breezy_scraper import BreezyScraper
from scrapers.workable_scraper import WorkableScraper


class JobBoardOrchestrator:
    """Main orchestrator for managing all job board scrapers"""
    
    ATS_PATTERNS = {
        'lever': r'jobs\.lever\.co',
        'greenhouse': r'greenhouse\.io',
        'ashby': r'ashbyhq\.com',
        'breezy': r'breezy\.hr',
        'workable': r'workable\.com'
    }
    
    SCRAPER_MAP = {
        'lever': LeverScraper,
        'greenhouse': GreenhouseScraper,
        'ashby': AshbyScraper,
        'breezy': BreezyScraper,
        'workable': WorkableScraper
    }
    
    def __init__(self, db_connection):
        """
        Initialize the orchestrator
        
        Args:
            db_connection: Database connection object
        """
        self.db = db_connection
        self.scraped_jobs = []
        self.duplicate_count = 0
        self.new_jobs_count = 0
        
    def detect_ats_type(self, url: str) -> Optional[str]:
        """
        Detect the ATS type from URL
        
        Args:
            url: Job board URL
            
        Returns:
            ATS type string or None if not recognized
        """
        for ats_type, pattern in self.ATS_PATTERNS.items():
            if re.search(pattern, url, re.IGNORECASE):
                return ats_type
        return None
    
    def generate_job_hash(self, job_url: str) -> str:
        """
        Generate unique hash for job URL to detect duplicates
        
        Args:
            job_url: Job posting URL
            
        Returns:
            Hash string
        """
        return hashlib.md5(job_url.encode()).hexdigest()
    
    def is_duplicate(self, job_url: str) -> bool:
        """
        Check if job already exists in database
        
        Args:
            job_url: Job posting URL
            
        Returns:
            True if duplicate, False otherwise
        """
        job_hash = self.generate_job_hash(job_url)
        existing = self.db.query("SELECT id FROM jobs WHERE job_hash = ?", (job_hash,))
        return len(existing) > 0
    
    def extract_compensation(self, description: str, title: str) -> Optional[str]:
        """
        Extract compensation information from job description
        
        Args:
            description: Job description text
            title: Job title
            
        Returns:
            Compensation string or None
        """
        # Common compensation patterns
        patterns = [
            r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:-|to)\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:k|K)?',
            r'\$\s*(\d{1,3})\s*[kK]\s*(?:-|to)\s*\$?\s*(\d{1,3})\s*[kK]',
            r'(\d{1,3})\s*[kK]\s*(?:-|to)\s*(\d{1,3})\s*[kK]',
            r'\$\s*(\d{1,3}(?:,\d{3})*)\s*(?:-|to)\s*\$?\s*(\d{1,3}(?:,\d{3})*)',
        ]
        
        text = f"{title} {description}"
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                low = match.group(1).replace(',', '')
                high = match.group(2).replace(',', '')
                
                # Convert to k format if needed
                if len(low) > 3:
                    low = f"{int(low)//1000}k"
                    high = f"{int(high)//1000}k"
                else:
                    low = f"{low}k"
                    high = f"{high}k"
                    
                return f"${low} - ${high}"
        
        return None
    
    def scrape_job_board(self, company_config: Dict) -> List[Dict]:
        """
        Scrape a single job board
        
        Args:
            company_config: Dictionary containing company info (from companies table)
            
        Returns:
            List of scraped job dictionaries
        """
        url = company_config['job_board_url']
        company_name = company_config['name']
        company_id = company_config['id']
        
        # Detect ATS type
        ats_type = company_config.get('ats_type') or self.detect_ats_type(url)
        
        if not ats_type:
            print(f"⚠️  Unknown ATS type for {url}")
            return []
        
        print(f"🔍 Scraping {company_name} ({ats_type.upper()} ATS)")
        
        # Get appropriate scraper
        scraper_class = self.SCRAPER_MAP.get(ats_type)
        if not scraper_class:
            print(f"❌ No scraper available for {ats_type}")
            return []
        
        # Initialize and run scraper (without logo parameter)
        scraper = scraper_class(url, company_name, '')
        jobs = scraper.scrape()
        
        print(f"✅ Scraped {len(jobs)} jobs from {company_name}")
        
        # Process each job
        processed_jobs = []
        for job in jobs:
            # Check for duplicates
            if self.is_duplicate(job['job_url']):
                self.duplicate_count += 1
                continue
            
            # Set company_id
            job['company_id'] = company_id
            
            # Extract compensation if not already present
            if not job.get('salary'):
                compensation = self.extract_compensation(
                    job.get('full_description', job.get('description', '')),
                    job.get('title', '')
                )
                if compensation:
                    job['salary'] = compensation
            
            # Add metadata
            job['job_hash'] = self.generate_job_hash(job['job_url'])
            job['scraped_at'] = datetime.now().isoformat()
            job['ats_type'] = ats_type
            
            processed_jobs.append(job)
            self.new_jobs_count += 1
        
        return processed_jobs
    
    def scrape_all_boards(self, companies: List[Dict]) -> Dict:
        """
        Scrape all configured job boards
        
        Args:
            companies: List of company configurations from companies table
            
        Returns:
            Summary dictionary with statistics
        """
        print(f"\n🚀 Starting scrape of {len(companies)} companies...\n")
        
        all_jobs = []
        
        for company in companies:
            try:
                jobs = self.scrape_job_board(company)
                all_jobs.extend(jobs)
                
                # Update company last scraped
                self.db.update_company_last_scraped(company['id'])
                
            except Exception as e:
                print(f"❌ Error scraping {company['name']}: {str(e)}")
                continue
        
        # Save to database (newest first)
        all_jobs.sort(key=lambda x: x['scraped_at'], reverse=True)
        
        for job in all_jobs:
            self.db.insert_job(job)
        
        summary = {
            'total_scraped': len(all_jobs),
            'duplicates_skipped': self.duplicate_count,
            'new_jobs_added': self.new_jobs_count,
            'boards_processed': len(companies),
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\n✨ Scraping Complete!")
        print(f"   📊 Total jobs scraped: {summary['total_scraped']}")
        print(f"   🆕 New jobs added: {summary['new_jobs_added']}")
        print(f"   ⏭️  Duplicates skipped: {summary['duplicates_skipped']}")
        print(f"   📋 Companies processed: {summary['boards_processed']}\n")
        
        return summary
    
    def run_daily_scrape(self):
        """Run the daily scheduled scrape"""
        # Get all active companies from database
        companies = self.db.get_all_companies(active_only=True)
        
        # Run scraper
        summary = self.scrape_all_boards(companies)
        
        # Log summary
        self.db.log_scrape_run(summary)
        
        return summary


# Example usage
if __name__ == "__main__":
    from database import Database
    
    # Initialize database
    db = Database("web3_jobs.db")
    
    # Example job boards configuration
    job_boards = [
        {
            'url': 'https://jobs.lever.co/crypto',
            'company': 'Crypto.com',
            'logo': 'https://example.com/crypto-logo.png'
        },
        {
            'url': 'https://job-boards.greenhouse.io/fireblocks/',
            'company': 'Fireblocks',
            'logo': 'https://example.com/fireblocks-logo.png'
        },
        {
            'url': 'https://jobs.ashbyhq.com/chainalysis-careers',
            'company': 'Chainalysis',
            'logo': 'https://example.com/chainalysis-logo.png'
        },
        {
            'url': 'https://zero-hash.breezy.hr/',
            'company': 'Zero Hash',
            'logo': 'https://example.com/zerohash-logo.png'
        },
        {
            'url': 'https://apply.workable.com/io-global/?lng=en',
            'company': 'IO Global',
            'logo': 'https://example.com/io-logo.png'
        }
    ]
    
    # Create orchestrator
    orchestrator = JobBoardOrchestrator(db)
    
    # Run scrape
    results = orchestrator.scrape_all_boards(job_boards)
    
    print(json.dumps(results, indent=2))
