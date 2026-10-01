"""Stage 4 — Outreach drafting.

Two modes:
1. Template engine (default): deterministic, zero-dependency drafting that
   personalizes from the lead's signals. Runs out of the box.
2. Live Claude (optional): if ANTHROPIC_API_KEY and ANTHROPIC_MODEL are set in
   the environment, the exact prompts from prompts.py are executed against the
   Claude API (stdlib only — urllib, no extra packages).

Every draft is labeled with which engine produced it.
"""
import json
import os
import urllib.request

from prompts import OUTREACH_SYSTEM_PROMPT, OUTREACH_USER_PROMPT

SENDER_NAME = os.environ.get("SENDER_NAME", "Sam Shershevsky")


def _signals_block(lead: dict, enrichment: dict) -> str:
    lines = [
        f"- Research hook: {lead['hook']}",
        f"- Estimated headcount: ~{enrichment['employee_estimate']} ({enrichment['funding_stage']})",
        f"- Tech stack: {', '.join(enrichment['tech_stack'])}",
    ]
    for sig in enrichment["hiring_signals"]:
        lines.append(f"- Hiring signal: {sig}")
    lines.append(f"- Intent topics: {', '.join(enrichment['intent_topics'])}")
    return "\n".join(lines)


def _template_draft(lead: dict, enrichment: dict, score: dict) -> dict:
    """Deterministic personalization: opener from the strongest signal."""
    first, company = lead["first_name"], lead["company"]

    # Clean the research hook so it reads naturally mid-sentence.
    raw_hook = lead["hook"].strip()
    hook = raw_hook.replace(" - ", ", ").replace(" — ", ", ")
    if hook[:1].isupper():
        hook = hook[:1].lower() + hook[1:]

    hiring = enrichment["hiring_signals"][0] if enrichment["hiring_signals"] else None

    if enrichment["pain_detected"]:
        opener = (
            f"Did a little digging on {company} — {hook}. "
            "Manual processes like that are usually the first thing to break "
            "when a team starts to scale."
        )
    elif "migrat" in lead["hook"].lower():
        opener = (
            f"Saw {company} is {hook} — migrations are exactly when teams "
            "rethink the manual workarounds they've been tolerating."
        )
    elif hiring and "hiring" not in lead["hook"].lower():
        opener = (
            f"Saw that {company} is {hiring} — usually a sign the team is "
            "about to feel the pain of manual prospecting."
        )
    else:
        opener = f"Been following {company} — {hook}."

    title = lead["title"].lower()
    if any(k in title for k in ("chief", "vp", "president", "founder", "owner", "director", "head")):
        value = (
            "I help revenue leaders replace the manual prospecting busywork "
            "with AI-assisted workflows — most teams get about half that time back."
        )
    else:
        value = (
            "I help revenue teams replace manual prospecting busywork with "
            "AI-assisted workflows — most teams get about half that time back."
        )

    subject = f"{first} — {raw_hook.split('—')[0].strip()[:48]}"
    body = (
        f"Hi {first},\n\n{opener}\n\n{value}\n\n"
        f"Worth a quick look at what that could look like for {company}?\n\n"
        f"Best,\n{SENDER_NAME}"
    )
    return {
        "to": f"{first.lower()}.{lead['last_name'].lower()}@{lead['website']} (synthetic)",
        "subject": subject,
        "body": body,
        "drafted_by": "template-engine (deterministic, no API)",
        "signals_used": _signals_block(lead, enrichment),
    }


def _claude_draft(lead: dict, enrichment: dict) -> dict:
    """Execute the real prompts against the Claude API. Stdlib only."""
    api_key = os.environ["ANTHROPIC_API_KEY"]
    model = os.environ["ANTHROPIC_MODEL"]
    payload = {
        "model": model,
        "max_tokens": 400,
        "system": OUTREACH_SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": OUTREACH_USER_PROMPT.format(
                    first_name=lead["first_name"],
                    last_name=lead["last_name"],
                    title=lead["title"],
                    company=lead["company"],
                    industry=lead["industry"],
                    city=lead["city"],
                    state=lead["state"],
                    website=lead["website"],
                    signals=_signals_block(lead, enrichment),
                    hook=lead["hook"],
                    sender_name=SENDER_NAME,
                ),
            }
        ],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        text = json.loads(resp.read())["content"][0]["text"]
    subject, _, body = text.partition("\n\n")
    return {
        "to": f"{lead['first_name'].lower()}.{lead['last_name'].lower()}@{lead['website']} (synthetic)",
        "subject": subject.replace("Subject:", "").strip(),
        "body": body.strip(),
        "drafted_by": f"claude-api ({model})",
        "signals_used": _signals_block(lead, enrichment),
    }


def draft_email(lead: dict, enrichment: dict, score: dict) -> dict:
    if os.environ.get("ANTHROPIC_API_KEY") and os.environ.get("ANTHROPIC_MODEL"):
        try:
            return _claude_draft(lead, enrichment)
        except Exception as exc:  # fall back cleanly; never crash the pipeline
            print(f"    ! Claude API failed ({exc}); using template engine.")
    return _template_draft(lead, enrichment, score)
