from sorts.core.interfaces import IExplanationGenerator
from sorts.core.domain.entities import RecommendationEvidence

class ExplanationGenerator(IExplanationGenerator):
    def generate_explanation(self, evidence: RecommendationEvidence) -> str:
        """Generates a short, humorous, and crisp explanation with minimal cognitive load."""
        
        # Map trait slugs to funny templates containing {trait_name} placeholder
        trait_maps = {
            "software": "You like {trait_name}, and they live in IDEs.",
            "hardware": "You want to build gadgets with {trait_name}, and they live for hands-on robotics.",
            "aerospace": "You want to fly things using {trait_name}, and they build aircraft.",
            "entrepreneurship": "You want a startup in {trait_name}, and they live for pitch decks.",
            "public_speaking": "You like {trait_name}, and they love the spotlight.",
            "music": "You enjoy {trait_name}, and they jam all night.",
            "creative": "You have a spark of {trait_name}, and they make art.",
            "social": "You are highly social, and {trait_name} is their core vibe.",
            "commitment_high": "You chose {trait_name} (rip your free time).",
            "commitment_medium": "You want {trait_name} (balanced life).",
            "commitment_low": "You want {trait_name} (maximum chill)."
        }
        
        reasons = []
        for m in evidence.matches:
            # Only count significant positive contributions
            if m.contribution > 0.05:
                template = trait_maps.get(m.trait_slug)
                if template:
                    reasons.append(template.format(trait_name=m.trait_name.lower()))
                else:
                    reasons.append(f"Your interest in {m.trait_name.lower()} fits their focus.")

        if not reasons:
            return f"I ran the numbers and it just clicks for {evidence.club_name}. Trust me."
            
        # Keep it short, crisp, and humorous
        return " ".join(reasons[:2]) + f" {evidence.club_name} is a perfect fit: a match made in campus heaven."
