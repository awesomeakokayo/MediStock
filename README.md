# MediStock (CareGrid)

> AI-enabled healthcare resource intelligence and coordination platform for hospitals, clinics, pharmacies, and laboratories.

## Overview

MediStock (CareGrid) records procurement, stock balances, movements, actual consumption, and reusable equipment tracking to power operational analytics and demand recommendations.

For full technical specifications, architecture guidelines, design tokens, and parallel track assignments, see [PRD.md](./PRD.md) (or [docs/PRD.md](./docs/PRD.md)).

## Quick Links

- [Engineering Product Requirements Document (PRD.md)](./PRD.md)
- [Agent & Contributor Rules (AGENTS.md)](./AGENTS.md)
- [Reproducible Analysis Package (analysis/)](./analysis/README.md)
- [Headline Findings & Key Numbers (key_numbers.json)](./analysis/outputs/key_numbers.json)
- **Primary Target:** Interactive local-first web frontend (Next.js, TypeScript, Tailwind CSS, IndexedDB/Dexie)

---

## Evidence Base & Research Analysis

CareGrid's problem statement and design requirements are directly grounded in empirical analysis of the challenge health performance dataset (32 countries, 212 regions, 2018–2024 panel). 

The reproducible analysis pipeline is located in [`analysis/run_analysis.py`](./analysis/run_analysis.py) with full documentation in [`analysis/README.md`](./analysis/README.md).

### Key Empirical Findings ([`analysis/outputs/key_numbers.json`](./analysis/outputs/key_numbers.json))

1. **ICU Returned, but ED and Elective Care Lagged (Post-Pandemic Gap):**
   - ICU occupancy returned to within 2 percentage points of baseline across all 32 countries by 2024 (median phase mean: Pre-Pandemic 72.3%, Acute 81.8%, Post-Pandemic 72.2%).
   - Conversely, emergency department (ED) 4-hour performance remained **below baseline in all 32 countries** (median gap: **-9.4 points**).
   - Elective wait times remained **31.0% above baseline** (median). Only 8 countries returned to within 10% of their pre-pandemic baseline.

2. **Lagged Impact on Patient Flow:**
   - ED performance trough lagged the ICU peak by a median of **6.0 quarters** (1.5 years), showing that acute surges cascade into protracted front-door bottlenecks.

3. **The Beds vs. Spend Paradox:**
   - Across all 32 countries between 2019 and 2024, hospital beds per 1,000 fell by **-4.8%** (from 3.82 to 3.64), while health expenditure per capita rose by **+19.0%** (nominal USD $4,430 to $5,274).
   - Higher spending without ledger-level operational tracking fails to guarantee resource availability.

4. **Workforce Strain:**
   - Clinical staff vacancy rate and burnout index show a strong positive correlation ($r = 0.58$ across region-years; within-year range $0.35$ to $0.49$).

5. **Resource Matching & Surplus Framing:**
   - During peak surges (e.g., 2021 Q1), **zero** countries had simultaneously an overloaded region ($\ge 85\%$ ICU) next to a region with spare capacity ($< 75\%$).
   - Therefore, CareGrid frames inter-facility resource coordination as **surplus consumable redistribution and expiry mitigation**, not as an emergency clinical surge solution.

6. **The Missing Data Layer:**
   - Macro datasets track high-level indicators but lack facility-level inventory, batch-level shelf-life, and granular consumption records. CareGrid is built to bridge this operational gap.

> **Data Notice:** The research dataset and seeded scenario values are synthetic (simulated for the challenge) and are clearly identified as such.
