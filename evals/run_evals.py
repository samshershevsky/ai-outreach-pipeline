#!/usr/bin/env python3
"""Evals for the outreach pipeline demo.

Runs against the 25 synthetic leads in demo/data/leads.csv and checks:

1. Scoring consistency: the same lead scores identically across 5 runs.
2. Rubric correctness: every score matches an independent recomputation of
   the rubric math, and every point awarded carries a reason string.
3. Draft grounding: every draft references at least one real signal from
   that lead's data, names only that lead's company, and contains no
   numbers or claims that are absent from the lead's data.
4. Tool calls: enrichment, scoring, and drafting are exercised as tools;
   success rate and latency are measured for every call.

Results are written to evals/results.json (and mirrored to
docs/evals-results.json so the live site can display the same numbers).
The script exits nonzero if any check fails, so CI cannot go green on a
broken pipeline. Stdlib only.
"""
import json
import os
import re
import statistics
import sys
import time
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEMO_DIR = REPO_ROOT / "demo"
sys.path.insert(0, str(DEMO_DIR))

# Force the deterministic template engine: evals must not depend on an API.
os.environ.pop("ANTHROPIC_API_KEY", None)
os.environ.pop("ANTHROPIC_MODEL", None)

from enrich import enrich_lead          # noqa: E402
from scoring import score_lead          # noqa: E402
from drafting import draft_email        # noqa: E402
from pipeline import load_leads         # noqa: E402

RUNS = 5
TITLE_TIERS = [
    (("chief", "cfo", "cro", "ceo", "president", "founder", "owner"), 30),
    (("vp", "vice president"), 25),
    (("director", "head of"), 20),
    (("manager",), 10),
]
HIGH_FIT = {"SaaS", "Fintech", "Healthcare", "Analytics", "Edtech"}
FORBIDDEN_CLAIMS = ["half that time", "%", "$", "quota", "guarantee"]


def expected_score(lead: dict, enrichment: dict) -> int:
    """Independent recomputation of the rubric, used as the oracle."""
    total = 0
    t = lead["title"].lower()
    pts = 5
    for keywords, value in TITLE_TIERS:
        if any(k in t for k in keywords):
            pts = value
            break
    total += pts
    emp = enrichment["employee_estimate"]
    total += 25 if 50 <= emp <= 1000 else 10 if 1000 < emp <= 5000 else 5
    total += 15 if lead["industry"] in HIGH_FIT else 8
    total += 7 * min(len(enrichment["hiring_signals"]), 3)
    total += 10 if enrichment["pain_detected"] else 0
    return min(total, 100)


def lead_signals(lead: dict, enrichment: dict) -> list[str]:
    """Every factual signal a draft is allowed to reference for this lead."""
    signals = [lead["hook"], lead["company"], lead["title"], lead["industry"],
               lead["city"], lead["state"]]
    signals += enrichment["hiring_signals"]
    signals += enrichment["tech_stack"]
    signals += enrichment["intent_topics"]
    signals.append(enrichment["funding_stage"])
    return [s for s in signals if s]


def check_consistency(leads):
    checked, stable = 0, 0
    for lead in leads:
        enrichment = enrich_lead(lead)
        scores = {score_lead(lead, enrichment)["score"] for _ in range(RUNS)}
        checked += 1
        stable += 1 if len(scores) == 1 else 0
    return {"leads_checked": checked, "runs_per_lead": RUNS,
            "stable_leads": stable, "passed": stable == checked}


def check_rubric(leads):
    checked, matched, reasons_ok = 0, 0, 0
    for lead in leads:
        enrichment = enrich_lead(lead)
        result = score_lead(lead, enrichment)
        checked += 1
        if result["score"] == expected_score(lead, enrichment):
            matched += 1
        reasons = result["reasons"]
        points_listed = 0
        ok = bool(reasons)
        for reason in reasons:
            if ": +" not in reason and ", +" not in reason:
                ok = False
                break
            m = re.search(r"\+(\d+)", reason)
            if not m:
                ok = False
                break
            points_listed += int(m.group(1))
        if ok and min(points_listed, 100) == result["score"]:
            reasons_ok += 1
    return {"leads_checked": checked, "scores_matching_rubric": matched,
            "leads_with_full_reason_strings": reasons_ok,
            "passed": matched == checked and reasons_ok == checked}


