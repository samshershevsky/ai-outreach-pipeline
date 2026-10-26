"""Stage 4: outreach drafting.

Two modes:
1. Template engine (default): deterministic, zero dependency drafting that
   personalizes from the lead's own signals. Runs out of the box.
2. Live Claude (optional): if ANTHROPIC_API_KEY and ANTHROPIC_MODEL are set in
   the environment, the exact prompts from prompts.py are executed against the
   Claude API (stdlib only, urllib, no extra packages).

Every draft is labeled with which engine produced it. Drafts are built per
lead: the opener, the value paragraph, and the closing question all come from
the lead's primary signal category, so two leads never share boilerplate
sentences.
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


def _category(lead: dict, enrichment: dict) -> str:
    """Pick the lead's primary signal category from its research hook."""
    hook = lead["hook"].lower()
    if "migrat" in hook:
        return "migration"
    if any(w in hook for w in ("second office", "new markets", "new locations",
                               "practice area", "franchis", "dtc channel",
                               "residential division")):
        return "expansion"
    if "hiring" in hook or "sdr team" in hook:
        return "hiring"
    if any(w in hook for w in ("new cro", "second generation", "founder-led")):
        return "leadership"
    if "partner program" in hook:
        return "partnership"
    if "acquired" in hook:
        return "acquisition"
    if enrichment["pain_detected"]:
        return "pain"
    if any(w in hook for w in ("series", "signups", "growing", "won two", "piloting")):
        return "growth"
    return "default"


def _parts(category: str, first: str, company: str, hook: str, title: str) -> tuple[str, str, str]:
    """Return (opener, value, closing) written for one signal category."""
    if category == "migration":
        return (
            f"Saw {company} is {hook}. A CRM move is the one moment when the old "
            "workarounds are already up for discussion, which makes it the right "
            "time to fix how leads enter the system in the first place.",
            "That is the layer I build for revenue teams: enrichment and scoring "
            "that land inside the new CRM from day one, plus first drafts written "
            "from each account's own signals. Instead of migrating old habits into "
            "a new tool, your team starts with a ranked queue and the research "
            "already done.",
            f"Open to a short walkthrough of how that layer would sit on {company}'s setup?",
        )
    if category == "expansion":
        return (
            f"Noticed this at {company}: {hook}. Growth like that quietly widens the "
            "prospecting surface: new territory, new accounts, and a playbook "
            "that suddenly has to travel to people who did not build it.",
            "I set up agent pipelines that give an expanding team one shared system "
            "for finding, enriching, and scoring accounts, with drafts grounded in "
            "what is actually happening at each company. The new ground gets "
            "consistent coverage without the original team cloning its habits by hand.",
            f"Would it help to see what that coverage could look like for {company} this quarter?",
        )
    if category == "hiring":
        return (
            f"Saw {company} is {hook}. New reps inherit whatever research habits "
            "already exist, so the weeks before they start are the best window to "
            "upgrade those habits.",
            "I build pipelines that hand a new hire a ranked, researched account "
            "list and a grounded draft for each first touch, all scored on a rubric "
            "managers can audit. Ramp time goes to learning customers instead of "
            "learning where the data hides.",
            "Useful to see the rubric side of that before the team grows further?",
        )
    if category == "leadership":
        return (
            f"Saw this at {company}: {hook}. New leadership usually reopens an old "
            "question: which accounts deserve the team's time, and can anyone show "
            "the math behind the answer?",
            "That audit trail is what I build: agent driven enrichment and scoring "
            "where every point carries its reason, and drafts tied to live signals "
            "at each account. A new leader gets a pipeline they can inspect, not a "
            "stack of rep folklore.",
            "Would a walkthrough of the scoring side be useful while the playbook is still being set?",
        )
    if category == "partnership":
        return (
            f"Noticed this at {company}: {hook}. Partner motions live or die on follow up "
            "speed, and follow up is usually where a small team runs out of week.",
            "I build the unglamorous middle of that motion: partner accounts "
            "enriched and scored as they appear, with first drafts ready for a "
            "human to approve. Coverage gets consistent without anyone hiring a "
            "coordinator to chase lists.",
            f"Worth a look at how that would cover {company}'s launch window?",
        )
    if category == "acquisition":
        return (
            f"Saw this at {company}: {hook}. An acquisition instantly grows the book, and "
            "the inherited half is always the part nobody has researched yet.",
            "I help teams work that inherited book with agent driven enrichment and "
            "scoring, so the combined list gets ranked by fit instead of by whoever "
            "remembers a name. Drafts follow the same signals, and a person still "
            "approves every send.",
            "Would it help to see the combined accounts ranked before renewal season hits?",
        )
    if category == "pain":
        return (
            f"Did a little digging on {company}: {hook}. That kind of manual grind "
            "works right up until volume arrives, and then it is the first thing "
            "to crack.",
            "I help teams in that exact spot put a small agent system under the "
            "work: accounts researched and scored automatically, drafts prepared "
            "from real signals, and a person approving every send. The process "
            "stops depending on memory and starts leaving a trail the whole team "
            "can see.",
            f"If I mapped that onto {company}'s current setup, would you be open to a look?",
        )
    if category == "growth":
        return (
            f"Saw this at {company}: {hook}. Momentum like that tends to expose the gap "
            "between demand and the hours a team has to chase it.",
            "I put agent workflows underneath that chase: every new account "
            "enriched, scored, and drafted against within a day, with a human "
            "approving what goes out. Growth stops waiting on whoever had a free "
            "afternoon to do research.",
            f"Open to seeing how that would handle {company}'s current inflow?",
        )
    return (
        f"Been following {company}: {hook}. It stood out because it is exactly the "
        "kind of signal that usually ends up buried in a rep's notes.",
        "I build AI pipelines for revenue teams that turn signals like this into "
        "enriched, scored accounts and a grounded first draft, reviewed by a "
        "person before anything is sent. Reps open their day at the conversation, "
        "not at the research.",
        f"Worth comparing notes on how {company} handles that research step today?",
    )


def _template_draft(lead: dict, enrichment: dict, score: dict) -> dict:
    """Deterministic personalization built from the lead's primary signal."""
    first, company = lead["first_name"], lead["company"]

    raw_hook = lead["hook"].strip()
    hook = raw_hook.replace(" - ", ", ")
    if hook[:1].isupper():
        hook = hook[:1].lower() + hook[1:]

    category = _category(lead, enrichment)
    opener, value, closing = _parts(category, first, company, hook, lead["title"])

    # One sentence keyed to this lead's own enrichment, so no two drafts
    # carry the same middle paragraph.
    topic = enrichment["intent_topics"][0]
    topic_txt = topic if topic.startswith("CRM") else topic[:1].lower() + topic[1:]
    tech = enrichment["tech_stack"][0]
    value += (f" For {company}, the first pass keys off {topic_txt}, "
              f"with {tech} already in the stack.")

    subject = f"{first}: {raw_hook[:48]}"
    body = (
        f"Hi {first},\n\n{opener}\n\n{value}\n\n"
        f"{closing}\n\n"
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
