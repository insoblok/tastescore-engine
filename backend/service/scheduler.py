"""Scheduled jobs for sanctions ingestion, metrics calculation, and protocol sync."""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from service.sanctions.ofac_ingester import OFACIngester
from service.protocols.protocol_sync import ProtocolSyncJob
from service.utils import logger
import atexit


class Scheduler:
    """Manages scheduled jobs for the application."""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.ofac_ingester = OFACIngester()
        self.protocol_sync = ProtocolSyncJob()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """Set up scheduled jobs."""
        # OFAC sanctions ingestion - run nightly at 2 AM UTC
        self.scheduler.add_job(
            func=self._run_ofac_ingestion,
            trigger=CronTrigger(hour=2, minute=0),
            id='ofac_nightly_ingestion',
            name='OFAC Nightly Sanctions Ingestion',
            replace_existing=True
        )
        
        # Protocol sync - run nightly at 3 AM UTC (after OFAC)
        self.scheduler.add_job(
            func=self._run_protocol_sync,
            trigger=CronTrigger(hour=3, minute=0),
            id='protocol_nightly_sync',
            name='Protocol Nightly Sync',
            replace_existing=True
        )
        
        logger.info("Scheduled jobs configured")
    
    def _run_ofac_ingestion(self):
        """Run OFAC sanctions ingestion job."""
        try:
            logger.info("Starting scheduled OFAC ingestion")
            success = self.ofac_ingester.ingest()
            if success:
                logger.info("Scheduled OFAC ingestion completed successfully")
            else:
                logger.warning("Scheduled OFAC ingestion completed with warnings")
        except Exception as e:
            logger.error(f"Scheduled OFAC ingestion failed: {e}")
    
    def _run_protocol_sync(self):
        """Run protocol sync job."""
        try:
            logger.info("Starting scheduled protocol sync")
            success = self.protocol_sync.sync_all_protocols()
            if success:
                logger.info("Scheduled protocol sync completed successfully")
            else:
                logger.warning("Scheduled protocol sync completed with warnings")
        except Exception as e:
            logger.error(f"Scheduled protocol sync failed: {e}")
    
    def start(self):
        """Start the scheduler."""
        self.scheduler.start()
        logger.info("Scheduler started")
        
        # Register shutdown handler
        atexit.register(lambda: self.scheduler.shutdown())
    
    def shutdown(self):
        """Shutdown the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler shut down")


# Global scheduler instance
scheduler = Scheduler()

