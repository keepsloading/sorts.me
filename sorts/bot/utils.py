import os
import nextcord
from typing import Tuple, Optional
from sqlalchemy.orm import Session

MASCOT_DIR = "Sortling Mascot"

# Standard Brand Color for sorts.me (#000543)
BRAND_COLOR = nextcord.Color(0x000543)

def clean_text(text: Optional[str]) -> str:
    """Sanitizes text to avoid em-dashes and removes hyphens used as separators.
    
    Converts space-padded hyphens or dashes (e.g. ' - ' or ' – ') into clean colons.
    """
    if not text:
        return ""
    # Standardise dashes to simple spaced hyphens first
    t = text.replace("—", " - ").replace("–", " - ")
    # Replace any spaced hyphens (used as separators) with clean colons
    t = t.replace(" - ", " : ")
    return t

def create_sortling_embed(
    title: str,
    description: str,
    color: nextcord.Color = BRAND_COLOR,
    is_error: bool = False
) -> Tuple[nextcord.Embed, Optional[nextcord.File]]:
    """Creates a standardized nextcord Embed showing the mascot in the thumbnail.
    
    Returns:
        A tuple of (Embed, File). The File must be sent alongside the Embed in interaction.send() 
        or interaction.followup.send() to display properly.
    """
    filename = "Sad_Error.png" if is_error else "Icon_Neutral.png"
    filepath = os.path.join(MASCOT_DIR, filename)

    embed = nextcord.Embed(
        title=clean_text(title), 
        description=clean_text(description), 
        color=color
    )
    
    file = None
    if os.path.exists(filepath):
        file = nextcord.File(filepath, filename=filename)
        embed.set_thumbnail(url=f"attachment://{filename}")
    
    return embed, file

def get_guild_university(db: Session, guild_id: Optional[int]):
    """Resolves the university associated with the Discord guild.
    
    Exempted guild IDs are hardcoded to Mahindra University.
    """
    exempted_guilds = {1475575129726517349, 1361752080297230376}
    
    from sorts.database import models as db_models
    
    if not guild_id or guild_id in exempted_guilds:
        # Default to Mahindra University (slug: "mahindra")
        return db.query(db_models.University).filter_by(slug="mahindra").first()
        
    return db.query(db_models.University).filter_by(guild_id=str(guild_id)).first()
