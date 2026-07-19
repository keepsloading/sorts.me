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

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Calculates cosine similarity between two vectors."""
        epsilon = 1e-9
        
        # Calculate norm for vec1
        v1_sum_sq = sum(val ** 2 for val in vec1.values())
        v1_norm = math.sqrt(v1_sum_sq)
        
        # Calculate norm for vec2
        v2_sum_sq = sum(val ** 2 for val in vec2.values())
        v2_norm = math.sqrt(v2_sum_sq)
        
        if v1_norm <= 0.001 or v2_norm <= 0.001:
            return 0.0
            
        # Calculate dot product
        dot_product = sum(vec1.get(k, 0.0) * vec2.get(k, 0.0) for k in vec1.keys())
        return dot_product / (v1_norm * v2_norm + epsilon)

    def calculate_recommendations(
        self, session_traits: Dict[str, float], clubs: List[Club]
    ) -> List[RecommendationEvidence]:
        """Calculates match scores by separating interests (85%) and commitment (15%).
        
        This prevents workload commitment from dominates matching when interests do not align.
        """
        interest_slugs = {
            "software", "hardware", "public_speaking", "entrepreneurship",
            "aerospace", "music", "social", "creative"
        }
        commitment_slugs = {"commitment_high", "commitment_medium", "commitment_low"}

        # Extract student vectors
        s_interests = {slug: val for slug, val in session_traits.items() if slug in interest_slugs and abs(val) > 0.001}
        s_commitments = {slug: val for slug, val in session_traits.items() if slug in commitment_slugs and abs(val) > 0.001}

        results = []

        for club in clubs:
            # Extract club vectors
            c_interests = {}
            c_commitments = {}
            matches = []

            for ct in club.traits:
                if ct.trait_slug in interest_slugs:
                    c_interests[ct.trait_slug] = ct.weight
                elif ct.trait_slug in commitment_slugs:
                    c_commitments[ct.trait_slug] = ct.weight

                # Capture non-trivial matches for explanation evidence
                s_val = session_traits.get(ct.trait_slug, 0.0)
                contribution = s_val * ct.weight
                if abs(contribution) > 0.001:
                    trait_name = self.trait_names.get(ct.trait_slug, ct.trait_slug.replace("_", " ").title())
                    matches.append(
                        TraitMatchEvidence(
                            trait_slug=ct.trait_slug,
                            trait_name=trait_name,
                            student_weight=s_val,
                            club_weight=ct.weight,
                            contribution=contribution,
                        )
                    )

            # Calculate independent cosine similarities
            interest_score = self._cosine_similarity(s_interests, c_interests)
            commitment_score = self._cosine_similarity(s_commitments, c_commitments)

            # Combine scores
            if c_interests and interest_score <= 0.0:
                # If they have no matching interests (or negative alignment), heavily penalize the match
                overall_score = min(0.0, interest_score)
            else:
                # Weighted combination: 85% interests, 15% commitment
                overall_score = 0.85 * interest_score + 0.15 * commitment_score

            # Clamp score to [0.0, 1.0] range
            overall_score = max(0.0, min(1.0, overall_score))

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
