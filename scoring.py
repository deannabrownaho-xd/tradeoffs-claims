"""
Scoring Engine: Claims Prioritization Algorithm

Calculates a composite score for each claim based on four weighted factors.
All scores are dynamically normalized so the algorithm works with any data range.

SCORING FORMULA:
score = financial_component + acceptance_component + days_remaining_component - effort_component

COMPONENTS:
1. Financial Value (financial_value slider)
   Reward = normalized net_value × slider weight (0-1)
   Higher recovery potential = higher priority

2. Acceptance Likelihood (acceptance_likelihood slider)
   Reward = correction_confidence × slider weight × 0.8 (dampened)
   Higher AI confidence in the correction = higher priority

3. Days Remaining (days_remaining slider)
   Reward = normalized days_remaining × slider weight (0-1)
   More time before deadline = higher priority (right slider = prioritize time)

4. Manual Review Effort (manual_review_effort slider)
   Penalty = normalized effort_hours × (1 - slider weight)
   Left slider = avoid effort; Right slider = willing to do work

USAGE:
from scoring import rank_claims
weights = {"financial_value": 1.0, "confidence": 0.5, "effort": 0.5, "risk": 0.5}
ranked_claims = rank_claims(all_claims, weights)
"""


def normalise(value, min_val, max_val):
    if max_val == min_val:
        return 0.5
    return (value - min_val) / (max_val - min_val)


def rank_claims(claims, weights):
    """
    Scores and ranks claims based on four weighted factors.
    Returns all claims sorted best-to-worst by weighted score.
    Every claim gets a 'score' field added.

    Score formula:
    - financial_component: net_value normalized, weighted by financial_value slider
    - acceptance_component: correction_confidence, weighted by acceptance_likelihood slider
    - days_remaining_component: days_remaining normalized, weighted by days_remaining slider
    - effort_component: effort_hours normalized inverted, weighted by manual_review_effort slider

    score = financial + acceptance + days_remaining - effort

    Normalisation min/max values are derived from the dataset itself,
    so scoring works correctly regardless of data range changes.
    """

    w_financial  = weights.get("financial_value", 0)
    w_confidence = weights.get("confidence", 0)
    w_effort     = weights.get("effort", 0)
    w_risk       = weights.get("risk", 0)

    # Normalize ranges dynamically from dataset so scoring adapts to any data distribution
    net_values       = [c["net_value"] for c in claims]
    days_values      = [c.get("days_remaining", 150) for c in claims]  # days_remaining added May 2026
    effort_values    = [c["effort_hours"] for c in claims]

    net_min, net_max       = min(net_values), max(net_values)
    days_min, days_max     = min(days_values), max(days_values)
    effort_min, effort_max = min(effort_values), max(effort_values)

    scored = []
    for claim in claims:

        # REWARD: Financial value (net recovery per claim)
        # Higher net_value = better. Weighted by financial_value slider (0-1)
        fin_norm            = normalise(claim["net_value"], net_min, net_max)
        financial_component = fin_norm * w_financial

        # REWARD: Acceptance likelihood (AI-assessed correction confidence)
        # Dampened by 0.8 so no single factor can dominate scoring
        # Higher correction_confidence = more confident the correction is right
        # Weighted by acceptance_likelihood slider (0-1)
        acceptance_component = claim["correction_confidence"] * w_confidence * 0.8

        # REWARD: Days remaining (filing deadline urgency)
        # Claims with more days remaining score higher
        # Weighted by days_remaining slider (0-1). Left=ignore deadline, Right=prioritize time
        # Added May 2026 to track statute-of-limitations and filing deadline risk
        days_norm                = normalise(claim.get("days_remaining", 150), days_min, days_max)
        days_remaining_component = days_norm * w_effort

        # PENALTY: Manual review effort (hours required)
        # Higher effort = takes longer = penalty to score
        # Slider is inverted: Left=avoid effort, Right=willing to do effort work (low penalty)
        # Weighted by manual_review_effort slider via (1 - w_risk)
        eff_norm         = normalise(claim["effort_hours"], effort_min, effort_max)
        effort_component = eff_norm * (1 - w_risk)

        # Calculate composite score: sum rewards, subtract penalties
        # Higher score = higher priority in the ranked list
        score = (
            financial_component          # Add: value reward
            + acceptance_component       # Add: confidence reward
            + days_remaining_component   # Add: deadline reward
            - effort_component           # Subtract: effort penalty
        )

        scored_claim = dict(claim)
        scored_claim["score"] = round(score, 4)
        scored.append(scored_claim)

    scored.sort(key=lambda c: c["score"], reverse=True)
    return scored
