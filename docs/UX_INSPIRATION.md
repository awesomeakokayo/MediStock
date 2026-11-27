# MediStock UX & UI Inspiration Guide

**Purpose:** Research-backed visual and interaction references for the MediStock web application.  
**Status:** Directional reference, not a request to copy another product.  
**Product source of truth:** `/PRD.md` remains authoritative for scope, design tokens, responsive rules, workflows and acceptance criteria.

## 1. Product design principle

MediStock is an operational healthcare resource tool, not a generic SaaS marketing template. Design for busy pharmacists, store officers, laboratory personnel and facility managers who need to record stock events accurately and find operational risks quickly.

Do not use the default landing-page composition of headline and paragraph on the left with a floating dashboard mockup on the right. The public landing page should have its own editorial composition and product storytelling. The authenticated workspace should prioritise task completion, information density and clear hierarchy.

## 2. Research references

These are public inspiration references. Some are concept designs and must not be treated as validated workflows or clinical guidance.

### Mobbin — real product patterns

- [Mobbin: Healthcare app category](https://mobbin.com/explore/mobile/app-categories/healthcare-app) — inspect real healthcare product screens, navigation, search, filtering, cards, onboarding and status patterns.
- [Mobbin: Medical app category](https://mobbin.com/explore/mobile/app-categories/medical) — useful references for medical product interaction patterns, bottom sheets, tab bars, search and task flows.
- [Mobbin: Dashboard design research](https://mobbin.com/blog/what-good-dashboard-design-looks-like) — dashboard hierarchy and how to surface useful answers rather than dumping metrics.
- [Mobbin: Sidebar pattern](https://mobbin.com/glossary/sidebar) — navigation trade-offs for complex applications.

### Dribbble — visual exploration

- [Pharmacy Control Center — dashboard](https://dribbble.com/shots/27340655-Pharmacy-SaaS-UI-Dashboard-Design-Pharmacy-Control-Center-HM) — transaction, inventory, filtering and audit-trail visual references.
- [Pharmacii — pharmacy UI elements](https://dribbble.com/shots/26969407-Pharmacii-Smart-Pharmacy-Management-UI-Elements-Dashboard) — reusable inventory, prescription and expiry components; inspect consistency across mobile and desktop.
- [RxFlow — batch management](https://dribbble.com/shots/27916597-RxFlow-Pharmacy-Operations-Inventory-Batch-Management) — strong reference for batch-level stock, expiry, par levels and severity states.
- [PharmaSync / AI inventory dashboard](https://dribbble.com/shots/27728208-Healthcare-SaaS-UI-UX-AI-pharmacy-inventory-dashboard-design) — useful table hierarchy, expiry visibility, stock bars and plain-language AI insights.
- [Pharmacy inventory management](https://dribbble.com/shots/17315108-Pharmacy-Inventory-Management) — older inventory screen reference; use for comparison, not as a visual target.
- [Dribbble inventory dashboard search](https://dribbble.com/search/inventory-stock-dashboard) — broader stock, warehouse and operations patterns.
- [Dribbble pharmacy dashboard search](https://dribbble.com/search/pharmacy-dashboard) — further pharmacy dashboard explorations.

### Behance — fuller case studies

- [Medtrack — Pharmacy Inventory Dashboard](https://www.behance.net/gallery/245957763/Medtrack-Pharmacy-Inventory-Dashboard) — multi-role pharmacy workflow covering inventory, expiry, purchasing, suppliers, returns and reporting; especially relevant regional context.
- [Nixfarma — pharmacy software UX redesign](https://www.behance.net/gallery/248899451/Nixfarma-UX-Redesign-for-Pharmacy-Software) — redesigning a mature operational product without disrupting established workflows; accessibility and role-based needs.
- [ProHealium RxPMS](https://www.behance.net/gallery/217838351/Pharmacy-Management-System-ProHealiums-RxPMS) — dashboard, POS, stock alerts, analytics and role-based workflow coverage.
- [Pharmacy dashboard UX case study](https://www.behance.net/gallery/228857353/Pharmacy-Dashboard-UIUX-Design-case-study) — order tracking, medicine management and status updates.
- [Pharmedica](https://www.behance.net/gallery/101032499/Pharmedica-UIUX-Case-Study) — pharmacy network concept connecting pharmacies and a pharmacy-facing dashboard.

## 3. What to study in each reference

Do not copy screenshots blindly. Inspect the full flow and record the interaction pattern:

1. **Information hierarchy:** What is visible first? Which metrics are genuinely actionable?
2. **Navigation:** How are frequent tasks reached? Is the sidebar too dominant?
3. **Inventory table:** How do product, batch, location, available quantity, unit, expiry and status fit together?
4. **Stock movement:** How does the interface distinguish receipt, internal issue, consumption, return, wastage and adjustment?
5. **Forms:** Are high-frequency forms short, grouped and keyboard-friendly? Are defaults sensible?
6. **Alerts:** Can users distinguish low stock, expiry risk, expired, quarantined and out-of-stock without relying on colour alone?
7. **Analytics:** Are chart labels, units, periods and comparisons explicit? Can users drill down to source transactions?
8. **AI recommendations:** Is the recommendation expressed in plain language with evidence, assumptions and a next action?
9. **Responsive behaviour:** What changes on tablet and mobile? Do tables become cards or horizontally scrollable data regions?
10. **Accessibility:** Contrast, text size, focus state, keyboard access, touch targets and non-colour status indicators.

## 4. MediStock design direction

### Public landing page

Avoid the generic SaaS hero. Explore an editorial / product-led composition:
- A strong full-width statement and a distinctive visual system built from real product interface fragments, not a floating generic dashboard card.
- A visual explanation of the resource lifecycle: receive → store → issue → consume → analyse → plan.
- A connected-facility story showing how stock visibility can reduce avoidable shortages and waste.
- A clear product demonstration section with deliberate crops of real MediStock screens.
- A proof/impact section using measurable product outcomes only; never invent customer metrics.
- A compact, direct call to action.

Potential compositions to explore: asymmetric editorial grid, oversized typographic section, full-bleed product workflow, split-screen data story, horizontal process narrative and modular bento-like evidence panels. Use these as layout studies, not a preselected template.

### Authenticated application

- Keep the current PRD palette and typography tokens. Do not introduce new colours or fonts.
- Use a restrained application shell with clear page titles and one obvious primary action per screen.
- Make inventory and movement tables the main working surfaces; cards should summarise, not replace, operational data.
- Prefer side panels / drawers for quick record workflows when users need to retain table context.
- Show stock quantity and unit together; never display a bare number without its unit.
- Display batch and expiry information wherever batch-controlled stock is selected or issued.
- Use explicit text labels and icons alongside status colours.
- Keep AI insights concise and adjacent to the data they explain.
- Keep the demo/local-data notice visible, as required by the PRD.

## 5. Screen-by-screen reference checklist

| MediStock screen | Reference pattern to investigate | MediStock requirement |
|---|---|---|
| Overview | Operational dashboard, exception-first hierarchy | Surface low stock, expiry, recent movements and key consumption trends |
| Inventory | Dense but readable catalogue/table | Search, filter, category, stock, location, batch/expiry visibility |
| Product detail | Master-detail / activity timeline | Product identity, batches, stock by location and complete movement history |
| Record movement | Drawer, progressive disclosure, validated form | Distinguish receipt, issue, consumption, return, waste and adjustment |
| Equipment | Asset register and status history | Serial/asset ID, location, assignment, condition and maintenance |
| Analytics | Filterable reports and drill-down | Explicitly separate purchase, receipt, issue, consumption, wastage and expiry |
| Recommendations | Alert + evidence + suggested action | Explain inputs, assumptions, data sufficiency and human approval |
| Resource network | Matching / request workflow | Show eligible surplus, shortage, match rationale and approval state |

## 6. Anti-patterns to avoid

- Generic SaaS hero with left-aligned copy and a right-side dashboard screenshot.
- Gradient blobs, excessive glassmorphism, glowing cards or decorative chart clutter.
- A dashboard made entirely of equal-sized KPI cards.
- Hiding expiry date or batch number inside a deep detail screen.
- Treating every stock decrease as consumption.
- Treating issue to a department as proof that a product was used.
- Inferring a disease from a medicine name.
- AI chat as the main interface when a table, filter or clear action is faster.
- Colour-only status communication.
- Fake real-time indicators, fake integrations or invented impact metrics.

## 7. Implementation instructions for coding agents

1. Read `/PRD.md` before building or changing any screen.
2. Treat this file as visual/UX research guidance only. It does not override requirements, design tokens, data rules or acceptance criteria in the PRD.
3. Use the links above as references to inspect. Do not copy proprietary assets, screenshots, branding, text or exact layouts.
4. Do not change the established palette, typography, framework or component stack to match an inspiration reference.
5. Do not redesign the whole product based on one Dribbble shot. Combine patterns that improve actual MediStock workflows.
6. Before implementing the landing page, propose at least two materially different page compositions using the existing tokens; choose the one that best explains the product rather than the most decorative one.
7. For each operational screen, prioritise the user's task, data relationships, error prevention and keyboard flow.
8. Preserve responsive behaviour and accessibility requirements from the PRD.
9. Do not add backend calls or remote AI dependencies to the local-first demo.
10. If a reference is inaccessible, use the other links; do not invent details about unseen screens.

## 8. Research log template

When the team reviews a reference, add a short entry here:

- **Reference / URL:**
- **Screen or flow inspected:**
- **Pattern worth adopting:**
- **What does not fit MediStock:**
- **MediStock screen affected:**
- **Decision:** Adopt / Adapt / Reject
