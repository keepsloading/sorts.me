from sorts.core.interfaces import IExplanationGenerator
from sorts.core.domain.entities import RecommendationEvidence


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
            trait_name = m.trait_name
            acronyms = {"AI", "UN", "BAJA", "DSA", "IOT", "MUN", "SAE", "EIC", "TEDX"}
            words = trait_name.split()
            cased_words = [w if w.upper() in acronyms else w.lower() for w in words]
            name_formatted = " ".join(cased_words)

            if m.trait_slug == "commitment_high":
                reasons.append("Your high commitment preference fits their intensive schedule.")
            elif m.trait_slug == "commitment_medium":
                reasons.append("Your medium commitment preference fits their weekly pace.")
            elif m.trait_slug == "commitment_low":
                reasons.append("Your low commitment preference fits their flexible schedule.")
            elif "commitment" in m.trait_slug:
                reasons.append("Fits your availability and schedule.")
            else:
                reasons.append(f"Your interest in {name_formatted} fits their focus.")

        if not reasons:
            if evidence.overall_score <= 0.001:
                return "Fits an open student profile: a great starting point to explore campus life."
            return "Fits your general profile across campus activity."

        return " ".join(reasons)
