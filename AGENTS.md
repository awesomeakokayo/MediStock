# Guidelines for AI Coding Agents

## 1. Single Source of Truth
- The Engineering PRD ([PRD.md](./PRD.md) / [docs/PRD.md](./docs/PRD.md)) is the **implementation specification** for the CareGrid/MediStock prototype.
- The research report and analysis package in [`analysis/`](./analysis/) provide **empirical context and problem motivation**, not a build specification.

## 2. Team Split and Ownership
Adhere strictly to the two-track boundary:
- **Track A (Foundation and logic):** `src/domain/`, `src/services/`, `src/repositories/`, `src/lib/`, `src/data/seed/`, `src/tests/`, `PRD.md`.
- **Track B (Interface and design):** `src/app/`, `src/components/`, `src/styles/`, `src/features/*/components/`.
- UI components call services only. Never import IndexedDB/Dexie or domain balance calculators directly in components.

## 3. Evidence-Base & Data Truthfulness Rules
- **Synthetic Data Notice:** All challenge dataset numbers and all seeded demo records are synthetic. Always mark them clearly as "synthetic / demo data".
- **No False Claims:** Do not claim measured stockout, clinical outcome, or carbon emission reductions as proven results.
- **Surplus-Supply Framing:** Resource matching is surplus-to-shortage coordination for usable supplies, never a surge-capacity/ICU-shock fix.
- **Demand Curve:** The demand surge for consumables follows the research dataset's respiratory illness index (Section 17.2: 1.24, 1.14, 1.23, 1.27, 1.18, 1.19, 1.10, 1.08, 1.05, 1.05, 1.03, 1.00).

## 4. Design & Interaction
- Use **semantic design tokens** defined in Appendix A of the PRD (`--cg-bg`, `--cg-surface`, `--cg-primary`, etc.). Never hardcode raw hex values in components.
- Status must always show **icon + text label + colour** (WCAG 1.4.1 compliance).
- Ensure mobile responsiveness (390px, 768px, 1280px) with no horizontal scroll.
