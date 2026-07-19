import sys
import logging
from sorts.database.connection import init_db, get_db
from sorts.services.seed_service import seed_database
from sorts.database import models as db_models
from sorts.bot.bot import run_bot

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")

def bootstrap():
    """Initializes database schema and automatically seeds Mahindra University dataset if missing."""
    logger.info("Initializing database schema...")
    init_db()

    with get_db() as db:
        mahindra = db.query(db_models.University).filter_by(slug="mahindra").first()
        if not mahindra:
            logger.info("Mahindra University records not found. Running auto-seeding...")
            try:
                seed_database(db, "sorts/assets/data/mahindra_seed.json")
                logger.info("Auto-seeding completed.")
            except Exception as e:
                logger.error(f"Auto-seeding failed: {str(e)}")
        else:
            logger.info("Mahindra University records already present. Skipping auto-seeding.")

def main():
    bootstrap()
    logger.info("Starting Sortling Discord Bot...")
    run_bot()

if __name__ == "__main__":
    main()
