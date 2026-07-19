from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sorts.database import models as db_models

class ClubService:
    def get_club_by_slug(self, db: Session, university_id: int, slug: str) -> Optional[db_models.Club]:
        """Retrieves a single club by its slug name."""
        return db.query(db_models.Club).filter_by(university_id=university_id, slug=slug.lower().strip()).first()

    def get_club_by_id(self, db: Session, club_id: int) -> Optional[db_models.Club]:
        """Retrieves a single club by its unique ID."""
        return db.query(db_models.Club).filter_by(id=club_id).first()

    def get_clubs_paginated(
        self, db: Session, university_id: int, page: int = 1, per_page: int = 5
    ) -> Tuple[List[db_models.Club], int]:
        """Retrieves a paginated list of clubs for a university, alongside total count."""
        query = db.query(db_models.Club).filter_by(university_id=university_id)
        total_count = query.count()

        offset = (page - 1) * per_page
        clubs = query.order_by(db_models.Club.name).offset(offset).limit(per_page).all()
        
        return clubs, total_count

    def search_clubs(self, db: Session, university_id: int, search_query: str) -> List[db_models.Club]:
        """Searches clubs based on name, summary, description, or keyword aliases."""
        query_str = search_query.lower().strip()
        search_filter = f"%{query_str}%"

        matches = db.query(db_models.Club)\
            .filter(db_models.Club.university_id == university_id)\
            .filter(
                or_(
                    db_models.Club.name.ilike(search_filter),
                    db_models.Club.summary.ilike(search_filter),
                    db_models.Club.description.ilike(search_filter)
                )
            ).order_by(db_models.Club.name).all()

        if matches:
            return matches

        # Fallback alias matching for specific keywords
        alias_map = {
            "quantum": "Qubit Club",
            "qubit": "Qubit Club",
            "qiskit": "Qubit Club",
            "quantum computing": "Qubit Club",
            "quantum club": "Qubit Club"
        }

        for kw, target_name in alias_map.items():
            if kw in query_str or query_str in kw:
                alias_match = db.query(db_models.Club).filter(
                    db_models.Club.university_id == university_id,
                    db_models.Club.name.ilike(f"%{target_name}%")
                ).all()
                if alias_match:
                    return alias_match

        return []
