#!/usr/bin/env python3
"""AI outreach pipeline demo — synthetic data, end to end, one command.

    python3 pipeline.py
    python3 pipeline.py --min-score 55 --out demo/output

Stages: 1) ingest & validate CSV  2) enrich (SIMULATED)  3) score 0-100 + tiers
        4) draft personalized outreach  5) write report + CSV + emails.

Zero dependencies (stdlib only). All people/companies are fictional.
"""
import argparse
import csv
import os
import sys
from collections import Counter
from datetime import date

from enrich import enrich_lead
from scoring import score_lead
from drafting import draft_email


def load_leads(path: str) -> list[dict]:
    leads = []
    with open(path, newline="", encoding="utf-8") as f:
        # skip '#' comment lines (the synthetic-data notice)
        rows = [ln for ln in f if not ln.lstrip().startswith("#")]
    for row in csv.DictReader(rows):
        if not row.get("lead_id"):
            continue
        leads.append({k: (v or "").strip() for k, v in row.items()})
    required = {"lead_id", "first_name", "last_name", "title", "company",
                "industry", "website", "city", "state", "hook"}
    missing = required - set(leads[0].keys())
    if missing:
        sys.exit(f"Input CSV missing columns: {sorted(missing)}")
    return leads


def write_report(out_dir: str, results: list[dict], min_score: int) -> None:
    tiers = Counter(r["score"]["tier"] for r in results)
    top = sorted(results, key=lambda r: r["score"]["score"], reverse=True)[:10]
    lines = [
        "# Outreach pipeline — run report",
        "",
        f"Date: {date.today().isoformat()}",
        f"Leads processed: {len(results)} (synthetic data — all fictional)",
        f"Minimum score filter: {min_score}",
        "",
        "## Honesty notes",
        "- **Enrichment is simulated** (deterministic mock, seeded per lead). In production this stage calls real enrichment APIs.",
        "- **Drafts**: template engine by default; set `ANTHROPIC_API_KEY` + `ANTHROPIC_MODEL` for live Claude drafting.",
        "- No emails are sent. This pipeline produces drafts for human review (approve-and-send).",
        "",
        "## Tier distribution",
        "",
    ]
    for tier in ("A", "B", "C"):
        lines.append(f"- Tier {tier}: {tiers.get(tier, 0)}")
    lines += ["", "## Top 10 leads", "",
              "| Score | Tier | Name | Title | Company |",
              "|------:|:----:|------|-------|---------|"]
    for r in top:
        l, s = r["lead"], r["score"]
        lines.append(f"| {s['score']} | {s['tier']} | {l['first_name']} {l['last_name']} "
                     f"| {l['title']} | {l['company']} |")
    lines += ["", "## Per-lead scoring reasons (top 10)", ""]
    for r in top:
        l, s = r["lead"], r["score"]
        lines.append(f"### {l['first_name']} {l['last_name']} — {l['company']} ({s['score']}, tier {s['tier']})")
        lines += [f"- {reason}" for reason in s["reasons"]] + [""]
    with open(os.path.join(out_dir, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def write_outputs(out_dir: str, results: list[dict]) -> None:
    with open(os.path.join(out_dir, "scored_leads.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["lead_id", "name", "title", "company", "score", "tier",
                    "employee_estimate", "funding_stage", "tech_stack"])
        for r in results:
            l, s, e = r["lead"], r["score"], r["enrichment"]
            w.writerow([l["lead_id"], f"{l['first_name']} {l['last_name']}", l["title"],
                        l["company"], s["score"], s["tier"],
                        e["employee_estimate"], e["funding_stage"], ";".join(e["tech_stack"])])

    with open(os.path.join(out_dir, "outreach_emails.md"), "w", encoding="utf-8") as f:
        f.write("# Drafted outreach (SYNTHETIC — review before anything goes anywhere)\n\n")
        for r in results:
            l, d, s = r["lead"], r["draft"], r["score"]
            f.write(f"---\n\n## {l['first_name']} {l['last_name']} — {l['company']} "
                    f"(score {s['score']}, tier {s['tier']})\n\n")
            f.write(f"To: {d['to']}\nSubject: {d['subject']}\n\n{d['body']}\n\n")
            f.write(f"*Drafted by: {d['drafted_by']}*\n\n")


def main() -> None:
    ap = argparse.ArgumentParser(description="AI outreach pipeline demo (synthetic data)")
    ap.add_argument("--input", default="data/leads.csv")
    ap.add_argument("--out", default="output")
    ap.add_argument("--min-score", type=int, default=0)
    args = ap.parse_args()

    print("[1/5] Ingest & validate…")
    leads = load_leads(args.input)
    print(f"      {len(leads)} synthetic leads loaded from {args.input}")

    print("[2/5] Enrich (SIMULATED)…")
    print("[3/5] Score…")
    results = []
    for lead in leads:
        enrichment = enrich_lead(lead)
        score = score_lead(lead, enrichment)
        results.append({"lead": lead, "enrichment": enrichment, "score": score})
    results = [r for r in results if r["score"]["score"] >= args.min_score]
    tiers = Counter(r["score"]["tier"] for r in results)
    print(f"      scored {len(results)} leads → "
          f"A:{tiers.get('A', 0)} B:{tiers.get('B', 0)} C:{tiers.get('C', 0)}")

    print("[4/5] Draft personalized outreach…")
    for r in results:
        r["draft"] = draft_email(r["lead"], r["enrichment"], r["score"])
    print(f"      {len(results)} drafts written (approve-and-send: nothing sent)")

    print("[5/5] Write report…")
    os.makedirs(args.out, exist_ok=True)
    write_outputs(args.out, results)
    write_report(args.out, results, args.min_score)
    print(f"      → {args.out}/report.md, scored_leads.csv, outreach_emails.md")
    print("Done.")


if __name__ == "__main__":
    main()
