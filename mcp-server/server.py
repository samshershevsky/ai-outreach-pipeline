#!/usr/bin/env python3
"""gtm-pipeline-mcp: a demo MCP server for the outreach pipeline.

Speaks the Model Context Protocol over stdio (JSON RPC 2.0), stdlib only,
no dependencies and no network calls. It exposes the demo pipeline in
../demo as tools, running on the same 25 synthetic leads:

- enrich_lead(lead_id): simulated enrichment for one lead
- score_lead(lead_id): rubric score, tier, and reason strings
- draft_outreach(lead_id): a grounded outreach draft (never sent)
- get_report(): tier distribution and the top ranked leads

Run it directly to speak MCP over stdin and stdout:

    python3 mcp-server/server.py

See README.md in this folder for how to connect it to Claude.
"""
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "demo"))

from enrich import enrich_lead as _enrich          # noqa: E402
from scoring import score_lead as _score          # noqa: E402
from drafting import draft_email as _draft        # noqa: E402
from pipeline import load_leads                   # noqa: E402

SERVER_NAME = "gtm-pipeline-mcp"
SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2024-11-05"

_LEADS = {l["lead_id"]: l for l in load_leads(str(REPO_ROOT / "demo" / "data" / "leads.csv"))}

TOOLS = [
    {
        "name": "enrich_lead",
        "description": "Return simulated enrichment (headcount, tech stack, hiring signals, intent topics) for one synthetic lead.",
        "inputSchema": {
            "type": "object",
            "properties": {"lead_id": {"type": "string", "description": "Lead id, one of L001 to L025"}},
            "required": ["lead_id"],
        },
    },
    {
        "name": "score_lead",
        "description": "Score one synthetic lead against the ICP rubric. Returns the 0 to 100 score, the tier, and a reason string for every point.",
        "inputSchema": {
            "type": "object",
            "properties": {"lead_id": {"type": "string", "description": "Lead id, one of L001 to L025"}},
            "required": ["lead_id"],
        },
    },
    {
        "name": "draft_outreach",
        "description": "Draft a first touch email for one synthetic lead, grounded in that lead's signals. Draft only: this tool never sends anything.",
        "inputSchema": {
            "type": "object",
            "properties": {"lead_id": {"type": "string", "description": "Lead id, one of L001 to L025"}},
            "required": ["lead_id"],
        },
    },
    {
        "name": "get_report",
        "description": "Summarize the full synthetic dataset: tier distribution and the top 10 leads with scores and reasons.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def _lead(lead_id: str) -> dict:
    if lead_id not in _LEADS:
        raise ValueError(f"Unknown lead_id '{lead_id}'. Valid ids run from L001 to L025.")
    return _LEADS[lead_id]


def _pipeline_for(lead: dict):
    enrichment = _enrich(lead)
    score = _score(lead, enrichment)
    return enrichment, score


def call_tool(name: str, args: dict):
    if name == "enrich_lead":
        lead = _lead(args["lead_id"])
        return {"lead_id": lead["lead_id"], "company": lead["company"],
                "enrichment": _enrich(lead)}
    if name == "score_lead":
        lead = _lead(args["lead_id"])
        _, score = _pipeline_for(lead)
        return {"lead_id": lead["lead_id"], "company": lead["company"], **score}
    if name == "draft_outreach":
        lead = _lead(args["lead_id"])
        enrichment, score = _pipeline_for(lead)
        draft = _draft(lead, enrichment, score)
        return {"lead_id": lead["lead_id"], "score": score["score"],
                "tier": score["tier"], "draft": draft}
    if name == "get_report":
        results = []
        for lead in _LEADS.values():
            _, score = _pipeline_for(lead)
            results.append({"lead_id": lead["lead_id"],
                            "name": f"{lead['first_name']} {lead['last_name']}",
                            "title": lead["title"], "company": lead["company"],
                            "score": score["score"], "tier": score["tier"],
                            "reasons": score["reasons"]})
        tiers = Counter(r["tier"] for r in results)
        top = sorted(results, key=lambda r: r["score"], reverse=True)[:10]
        return {"leads_processed": len(results),
                "tier_distribution": {t: tiers.get(t, 0) for t in ("A", "B", "C")},
                "top_10": top,
                "note": "Synthetic data only. Drafts are produced for human review; nothing is sent."}
    raise ValueError(f"Unknown tool '{name}'")


def handle(msg: dict):
    method = msg.get("method", "")
    mid = msg.get("id")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION}}}
    if method == "notifications/initialized":
        return None
    if method == "ping":
        return {"jsonrpc": "2.0", "id": mid, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = msg.get("params", {})
        try:
            result = call_tool(params.get("name", ""), params.get("arguments", {}))
            return {"jsonrpc": "2.0", "id": mid, "result": {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
                "isError": False}}
        except Exception as exc:
            return {"jsonrpc": "2.0", "id": mid, "result": {
                "content": [{"type": "text", "text": f"Error: {exc}"}],
                "isError": True}}
    if mid is not None:
        return {"jsonrpc": "2.0", "id": mid,
                "error": {"code": -32601, "message": f"Method not found: {method}"}}
    return None


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(msg)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
