from typing import List, Dict
import math
from sorts.core.interfaces import IRecommendationEngine
from sorts.core.domain.entities import Club, RecommendationEvidence, TraitMatchEvidence

class DeterministicRecommendationEngine(IRecommendationEngine):
    def __init__(self, trait_names: Dict[str, str] = None):
        """
        Args:
            trait_names: Optional dictionary mapping trait slugs to human-readable names.
        """
        self.trait_names = trait_names or {}

    def calculate_recommendations(
        self, session_traits: Dict[str, float], clubs: List[Club]
    ) -> List[RecommendationEvidence]:
        """Calculates match scores using Cosine Similarity.
        
        Formula:
            CosineSimilarity = Sum(S[t] * C[t]) / (Sqrt(Sum(S[t]^2)) * Sqrt(Sum(C[t]^2)) + epsilon)
            This guarantees a value in the range [-1.0, 1.0].
        """
        results = []
        epsilon = 1e-9

        # Filter out 0.0 values to ensure clean norm calculation
        cleaned_session_traits = {slug: val for slug, val in session_traits.items() if abs(val) > 0.001}
        s_sum_sq = sum(val ** 2 for val in cleaned_session_traits.values())
        s_norm = math.sqrt(s_sum_sq)

        for club in clubs:
            numerator = 0.0
            club_sum_sq = 0.0
            matches = []

            # Process traits
            for ct in club.traits:
                c_weight = ct.weight
                club_sum_sq += c_weight ** 2

                s_value = cleaned_session_traits.get(ct.trait_slug, 0.0)
                contribution = s_value * c_weight
                numerator += contribution

                # Capture non-trivial contributions as evidence
                if abs(contribution) > 0.001:
                    trait_name = self.trait_names.get(ct.trait_slug, ct.trait_slug.replace("_", " ").title())
                    matches.append(
                        TraitMatchEvidence(
                            trait_slug=ct.trait_slug,
                            trait_name=trait_name,
                            student_weight=s_value,
                            club_weight=c_weight,
                            contribution=contribution,
                        )
                    )

            club_norm = math.sqrt(club_sum_sq)
            
            # Compute cosine similarity
            if s_norm > 0.001 and club_norm > 0.001:
                overall_score = numerator / (s_norm * club_norm + epsilon)
            else:
                overall_score = 0.0

            # Clamp cosine similarity score strictly within [-1.0, 1.0] to prevent any floating point overflow
            overall_score = max(-1.0, min(1.0, overall_score))

            # Sort matches by absolute contribution
            matches.sort(key=lambda m: abs(m.contribution), reverse=True)

            results.append(
                RecommendationEvidence(
                    club_id=club.id if club.id else 0,
                    club_name=club.name,
                    overall_score=overall_score,
                    matches=matches,
                )
            )

        # Sort recommendations by overall score descending
        results.sort(key=lambda r: r.overall_score, reverse=True)
        return results
