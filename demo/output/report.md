# Outreach pipeline — run report

Date: 2026-10-01
Leads processed: 25 (synthetic data — all fictional)
Minimum score filter: 0

## Honesty notes
- **Enrichment is simulated** (deterministic mock, seeded per lead). In production this stage calls real enrichment APIs.
- **Drafts**: template engine by default; set `ANTHROPIC_API_KEY` + `ANTHROPIC_MODEL` for live Claude drafting.
- No emails are sent. This pipeline produces drafts for human review (approve-and-send).

## Tier distribution

- Tier A: 4
- Tier B: 14
- Tier C: 7

## Top 10 leads

| Score | Tier | Name | Title | Company |
|------:|:----:|------|-------|---------|
| 84 | A | Sofia Marino | Chief Revenue Officer | Driftline |
| 80 | A | Robert Hayes | Owner | Ferrostack Supply |
| 77 | A | Chris Novak | Founder | Novak Fitness Systems |
| 77 | A | Sam Whitfield | President | Whitfield Industrial |
| 74 | B | David Okafor | Director of Revenue | Quantia Health |
| 74 | B | Priya Nair | Head of Growth | Vantagewell |
| 74 | B | Daniel Kim | Head of Revenue | Cloudhaven |
| 74 | B | Grace O'Malley | Head of Sales | Datawise |
| 72 | B | Brian Foster | Owner | Foster & Associates |
| 67 | B | Tom Becker | Sales Manager | Copperline Manufacturing |

## Per-lead scoring reasons (top 10)

### Sofia Marino — Driftline (84, tier A)
- Title seniority 'Chief Revenue Officer': +30
- Company size ~600 employees (sweet spot): +25
- Industry 'SaaS' is high-fit: +15
- Buying signal — hiring a sales manager: +7
- Buying signal — hiring account executives: +7

### Robert Hayes — Ferrostack Supply (80, tier A)
- Title seniority 'Owner': +30
- Company size ~600 employees (sweet spot): +25
- Industry 'Wholesale': +8
- Buying signal — hiring SDRs: +7
- Pain signal in research (manual process): +10

### Chris Novak — Novak Fitness Systems (77, tier A)
- Title seniority 'Founder': +30
- Company size ~80 employees (sweet spot): +25
- Industry 'Fitness': +8
- Buying signal — hiring revenue operations: +7
- Buying signal — hiring SDRs: +7

### Sam Whitfield — Whitfield Industrial (77, tier A)
- Title seniority 'President': +30
- Company size ~140 employees (sweet spot): +25
- Industry 'Manufacturing': +8
- Buying signal — hiring a sales manager: +7
- Buying signal — hiring revenue operations: +7

### David Okafor — Quantia Health (74, tier B)
- Title seniority 'Director of Revenue': +20
- Company size ~80 employees (sweet spot): +25
- Industry 'Healthcare' is high-fit: +15
- Buying signal — hiring SDRs: +7
- Buying signal — hiring revenue operations: +7

### Priya Nair — Vantagewell (74, tier B)
- Title seniority 'Head of Growth': +20
- Company size ~140 employees (sweet spot): +25
- Industry 'Fintech' is high-fit: +15
- Buying signal — hiring a sales manager: +7
- Buying signal — hiring revenue operations: +7

### Daniel Kim — Cloudhaven (74, tier B)
- Title seniority 'Head of Revenue': +20
- Company size ~140 employees (sweet spot): +25
- Industry 'SaaS' is high-fit: +15
- Buying signal — hiring SDRs: +7
- Buying signal — hiring revenue operations: +7

### Grace O'Malley — Datawise (74, tier B)
- Title seniority 'Head of Sales': +20
- Company size ~220 employees (sweet spot): +25
- Industry 'SaaS' is high-fit: +15
- Buying signal — hiring revenue operations: +7
- Buying signal — hiring a sales manager: +7

### Brian Foster — Foster & Associates (72, tier B)
- Title seniority 'Owner': +30
- Company size ~1200 employees: +10
- Industry 'Consulting': +8
- Buying signal — hiring account executives: +7
- Buying signal — hiring revenue operations: +7
- Pain signal in research (manual process): +10

### Tom Becker — Copperline Manufacturing (67, tier B)
- Title seniority 'Sales Manager': +10
- Company size ~220 employees (sweet spot): +25
- Industry 'Manufacturing': +8
- Buying signal — hiring SDRs: +7
- Buying signal — hiring a sales manager: +7
- Pain signal in research (manual process): +10

