import pytest
from sorts.database.connection import get_db, init_db
from sorts.database import models as db_models
from sorts.services.seed_service import sync_verified_events, seed_database


def test_event_seeding_and_querying():
    init_db()
    with get_db() as db:
        seed_database(db, "sorts/assets/data/mahindra_seed.json")
        sync_verified_events(db)

        univ = db.query(db_models.University).filter_by(slug="mahindra").first()
        assert univ is not None

        sih_event = db.query(db_models.Event).filter_by(university_id=univ.id, slug="smart-india-hackathon-2026").first()
        assert sih_event is not None
        assert sih_event.name == "Smart India Hackathon 2026 (Internal Hackathon)"
        assert sih_event.category == "Hackathon"
        assert sih_event.registration_link == "https://qrco.de/bgvXHe"
        assert sih_event.email_required is True
        assert "₹60,000" in sih_event.prizes
        assert "10 August 2026" in sih_event.registration_deadline
