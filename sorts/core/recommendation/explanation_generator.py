from sorts.core.interfaces import IExplanationGenerator
from sorts.core.domain.entities import RecommendationEvidence

class ExplanationGenerator(IExplanationGenerator):
    def generate_explanation(self, evidence: RecommendationEvidence) -> str:
        """Generates a short, humorous, and crisp explanation dynamically without hardcoding."""
        reasons = []
        
        # Sort matches by absolute contribution to prioritize the strongest matches
        sorted_matches = sorted(evidence.matches, key=lambda m: abs(m.contribution), reverse=True)
        
        for m in sorted_matches[:2]:
            name_lower = m.trait_name.lower()
            if "commitment" in m.trait_slug:
                reasons.append(f"You wanted {name_lower}, fitting their schedule.")
            else:
                reasons.append(f"Your interest in {name_lower} fits their focus.")
                
        if not reasons:
            return "I ran the numbers and it just fits. Trust me."
            
        return " ".join(reasons)
