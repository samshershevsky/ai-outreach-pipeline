"""Stage 2 — Enrichment (SIMULATED).

In production this stage calls real enrichment providers (Apollo, Clearbit-style
APIs) and parses the company website. Here it is a deterministic mock: the same
lead_id always produces the same enrichment, so the demo is reproducible with
zero API keys. Every output is labeled simulated — the point of the demo is the
pipeline architecture and the downstream reasoning, not the data.
"""
import hashlib
import random

_TECH_STACKS = [
    ["HubSpot", "Salesforce"],
    ["HubSpot", "Outreach"],
    ["Salesforce", "Gong"],
    ["Pipedrive", "Mailchimp"],
    ["Zoho CRM", "ActiveCampaign"],
    ["Spreadsheets", "Gmail"],
    ["Salesforce", "Salesloft", "6sense"],
    ["HubSpot", "Apollo"],
]

_HIRING_SIGNALS = [
    "hiring account executives",
    "hiring SDRs",
    "hiring revenue operations",
    "hiring a sales manager",
    "no open revenue roles",
]

_FUNDING_STAGES = ["Bootstrapped", "Seed", "Series A", "Series B", "Series C", "Private equity", "Public"]

_INTENT_TOPICS = [
    "CRM migration",
    "Sales automation",
    "Lead scoring",
    "Outbound prospecting",
    "Data enrichment",
    "Forecasting",
]

_PAIN_PHRASES = ["manual", "spreadsheet", "no crm", "memory", "drying up", "stalling"]


def _rng(lead_id: str) -> random.Random:
    """Deterministic RNG seeded from the lead id — reproducible mock data."""
    seed = int(hashlib.sha256(lead_id.encode("utf-8")).hexdigest()[:8], 16)
    return random.Random(seed)


def enrich_lead(lead: dict) -> dict:
    """Return simulated enrichment for one lead. Never hits the network."""
    rng = _rng(lead["lead_id"])
    hook = lead.get("hook", "").lower()

    employees = rng.choice([12, 28, 45, 80, 140, 220, 350, 600, 1200, 4500])
    tech_stack = rng.choice(_TECH_STACKS)
    hiring = [s for s in rng.sample(_HIRING_SIGNALS, 2) if "no open" not in s]

    # Let the research hook influence signals so drafts feel grounded.
    if any(w in hook for w in ("hiring", "sdr", "ae")):
        hiring = ["hiring account executives", "hiring SDRs"]
    if "hubspot" in hook and "HubSpot" not in tech_stack:
        tech_stack = ["HubSpot"] + tech_stack[:1]

    pain_detected = any(p in hook for p in _PAIN_PHRASES)

    return {
        "simulated": True,  # honesty label — always present
        "employee_estimate": employees,
        "tech_stack": tech_stack,
        "hiring_signals": hiring,
        "funding_stage": rng.choice(_FUNDING_STAGES),
        "intent_topics": rng.sample(_INTENT_TOPICS, 2),
        "pain_detected": pain_detected,
        "website_status": "reachable (simulated)",
    }
