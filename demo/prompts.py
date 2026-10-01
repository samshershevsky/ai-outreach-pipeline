"""Prompt templates used by the outreach pipeline.

These are the actual prompts the system is designed around. Out of the box the
demo drafts emails with a deterministic template engine so it runs with zero
dependencies. Set ANTHROPIC_API_KEY (and ANTHROPIC_MODEL) to have these exact
prompts executed live against the Claude API instead — see drafting.py.
"""

OUTREACH_SYSTEM_PROMPT = """You are a senior SDR writing first-touch cold emails for a B2B seller.
Rules:
- Plain, human language. No buzzwords (no "synergy", "leverage", "game-changer", "cutting-edge").
- Under 110 words total.
- Exactly one personalized observation about the prospect's company — never generic flattery.
- One clear, low-pressure question as the call to action. Never ask for "15 minutes" in email one.
- Never invent facts. Only use the signals provided. If a signal is weak, say less, not more.
- Output format: a subject line on the first line prefixed with "Subject: ", then a blank line, then the email body.
"""

OUTREACH_USER_PROMPT = """Write a first-touch cold email.

Prospect:
- Name: {first_name} {last_name}
- Title: {title}
- Company: {company} ({industry}, {city}, {state})
- Website: {website}

Observed signals (use at most two, the strongest ones):
{signals}

Conversation hook from research:
{hook}

Sender: {sender_name}
What the sender offers (one line, keep it modest): help revenue teams replace manual prospecting busywork with AI-assisted workflows.

Write the email now following the system rules exactly."""

# The scoring rubric the pipeline encodes. Kept here (not buried in code) so the
# business logic is reviewable in one place — same practice as a production system.
SCORING_RUBRIC = """
Lead score: 0-100. Tiers: A (>=75) = work now, B (55-74) = nurture, C (<55) = deprioritize.
- Title seniority: C-level/Chief +30, VP +25, Director/Head +20, Manager +10, other +5
- Company size fit: 50-1000 employees +25 (sweet spot), 1000-5000 +10, else +5
- Industry fit: SaaS/Fintech/Healthcare/Analytics +15, others +8
- Buying signals: +7 each for hiring revenue roles, tech migration, expansion, new leadership (cap +21)
- Pain signals: +10 if manual process / no CRM / spreadsheet tracking detected
"""
