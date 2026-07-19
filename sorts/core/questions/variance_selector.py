import math
from typing import List, Dict, Optional
from sorts.core.interfaces import IQuestionSelector
from sorts.core.domain.entities import Question, Club

class VarianceQuestionSelector(IQuestionSelector):
    def __init__(self, top_k_cutoff: int = 10, temperature: float = 5.0):
        """
        Args:
            top_k_cutoff: Number of top clubs to consider.
            temperature: Softmax temperature parameter to adjust distribution sharpness.
        """
        self.top_k_cutoff = top_k_cutoff
        self.temperature = temperature

    def _calculate_cosine_scores(self, traits: Dict[str, float], clubs: List[Club]) -> List[float]:
        """Calculates cosine similarity scores for all clubs."""
        scores = []
        s_sum_sq = sum(val ** 2 for val in traits.values())
        s_norm = math.sqrt(s_sum_sq)
        
        for club in clubs:
            numerator = 0.0
            club_sum_sq = 0.0
            for ct in club.traits:
                club_sum_sq += ct.weight ** 2
                s_val = traits.get(ct.trait_slug, 0.0)
                numerator += s_val * ct.weight
            
            club_norm = math.sqrt(club_sum_sq)
            if s_norm > 0.001 and club_norm > 0.001:
                scores.append(numerator / (s_norm * club_norm + 1e-9))
            else:
                scores.append(0.0)
        return scores

    def _calculate_entropy(self, scores: List[float]) -> float:
        """Applies softmax to scores and calculates Shannon Entropy."""
        if not scores:
            return 0.0
            
        # Softmax to convert scores into a probability distribution
        # Subtract max for numerical stability
        max_score = max(scores)
        exp_scores = [math.exp(self.temperature * (s - max_score)) for s in scores]
        sum_exp = sum(exp_scores)
        
        probabilities = [e / (sum_exp + 1e-9) for e in exp_scores]
        
        # Shannon Entropy: -Sum(p * log2(p))
        entropy = 0.0
        for p in probabilities:
            if p > 1e-6:
                entropy -= p * math.log2(p)
        return entropy

    def select_next_question(
        self, unasked_questions: List[Question], current_session_traits: Dict[str, float], candidate_clubs: List[Club]
    ) -> Optional[Question]:
        """Selects the next question utilizing Shannon Entropy Information Gain.
        It chooses the question that minimizes expected conditional entropy of the candidate matches.
        """
        if not unasked_questions:
            return None
        if not candidate_clubs:
            return unasked_questions[0]

        best_question = None
        # We want to minimize expected conditional entropy, so we start with infinity
        best_expected_entropy = float("inf")

        for q in unasked_questions:
            expected_entropy = 0.0
            
            for opt in q.options:
                # Simulate student traits after choosing this option
                sim_traits = current_session_traits.copy()
                for mod in opt.trait_modifiers:
                    sim_traits[mod.trait_slug] = max(-1.0, min(1.0, sim_traits.get(mod.trait_slug, 0.0) + mod.weight))
                
                # Calculate simulated scores for all clubs
                sim_scores = self._calculate_cosine_scores(sim_traits, candidate_clubs)
                
                # Sort simulated scores to take the top K candidates
                sim_scores.sort(reverse=True)
                top_sim_scores = sim_scores[:self.top_k_cutoff]
                
                # Compute simulated entropy
                expected_entropy += self._calculate_entropy(top_sim_scores)
                
            # Average expected entropy across options
            avg_expected_entropy = expected_entropy / len(q.options) if q.options else 0.0
            
            # We select the question that results in the lowest expected conditional entropy (highest Info Gain)
            if avg_expected_entropy < best_expected_entropy:
                best_expected_entropy = avg_expected_entropy
                best_question = q

        return best_question if best_question else unasked_questions[0]
