import os
import json
import logging
from sqlalchemy.orm import Session
from sorts.database.models import (
    University, ImportSource, Trait, Question, QuestionOption, OptionTraitModifier
)

logger = logging.getLogger(__name__)

def seed_database(db: Session, seed_filepath: str) -> None:
    """Seeds the database with university, traits, questions, and import sources from a JSON file."""
    if not os.path.exists(seed_filepath):
        logger.error(f"Seed file not found: {seed_filepath}")
        return

    logger.info(f"Seeding database from: {seed_filepath}")
    with open(seed_filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Seed University
    univ_data = data["university"]
    db_univ = db.query(University).filter_by(slug=univ_data["slug"]).first()
    if not db_univ:
        db_univ = University(
            slug=univ_data["slug"],
            name=univ_data["name"],
            website=univ_data["website"],
            logo=univ_data.get("logo"),
            primary_color=univ_data.get("primary_color"),
            secondary_color=univ_data.get("secondary_color"),
            description=univ_data.get("description"),
        )
        db_univ.set_metadata(univ_data.get("metadata", {}))
        db.add(db_univ)
        db.commit()
        db.refresh(db_univ)
        logger.info(f"Seeded university: {db_univ.name} (ID: {db_univ.id})")
    else:
        logger.info(f"University '{univ_data['name']}' already exists. Skipping.")

    # 2. Seed Import Sources
    for src in data.get("import_sources", []):
        db_src = db.query(ImportSource).filter_by(university_id=db_univ.id, url=src["url"]).first()
        if not db_src:
            db_src = ImportSource(
                university_id=db_univ.id,
                name=src["name"],
                source_type=src["source_type"],
                url=src["url"],
            )
            db_src.set_parser_config(src.get("parser_config", {}))
            db.add(db_src)
            logger.info(f"Seeded import source: {db_src.name}")
    db.commit()

    # 3. Seed Traits
    slug_to_trait_id = {}
    for trait_data in data.get("traits", []):
        db_trait = db.query(Trait).filter_by(slug=trait_data["slug"]).first()
        if not db_trait:
            db_trait = Trait(
                slug=trait_data["slug"],
                name=trait_data["name"],
                description=trait_data["description"],
                category=trait_data["category"],
            )
            db.add(db_trait)
            db.commit()
            db.refresh(db_trait)
            logger.info(f"Seeded trait: {db_trait.slug}")
        else:
            logger.debug(f"Trait '{trait_data['slug']}' already exists. Skipping.")
        slug_to_trait_id[db_trait.slug] = db_trait.id

    # 4. Seed Questions & Options
    for q_data in data.get("questions", []):
        db_q = db.query(Question).filter_by(university_id=db_univ.id, code=q_data["code"]).first()
        if not db_q:
            db_q = Question(
                university_id=db_univ.id,
                text=q_data["text"],
                code=q_data["code"],
            )
            db.add(db_q)
            db.commit()
            db.refresh(db_q)
            logger.info(f"Seeded question: {db_q.code}")

            for opt_data in q_data.get("options", []):
                db_opt = QuestionOption(
                    question_id=db_q.id,
                    text=opt_data["text"],
                )
                db.add(db_opt)
                db.commit()
                db.refresh(db_opt)

                for trait_slug, weight in opt_data.get("trait_modifiers", {}).items():
                    trait_id = slug_to_trait_id.get(trait_slug)
                    if trait_id:
                        db_mod = OptionTraitModifier(
                            option_id=db_opt.id,
                            trait_id=trait_id,
                            weight=weight,
                        )
                        db.add(db_mod)
            db.commit()
            logger.info(f"Seeded options and modifiers for question: {db_q.code}")
        else:
            logger.debug(f"Question '{q_data['code']}' already exists. Skipping.")

    logger.info("Database seeding finished.")
