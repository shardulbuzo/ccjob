#!/usr/bin/env python3
"""
Daily Scheduler for Web3 Job Board Scraper
Run this script daily via cron to automatically scrape job boards

Setup cron job (runs daily at 3 AM):
0 3 * * * /usr/bin/python3 /path/to/daily_scraper.py >> /path/to/logs/scraper.log 2>&1

Or use the included systemd service/timer for more robust scheduling
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database import Database
from scraper_orchestrator import JobBoardOrchestrator


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def run_daily_scrape():
    """Execute the daily scraping routine"""
    logger.info("=" * 60)
    logger.info("Starting Daily Web3 Job Board Scrape")
    logger.info("=" * 60)
    
    try:
        # Initialize database
        db = Database("web3_jobs.db")
        logger.info("Database connection established")
        
        # Get active companies
        companies = db.get_all_companies(active_only=True)
        logger.info(f"Found {len(companies)} active companies to scrape")
        
        if not companies:
            logger.warning("No active companies found! Please add companies to the database.")
            return
        
        # Create orchestrator
        orchestrator = JobBoardOrchestrator(db)
        
        # Run the scrape
        summary = orchestrator.scrape_all_boards(companies)
        
        # Log results
        logger.info("Scraping completed successfully")
        logger.info(f"Summary:")
        logger.info(f"  - Total jobs scraped: {summary['total_scraped']}")
        logger.info(f"  - New jobs added: {summary['new_jobs_added']}")
        logger.info(f"  - Duplicates skipped: {summary['duplicates_skipped']}")
        logger.info(f"  - Companies processed: {summary['boards_processed']}")
        
        db.close()
        logger.info("Daily scrape completed successfully!")
        
        return summary
        
    except Exception as e:
        logger.error(f"Error during daily scrape: {str(e)}", exc_info=True)
        
        # Log the failed run
        try:
            db = Database("web3_jobs.db")
            db.cursor.execute("""
                INSERT INTO scrape_logs (
                    total_scraped, new_jobs_added, duplicates_skipped,
                    boards_processed, status, error_message, timestamp
                ) VALUES (0, 0, 0, 0, 'failed', ?, ?)
            """, (str(e), datetime.now().isoformat()))
            db.conn.commit()
            db.close()
        except Exception as db_error:
            logger.error(f"Could not log failed run to database: {db_error}")
        
        sys.exit(1)


def setup_sample_boards():
    """
    Setup sample companies for testing
    Run this once to initialize the database with some companies
    """
    logger.info("Setting up sample companies...")
    
    db = Database("web3_jobs.db")
    
    sample_companies = [
        {
            'name': 'Crypto.com',
            'job_board_url': 'https://jobs.lever.co/crypto',
            'website_url': 'https://crypto.com',
            'logo_url': 'https://images.unsplash.com/photo-1621416894569-0f39ed31d247?w=100',
            'ats_type': 'lever',
            'description': 'Leading cryptocurrency platform'
        },
        {
            'name': 'Fireblocks',
            'job_board_url': 'https://job-boards.greenhouse.io/fireblocks/',
            'website_url': 'https://fireblocks.com',
            'logo_url': 'https://images.unsplash.com/photo-1621504450181-5d356f61d307?w=100',
            'ats_type': 'greenhouse',
            'description': 'Digital asset custody and transfer platform'
        },
        {
            'name': 'Chainalysis',
            'job_board_url': 'https://jobs.ashbyhq.com/chainalysis-careers',
            'website_url': 'https://chainalysis.com',
            'logo_url': 'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=100',
            'ats_type': 'ashby',
            'description': 'Blockchain data platform'
        },
        {
            'name': 'Zero Hash',
            'job_board_url': 'https://zero-hash.breezy.hr/',
            'website_url': 'https://zerohash.com',
            'logo_url': 'https://images.unsplash.com/photo-1605792657660-596af9009e82?w=100',
            'ats_type': 'breezy',
            'description': 'B2B crypto infrastructure'
        },
        {
            'name': 'IO Global',
            'job_board_url': 'https://apply.workable.com/io-global/?lng=en',
            'website_url': 'https://iohk.io',
            'logo_url': 'https://images.unsplash.com/photo-1621504450181-5d356f61d307?w=100',
            'ats_type': 'workable',
            'description': 'Cardano blockchain development'
        }
    ]
    
    for company in sample_companies:
        company_id = db.add_company(
            company['name'],
            company['job_board_url'],
            company['logo_url'],
            company['website_url'],
            company['ats_type'],
            company['description']
        )
        if company_id:
            logger.info(f"Added company: {company['name']}")
        else:
            logger.info(f"Company already exists: {company['name']}")
    
    db.close()
    logger.info("Sample companies setup complete!")


if __name__ == "__main__":
    # Check if we should setup sample boards
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        setup_sample_boards()
    else:
        # Run the daily scrape
        run_daily_scrape()
