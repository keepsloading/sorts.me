from sorts.core.interfaces import IExplanationGenerator
from sorts.core.domain.entities import RecommendationEvidence

COMMITMENT_MAP = {
    "commitment_high": "high commitment preference fits their intense schedule.",
    "commitment_medium": "medium commitment preference fits their weekly pace.",
    "commitment_low": "low commitment preference fits their flexible schedule.",
}

class ExplanationGenerator(IExplanationGenerator):
    def generate_explanation(self, evidence: RecommendationEvidence) -> str:
        """Generates a short, clear explanation dynamically based on positive trait matches."""
        reasons = []
        
        # Filter strictly for positive contributions
        positive_matches = [
            m for m in evidence.matches 
            if m.contribution > 0.001 and m.student_weight > 0
        ]
        positive_matches.sort(key=lambda m: m.contribution, reverse=True)
        
        for m in positive_matches[:2]:
            name_lower = m.trait_name.lower()
            if m.trait_slug in COMMITMENT_MAP:
                reasons.append(f"Your {COMMITMENT_MAP[m.trait_slug]}")
            elif "commitment" in m.trait_slug:
                reasons.append(f"You wanted {name_lower}, fitting their schedule.")
            else:
                reasons.append(f"Your interest in {name_lower} fits their focus.")
                
        if not reasons:
            if evidence.overall_score <= 0.001:
                return "Fits an open student profile: a great starting point to explore campus life."
            return "Fits your general profile across campus activity."
            
        return " ".join(reasons)
