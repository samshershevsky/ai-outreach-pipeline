"""Stage 3 — Lead scoring.

Encodes the ICP fit rubric from prompts.py into a transparent 0-100 score.
Every point is explainable: score_lead() returns the score, the tier, and the
list of reasons so a human (or an approver agent) can audit it.
"""
from prompts import SCORING_RUBRIC  # noqa: F401  (kept visible: rubric lives with prompts)

_HIGH_FIT_INDUSTRIES = {"SaaS", "Fintech", "Healthcare", "Analytics", "Edtech"}

_TITLE_TIERS = [
    (("chief", "cfo", "cro", "ceo", "president", "founder", "owner"), 30),
    (("vp", "vice president"), 25),
    (("director", "head of"), 20),
    (("manager",), 10),
]


def _title_points(title: str) -> tuple[int, str]:
    t = title.lower()
    for keywords, pts in _TITLE_TIERS:
        if any(k in t for k in keywords):
            return pts, f"Title seniority '{title}': +{pts}"
    return 5, f"Title '{title}': +5 (individual contributor)"


def score_lead(lead: dict, enrichment: dict) -> dict:
    score = 0
    reasons = []

    pts, why = _title_points(lead["title"])
    score += pts
    reasons.append(why)

    emp = enrichment["employee_estimate"]
    if 50 <= emp <= 1000:
        score += 25
        reasons.append(f"Company size ~{emp} employees (sweet spot): +25")
    elif 1000 < emp <= 5000:
        score += 10
        reasons.append(f"Company size ~{emp} employees: +10")
    else:
        score += 5
        reasons.append(f"Company size ~{emp} employees (outside sweet spot): +5")

    if lead["industry"] in _HIGH_FIT_INDUSTRIES:
        score += 15
        reasons.append(f"Industry '{lead['industry']}' is high-fit: +15")
    else:
        score += 8
        reasons.append(f"Industry '{lead['industry']}': +8")

    for sig in enrichment["hiring_signals"][:3]:
        score += 7
        reasons.append(f"Buying signal — {sig}: +7")

    if enrichment["pain_detected"]:
        score += 10
        reasons.append("Pain signal in research (manual process): +10")

    score = min(score, 100)
    tier = "A" if score >= 75 else "B" if score >= 55 else "C"
    return {"score": score, "tier": tier, "reasons": reasons}
