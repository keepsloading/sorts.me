import sys
import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
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


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass  # Silence access logs


def start_health_server():
    """Starts a minimal HTTP server on PORT so Render's health check passes."""
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), _HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info(f"Health server running on port {port}")

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
    start_health_server()
    logger.info("Starting Sortling Discord Bot...")
    run_bot()

if __name__ == "__main__":
    main()