def check_grounding(leads):
    all_companies = {l["company"] for l in leads}
    checked, grounded = 0, 0
    failures = []
    for lead in leads:
        enrichment = enrich_lead(lead)
        score = score_lead(lead, enrichment)
        draft = draft_email(lead, enrichment, score)
        body = draft["body"]
        checked += 1
        ok = True
        # References at least one real signal from this lead's own data
        # beyond the company name itself.
        non_company = [s for s in lead_signals(lead, enrichment)
                       if s != lead["company"]]
        if not any(s.lower() in body.lower() for s in non_company):
            ok = False
            failures.append(f"{lead['lead_id']}: no lead signal referenced")
        # Names no other lead's company (no cross lead fact bleed).
        others = [c for c in all_companies
                  if c != lead["company"] and c.lower() in body.lower()]
        if others:
            ok = False
            failures.append(f"{lead['lead_id']}: mentions other companies {others}")
        # Invents no facts: any number in the draft must exist in the data.
        data_text = json.dumps(lead) + json.dumps(enrichment)
        draft_numbers = {tok.strip(".,%:") for tok in body.split()
                         if any(ch.isdigit() for ch in tok)}
        invented = {n for n in draft_numbers if n and n not in data_text}
        if invented:
            ok = False
            failures.append(f"{lead['lead_id']}: invented numbers {sorted(invented)}")
        # No forbidden or unsourced claims.
        for claim in FORBIDDEN_CLAIMS:
            if claim in body.lower():
                ok = False
                failures.append(f"{lead['lead_id']}: forbidden claim '{claim}'")
        if lead["company"].lower() not in body.lower():
            ok = False
            failures.append(f"{lead['lead_id']}: company not referenced")
        grounded += 1 if ok else 0
    return {"drafts_checked": checked, "drafts_grounded": grounded,
            "failures": failures, "passed": grounded == checked}


def check_tool_calls(leads):
    tools = {"enrich_lead": enrich_lead, "score_lead": None, "draft_email": None}
    latencies_ms = []
    calls, failed = 0, 0

    def timed(fn, *args):
        nonlocal calls, failed
        start = time.perf_counter()
        try:
            out = fn(*args)
            ok = out is not None
        except Exception:
            ok, out = False, None
        latencies_ms.append((time.perf_counter() - start) * 1000)
        calls += 1
        failed += 0 if ok else 1
        return out

    for lead in leads:
        enrichment = timed(tools["enrich_lead"], lead)
        score = timed(score_lead, lead, enrichment)
        timed(draft_email, lead, enrichment, score)

    latencies_ms.sort()
    p95 = latencies_ms[min(len(latencies_ms) - 1,
                           int(0.95 * len(latencies_ms)))] if latencies_ms else 0.0
    return {
        "tool_calls": calls,
        "failed_calls": failed,
        "success_rate_pct": round(100.0 * (calls - failed) / calls, 2) if calls else 0.0,
        "mean_latency_ms": round(statistics.mean(latencies_ms), 3) if latencies_ms else 0.0,
        "p95_latency_ms": round(p95, 3),
        "max_latency_ms": round(max(latencies_ms), 3) if latencies_ms else 0.0,
        "passed": failed == 0,
    }


def main() -> int:
    leads = load_leads(str(DEMO_DIR / "data" / "leads.csv"))
    results = {
        "generated_on": date.today().isoformat(),
        "dataset": "demo/data/leads.csv (25 synthetic leads)",
        "engine": "template engine, deterministic, no API calls",
        "checks": {
            "scoring_consistency": check_consistency(leads),
            "rubric_correctness": check_rubric(leads),
            "draft_grounding": check_grounding(leads),
            "tool_calls": check_tool_calls(leads),
        },
    }
    results["all_passed"] = all(c["passed"] for c in results["checks"].values())

    out_path = REPO_ROOT / "evals" / "results.json"
    out_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    site_copy = REPO_ROOT / "docs" / "evals-results.json"
    if site_copy.parent.exists():
        site_copy.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

    for name, check in results["checks"].items():
        status = "PASS" if check["passed"] else "FAIL"
        print(f"[{status}] {name}: {json.dumps(check)}")
    print(f"Overall: {'PASS' if results['all_passed'] else 'FAIL'} "
          f"({len(leads)} leads). Results written to {out_path}")
    return 0 if results["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
