# CAREGRID — ENGINEERING PRODUCT REQUIREMENTS DOCUMENT

**Product:** CareGrid  
**Document type:** Engineering PRD / implementation specification  
**Audience:** Frontend developers, coding agents, technical lead, QA and future backend engineers  
**Version:** 1.1 (design system, responsive spec and team-split revision)  
**Status:** Initial build specification for the 48-hour hackathon demo  
**Date:** 27 November 2026  
**Primary implementation target:** Interactive local-first web frontend; no production backend in this phase

> **Revision 1.1 (27 November 2026) — what changed from 1.0**
>
> - **Design:** the generic evergreen/teal tokens are replaced by a palette adapted from the project lead's reference swatches (Sections 10.2–10.4, Appendix A).
> - **UX:** new responsive specification for mobile, tablet and desktop (Section 10.8). Receive / issue / consume / return / waste / adjust are now one responsive **Record** drawer instead of separate pages (Section 9.2).
> - **Team:** two-track ownership and contract rules so two people can build in parallel without collisions (Section 0).
> - **Engineering:** client-only data-layer notes (8.1); ledger clarifications for opening stock, expiry, the batch/location model and double-submit protection (14.2.1); `StockBatch` no longer carries a location; demo clock added (16.4).
> - **Fixes:** FR-012 wording (equipment is a separate register), FR-083 cross-reference (now Section 20), the build plan is split by track (Section 29), and the acceptance checklists are extended.

---

## 0. How to Use This Document

This document is the implementation source of truth for the CareGrid frontend prototype. Read it before changing architecture, creating screens or implementing business logic.

### Instruction priority

1. The explicit requirements and safety constraints in this document.
2. Existing repository conventions, package versions and configured tooling.
3. The shareable team PRD and project overview for product context.
4. Developer judgement for details not specified here, provided the decision does not contradict this document.

### Repository-first rule

If a repository already exists, inspect its framework, package scripts, installed dependencies, routes, design system and existing code before proposing changes. Preserve the existing stack and conventions unless the project lead explicitly approves a change. Do not replace package versions, routing, state management or styling architecture merely because another option is preferred. If this is a new repository, use the proposed default stack in Section 8.

### Phase boundary

The current implementation is **frontend only**. Data entry, updates, calculations, reports and demonstrations must work locally in the browser. Do not create a backend, database server, authentication service, real external integration or production AI connection during the 48-hour demo unless the project lead changes this scope.

The frontend must nevertheless be structured so a future backend can replace the local repository adapter behind stable service interfaces.

### Team split and ownership (two people, parallel work)

Two contributors work in the same repository at the same time. Ownership is **by folder** so that nobody edits the same file and nobody re-implements logic in the wrong place.

| Track | Owner | Owns | Must not edit |
|---|---|---|---|
| **A — Foundation and logic** | Technical lead | `src/domain/`, `src/services/`, `src/repositories/`, `src/lib/`, `src/data/seed/`, `src/tests/`, this PRD | Styling, page layouts, `src/components/` |
| **B — Interface and design** | Frontend / design teammate (using an AI coding tool) | `src/app/`, `src/components/`, `src/styles/`, `src/features/*/components/` | `src/domain/`, `src/services/`, `src/repositories/`, `src/data/seed/` |

**The contract between the tracks is: the TypeScript types (Section 13), the service signatures (Section 15.3) and the seed data (Section 17).** Rules:

1. **UI calls services only.** Screens never touch repositories, IndexedDB/Dexie or raw domain functions, and never calculate stock, analytics or recommendations themselves. If a number is needed, a service provides it.
2. **Track A ships the contract first (target: within the first 3 hours):** (a) all types, (b) every service interface with a **stub implementation that returns realistic fixture data**, (c) the seed fixtures. Track B builds the real screens against the stubs immediately. When Track A replaces a stub with the real implementation, the UI must not need to change.
3. **Missing data or a missing calculation** is requested from Track A (one line in team chat: screen, field, why). Track B does not work around it inside a component.
4. **Contract changes** (a type or service signature) are made only by Track A, in their own small commit, and announced in team chat before Track B pulls. The PRD is updated in the same commit.
5. **Design tokens are binding.** Track B uses only the tokens in Appendix A. No raw hex values, no ad-hoc colours, no new fonts in components.
6. **Git hygiene:** short-lived branches per track (`track-a/<topic>`, `track-b/<topic>`), pull `main` before every working session, merge to `main` at least every ~6 hours, small commits, never force-push `main`.
7. **Integration checkpoints** every ~6 hours: merge both tracks and run the judge demo path (Section 31) end to end.

**Instruction for coding agents:** before editing anything, identify which track the person is working on and stay inside that track's folders. If a task needs changes in the other track's files, stop and tell the person instead of making the change.

---

# PART I — PRODUCT DEFINITION

## 1. Product Summary

CareGrid is an AI-enabled healthcare resource intelligence and coordination platform for hospitals, clinics, pharmacies and laboratories. It records what organisations purchase and receive, what stock they hold, what they issue and consume, what they return or waste, and how reusable equipment is assigned and used. It turns those records into operational analytics and demand recommendations. Future releases will connect verified organisations so they can identify and coordinate eligible surplus resources.

### 1.1 One-line problem statement

Healthcare facilities and pharmacies lack a connected, reliable view of purchasing, consumption and demand, leading to poor procurement decisions, preventable shortages, unnecessary expenditure, limited resource visibility and avoidable waste.

### 1.2 One-line solution

CareGrid is an AI-powered healthcare resource platform that records procurement and consumption, analyses demand patterns, predicts future resource needs and connects participating facilities to coordinate eligible surplus supplies safely.

### 1.3 Product principle

**Capture trustworthy operational data first; provide intelligence and network coordination on top of it.**

## 2. Hackathon Challenge Alignment

The 2026 Health track asks:

> How can healthcare providers increase patient capacity and improve the availability of essential medical supplies while reducing resource wastage, unnecessary procurement, and the environmental impact of healthcare operations?

The overall theme is **Expanding Production in the Face of Environmental Responsibility**.

CareGrid addresses the challenge by improving resource visibility, recording actual consumption, reducing blind procurement, detecting stockout and expiry risks and preparing a controlled way to redirect eligible surplus. Better access to necessary supplies can support service continuity and the use of existing healthcare capacity.

**Scope clarification:** CareGrid's first release is an operational resource-management system. It is not a patient scheduling, bed-management, diagnosis, prescribing or treatment application. Patient-capacity improvements are an intended downstream benefit of better resource availability, not a feature claim for the first demo.

## 3. Product Goals

### 3.1 Demo goals

- Deliver a visually credible, interactive web application.
- Allow users to record and edit meaningful operational data.
- Persist data locally across browser refreshes on the same device and browser profile.
- Demonstrate purchase/receipt, stock movements, consumption and equipment tracking.
- Show analytics that update from the underlying local data.
- Show transparent, deterministic stock and expiry recommendations using seeded synthetic history.
- Demonstrate a simulated resource match between facilities.
- Keep frontend domain logic separate from UI and persistence.

### 3.2 Post-demo product goals

- Establish accurate facility-level inventory and consumption records.
- Support multi-location stock and batch traceability.
- Improve procurement and supply planning through analytics and forecasting.
- Provide multi-organisation resource visibility under controlled permissions.
- Enable safe and auditable transfer of eligible products.
- Integrate with existing health, pharmacy, laboratory and supply-chain systems.

## 4. Non-Goals for the 48-Hour Demo

Do not build or imply that the demo includes:

- Production server, backend API or cloud database.
- Real authentication or secure role enforcement.
- Real multi-tenant isolation or cross-device data synchronisation.
- Real patient records, identifiable health information or clinical record storage.
- Clinical diagnosis, prescribing, treatment or triage.
- Automatic procurement, payment, dispensing or transfer execution.
- Live supplier, hospital, pharmacy, laboratory, government or insurance integrations.
- Live external LLM / forecasting API calls.
- An operational resource marketplace or logistics service.
- Barcode scanner hardware integration (manual fields are acceptable; scanning can be a later extension).
- Cold-chain, blood, controlled medicine, opened clinical product or other high-risk exchange logic.
- Bed management, clinical staffing, appointment scheduling or full hospital management system features.

## 5. Demo Truthfulness and Data Rules

- All seeded records must be synthetic and clearly labelled as demo data.
- All demonstration facilities, staff, suppliers, quantities, costs, dates and trends must be fictional.
- Any generated forecast must be labelled as an estimate or simulated recommendation.
- Do not use patient names, phone numbers, addresses, medical record numbers or other identifiers.
- The local demo's facility switcher is a presentation feature, not a real access-control boundary.
- The local demo's role selector is a simulated view of role-based workflows, not authentication.
- The simulated resource exchange is a proposed match only; it must not show a real dispatch or successful external transfer.

---

# PART II — USERS, WORKFLOWS AND SCOPE

## 6. User Roles and Permissions Model

The demo may use a role selector or demo-user switcher. It should make workflows understandable, but it must not be described as secure authentication.

| Role | Primary permitted work | Sensitive actions |
|---|---|---|
| Store / Inventory Officer | Receive products, manage batches, record internal movements, returns, waste and stock counts. | Stock adjustments and write-offs should show a reason and confirmation. |
| Pharmacist / Pharmacy Manager | Review medicine inventory, batches, expiry, dispensing or pharmacy sales and product demand. | Confirm medicine-related stock corrections; review proposed transfers. |
| Laboratory Officer | Manage reagents, kits, lab locations and recorded consumption. | Record high-value or regulated reagent adjustments with a reason. |
| Procurement Officer | View use, supplier and cost history; review recommended quantities. | Create or approve a purchase request (future backend phase). |
| Facility Administrator | Review facility-level performance and user activity; configure thresholds. | Approve sensitive inventory operations and future transfer requests. |
| Equipment / Department Officer | Register, assign, check out, return and update asset condition. | Mark equipment unavailable, damaged or retired. |
| Network Coordinator | Review participating facilities and resource requests (future). | Coordinate transfers only under formal approval and eligibility controls. |

For production, permissions must be enforced on the server for every resource and action. Frontend route guards and hidden controls are not security controls.

## 7. Core User Journeys

### 7.1 Purchase and receive supplies

1. User selects active facility and receiving storage location.
2. User opens the receive-stock workflow.
3. User selects an existing product or creates a catalogue item.
4. User enters supplier, purchase reference, quantity, unit, unit cost and receipt date.
5. For batch-controlled products, user enters batch/lot number and expiry date. For equipment, user records asset identity and condition instead of a consumable batch.
6. User reviews and confirms.
7. A receipt transaction and stock movement are created.
8. Inventory balances and dashboard indicators refresh.

**Important:** Stock is added on receipt, not merely because a purchase order was created. The demo may combine purchase details and receipt into one simple form, but the domain model must preserve the distinction.

### 7.2 Transfer stock internally to a department

1. User selects source location, destination department/location, product, batch and quantity.
2. System validates that the source location has enough usable stock.
3. User confirms the issue/transfer.
4. The system records a paired stock movement: a decrease at the source and an increase at the destination.
5. The event is labelled as an issue/transfer, not final consumption.

### 7.3 Record actual consumption

1. User selects the department/location where the product is held.
2. User selects product and batch, quantity used, date/time and service/usage category if applicable.
3. User saves the consumption record.
4. The destination/department stock decreases.
5. Analytics count the quantity as consumed.
6. The movement record links to an anonymised service or diagnosis category only when the facility has that information and appropriate governance.

### 7.4 Record returns, wastage, expiry and adjustments

- **Return:** Stock moves from a department/location back to a store only when it remains usable and its status is confirmed.
- **Wastage:** A reason is required (e.g. damaged, spillage, contaminated, broken pack, other).
- **Expiry:** Expired batch quantity is removed from usable stock and recorded as an expiry event; it is never treated as transferable surplus.
- **Adjustment:** A stock count correction requires the counted quantity and reason; the system records the adjustment event rather than silently changing the opening balance.

### 7.5 Equipment lifecycle

1. Register asset with asset code or serial number, category, model, acquisition date/cost where known and condition.
2. Assign asset to a facility and location or department.
3. Record checkout / assignment to a responsible department or user label.
4. Record return, change of location or condition.
5. Record maintenance due date and maintenance history.
6. Mark unavailable, damaged or retired where appropriate.

Equipment is a reusable asset and must not be included in medicine consumption calculations.

### 7.6 Analytics and planning

1. User chooses date range, facility, location, product category or service category.
2. Analytics show purchases, receipts, issues, consumption, returns, wastage, expiries and current stock as separate measures.
3. The top-used product report ranks by recorded consumption or sales, not purchases.
4. Service-category trends use recorded aggregate service/diagnosis categories, not drug-name inference.
5. The user can click through to the supporting transactions.

### 7.7 Resource match demonstration

1. User selects Network Opportunities.
2. The demo engine compares synthetic facility stock and needs.
3. It identifies a possible sender and recipient facility for the same normalised product and suitable pack/unit.
4. It checks quantity, batch status and remaining shelf life in the demo rules.
5. It displays match rationale, limitations and required approvals.
6. It does not execute a transfer or claim that another organisation has accepted it.

---

# PART III — INFORMATION ARCHITECTURE AND UX

## 8. Recommended Frontend Stack

Use the existing repository stack if one exists. For a new frontend repository, the recommended default is:

- **Framework:** Next.js with React and TypeScript.
- **Styling:** Tailwind CSS.
- **UI primitives:** Existing design system if present; otherwise shadcn/ui / Radix primitives where appropriate.
- **Icons:** Lucide icon set.
- **Charts:** Recharts or the charting package already installed.
- **Forms:** React Hook Form plus Zod validation, if compatible with the repository.
- **Local database:** IndexedDB, preferably behind a small wrapper such as Dexie.js.
- **State:** Use the framework's local state and a small shared store only where needed. Avoid introducing heavy global state without a demonstrated need.
- **Testing:** Existing test framework; if none exists, add lightweight unit tests for domain calculations and core workflows before adding broad infrastructure.

### 8.1 Stack notes for the local-first demo

- **Client-only data layer.** Anything that reads IndexedDB is a client component (`'use client'`). Do not server-render data that lives in the browser; show skeletons until local data has loaded. This avoids hydration mismatches.
- **Reactive reads.** Use Dexie `liveQuery` / `useLiveQuery` (or equivalent) so every screen updates after a save without a refresh (FR-060).
- **Atomic writes.** A transfer writes two movement legs inside **one** Dexie transaction so both commit or neither does (Section 14.3).
- **No network dependencies at demo time.** Self-host fonts (e.g. `next/font` or local files), bundle icons and charts, and use no remote images or CDNs. Venue Wi-Fi is unreliable.
- **Presentation fallback.** Deploy a shareable demo link (any static-capable host) **and** keep a local production build ready on the presenting laptop.
- **Deterministic seed.** Seed data uses a fixed seed and the controlled demo date (Section 16.4). No `Math.random()` or `Date.now()` inside seed generation.

Do not pin new major versions without checking current compatibility. Do not put any API key or secret in frontend environment variables that are shipped to the browser.

## 9. Proposed Navigation and Screens

### 9.1 Global application shell

The shell adapts by breakpoint (full detail in Section 10.8):

- **Navigation:** persistent left sidebar on desktop; collapsed icon rail on tablet; bottom tab bar on mobile.
- **Top bar:** CareGrid identity, active facility selector, global search, notifications (demo), role selector (demo) and profile menu. On mobile this reduces to logo, facility pill, search icon and overflow.
- **Global Record action:** one entry point for all stock-changing workflows (Section 9.2).
- **Main content area:** page title, short description, date range when relevant and one primary action.
- **Persistent Local demo data indicator** at every breakpoint (FR-003).

### 9.2 Routes / views

The exact routing syntax may follow the existing framework, but the required views are:

| View | Purpose | Main actions |
|---|---|---|
| Overview / Dashboard | Facility snapshot and action queue. | Switch facility, date range, open flagged items. |
| Inventory | Product catalogue and usable stock by location / batch. | Search, filter, add product, receive stock, view details. |
| Product detail | Product profile, batches, stock by location and history. | Edit permitted metadata, view movement ledger. |
| Stock movements | Complete event history. | Filter, open details, record movement. |
| Receive stock (Record drawer) | Capture purchase and goods receipt. | Select/create product, supplier, quantity, batch, expiry. |
| Issue / transfer (Record drawer) | Move stock between internal locations. | Select source, destination, batch, quantity. |
| Record consumption (Record drawer) | Capture actual usage. | Select product, quantity, service category, date. |
| Equipment | Reusable asset register. | Add asset, assign, check out/return, record maintenance. |
| Analytics | Usage, purchases, stockouts, expiry and waste insights. | Date / facility / category filters, export. |
| Recommendations | Low-stock, expiry, reorder and surplus recommendations. | Inspect rationale, mark reviewed, create draft action. |
| Resource network | Simulated facility matching. | View possible match and requirements. |
| Settings / Data | Demo configuration and data management. | Reset seed data, export JSON, import supported JSON. |

**Record drawer (v1.1).** Receive, issue/transfer, consumption, return, wastage and adjustment are **one** global **Record** action that opens a single responsive drawer with a type switcher. It renders as a right-hand drawer on tablet and desktop and as a full-height bottom sheet on mobile. These flows therefore do not need separate pages, which removes three routes and keeps one form pattern to build, test and polish. A deep link such as `?record=receive` is optional. Product detail, Inventory and Overview each offer shortcuts that open the drawer pre-filled with the relevant product.

### 9.3 Dashboard content hierarchy

1. Page title and active facility context.
2. Summary cards: total usable stock value (only if costs are available), low-stock products, batches nearing expiry, recorded consumption for selected period.
3. Attention list: stockout risk, expiry risk, unusual consumption change and pending review.
4. Consumption trend chart.
5. Category / department usage breakdown.
6. Recent stock movements.
7. Optional multi-facility sample network card.

Avoid claiming that every dashboard count is a real clinical KPI. Label synthetic values clearly.

## 10. UX and Design System Requirements

### 10.1 Design direction

CareGrid should feel like a professional healthcare operations console: calm, precise, dependable and data-led, with a distinctive, art-directed identity. It must not look like a generic consumer medical app or a stock "AI dashboard" (no purple or blue gradients, glassmorphism, neon glows, or default teal-on-white).

The identity comes from a restrained **ink and azure** base, a warm **rose** accent family and **pale cyan** highlights on dark surfaces, all derived from the reference palette in Section 10.2.

**Principle: colour carries identity in the interface chrome and meaning in status. The two never mix.** Warm rose and cool azure are identity. Red, amber and green mean status and are used for nothing else.

### 10.2 Colour source and adaptation

Reference swatches supplied by the project lead, and how each is used:

| Source swatch | Hex | Role in CareGrid |
|---|---|---|
| Black | `#000018` | **Ink.** Sidebar background, primary text. |
| Ivory | `#D8F0F0` | **Tint.** Selected rows and active filters; text on dark surfaces. |
| Pale Muted Cyan | `#90E0F0` | **Highlight on dark surfaces only.** Active nav marker, focus ring on dark, logo accent. |
| Greyish Azure | `#607890` | **Primary family** (darkened for buttons and text), chart series 1. |
| Cold Grey IV | `#78A8A8` | **Success family** (darkened) and chart series 3 (darkened). |
| Muted Rose | `#9C5460` | **Warm accent.** Chart series 2, tags, empty-state artwork. |
| Light Greyish Rose | `#D8A8A8` | Soft accent fills and illustration (tinted for the Demo pill). |
| Dark Flesh | `#B48478` | Chart series 4; hue basis for Warning. |
| Caput Mortuum | `#603030` | Deep warm accent; Demo pill text; chart series 5. |
| Middle Cadmium Red | `#C03030` | **Critical** status (solid). |
| Deep Red | `#901010` | **Critical** status text on tint; destructive hover. |
| Dark Cadmium Orange | `#E46060` | **Not used in the app.** Too close to Critical. Allowed only in pitch-deck and landing artwork. |

**Adjustments made to the swatches, and why**

1. **Red is reserved for status.** The reference palette is red-dominant, but in an inventory tool red means "stockout, expired, destructive". Red never appears in brand chrome or on primary buttons. The warm identity is carried by rose instead. (Pitch slides and a landing hero may use the full red palette for drama; the product UI may not.)
2. **Base colours are darkened where they carry text or buttons**, to meet WCAG AA. Raw Greyish Azure is only 4.6:1 on white, so the primary button uses `#3A5269` (8.1:1 with white text).
3. **Ivory is lightened for the page background** (`#F3F9F9`) so large areas are not tinted. The original Ivory is kept for selected and hover fills.
4. **One colour is derived rather than sampled: Warning amber.** The palette has no amber or yellow hue, and Warning must be clearly distinguishable from Critical. It is derived from Dark Flesh's warm hue.
5. **Input and control borders are a separate, darker token** (`#7D93A6`, 3.2:1). The soft divider colour (`#C9DADA`, 1.5:1) is decorative only and must never be the only edge of an input or button.

### 10.3 Design tokens

Use **semantic tokens**, never raw hex values in components. Full CSS variables are in Appendix A. Ratios were checked against white unless stated.

| Token | Value | Usage | Contrast |
|---|---|---|---|
| `--cg-bg` | `#F3F9F9` | App background | — |
| `--cg-surface` | `#FFFFFF` | Cards, panels, tables, drawers | — |
| `--cg-tint` | `#D8F0F0` | Selected row, active filter chip | Ink on tint 17.4:1 |
| `--cg-hover` | `#EAF5F5` | Row and item hover | — |
| `--cg-text` | `#000018` | Titles and body | 20.7:1 |
| `--cg-text-secondary` | `#44586C` | Helper text, metadata, placeholders | 7.4:1 (6.9:1 on bg) |
| `--cg-border` | `#C9DADA` | Dividers, card edges (decorative only) | 1.5:1 |
| `--cg-border-strong` | `#7D93A6` | Input, select and button outlines | 3.2:1 |
| `--cg-primary` | `#3A5269` | Primary buttons, links, active controls | White on it 8.1:1 |
| `--cg-primary-hover` | `#2A3D50` | Primary hover / pressed | White on it 11.2:1 |
| `--cg-primary-tint` | `#E4ECF3` | Info background, subtle primary fills | — |
| `--cg-sidebar-bg` | `#000018` | Sidebar and mobile "More" sheet header | — |
| `--cg-sidebar-text` | `#D8F0F0` | Sidebar labels | 17.4:1 on ink |
| `--cg-sidebar-muted` | `#A9C2C8` | Inactive items, section labels | 11.1:1 on ink |
| `--cg-cyan` | `#90E0F0` | Active nav marker, focus ring on dark, logo accent. **Dark surfaces only.** | 13.9:1 on ink |
| `--cg-rose` | `#9C5460` | Tags, chart series 2, artwork | 5.5:1 |
| `--cg-demo-bg` / `--cg-demo-text` | `#F4E4E4` / `#603030` | "Demo data" pill and banner | 8.7:1 |
| `--cg-focus` | `#3A5269` | Focus ring on light surfaces (2px + 2px offset) | 8.1:1 |

Status tokens are in Section 10.4. Chart tokens:

| Series | Token | Value | Notes |
|---|---|---|---|
| 1 | `--cg-chart-1` | `#607890` (azure) | 4.6:1 |
| 2 | `--cg-chart-2` | `#9C5460` (rose) | 5.5:1 |
| 3 | `--cg-chart-3` | `#5E9494` (cold grey, darkened) | 3.4:1 |
| 4 | `--cg-chart-4` | `#B48478` (flesh) | 3.2:1 |
| 5 | `--cg-chart-5` | `#603030` (caput mortuum) | 10.7:1 |
| Grid | `--cg-chart-grid` | `#E2ECEC` | decorative |

Chart rules: never use red, amber or green for non-status series; at most 5 series per chart; always show direct labels or a legend and vary line style or markers so series are not told apart by colour alone; every chart names the event type it shows (Section 18).

### 10.4 Status semantics

Status is always **icon + text label + colour**. Colour alone never communicates a state (WCAG 1.4.1).

| Token set | Solid (icons, bars) | Text on tint | Tint background | Used for |
|---|---|---|---|---|
| **Critical** | `#C03030` (white on it 5.7:1) | `#901010` (7.6:1 on tint) | `#F8E4E4` | Stockout, expired, recalled, destructive confirmation, validation error |
| **Warning** | `#A35F00` (white on it 5.0:1) | `#7A4A00` (6.6:1 on tint) | `#FBEFD6` | Low stock, expiring soon, attention required |
| **Success** | `#2A6767` (white on it 6.5:1) | `#2A6767` (5.5:1 on tint) | `#E1F0EE` | In stock, reconciled, saved successfully |
| **Info** | `#3A5269` | `#3A5269` (6.8:1 on tint) | `#E4ECF3` | Monitor window, simulated, in progress |

| Product state | Badge | Icon |
|---|---|---|
| Out of usable stock | Critical, "Stockout" | octagon-alert |
| Expired | Critical, "Expired" | circle-x |
| Low stock (below reorder point) | Warning, "Low stock" | triangle-alert |
| Expiring soon (within warning window) | Warning, "Expiring soon" | clock-alert |
| Monitor window | Info, "Monitor" | eye |
| Healthy | Success, "In stock" | circle-check |
| Resource match / forecast | Info, "Simulated" or "Estimate" | flask / sparkles |

The persistent **Demo data** pill uses the rose-tinted demo tokens (not a status colour) so it never reads as a warning.

### 10.5 Typography, spacing and density

- **UI and body typeface:** Inter, or the system sans-serif stack if Inter is unavailable. Self-hosted.
- **Optional display typeface:** one serif with character (e.g. Fraunces or Newsreader) for page titles and empty-state headlines only, mirroring the editorial feel of the palette source. Self-hosted, with a safe fallback. If it costs more than 15 minutes, skip it.
- **Scale (px):** 12 caption, 14 table and UI default, 16 body on mobile and all form inputs, 20 section title, 24 page title (mobile), 32 page title (desktop). Strong heading hierarchy and readable labels.
- **Inputs are 16px on mobile** to prevent iOS zoom on focus.
- **Tabular numerals** (`font-variant-numeric: tabular-nums`) for quantities, percentages, dates and currency.
- **Spacing:** 4px base unit. Radius: 6px controls, 8px cards, 12px drawers and sheets, full radius for pills.
- **Depth:** prefer 1px borders over shadows. One soft shadow allowed for drawers, menus and the bottom tab bar.
- **Motion:** 150–200ms transitions for drawers, sheets and hover. No decorative animation. Respect `prefers-reduced-motion`.
- Data tables may be information-dense but must remain readable at 1280px wide.

### 10.6 Component standards

Create reusable components for:

- Application shell with three navigation modes: sidebar, icon rail, bottom tab bar.
- Top bar and facility selector (dropdown on tablet/desktop, bottom sheet on mobile).
- **Responsive drawer:** one component that renders as a right drawer (tablet/desktop) or a full-height bottom sheet (mobile). Used for the Record flows, filters and confirmations.
- Page header and action toolbar.
- Metric card and trend indicator.
- Status badge (Section 10.4) and alert row.
- Data table with sort, filters, empty state and pagination / simple virtualisation if needed, **plus its mobile row-card variant** (Section 10.8).
- Search field, select, date input and quantity input with unit.
- Confirmation dialog (centered modal on desktop, bottom sheet on mobile).
- Form field with label, helper text and inline validation.
- Chart container with title, event-type label, legend and empty state.
- Stock batch row showing batch, expiry, usable quantity and status.
- Movement detail timeline.
- Recommendation card with rationale and data freshness.
- Approval stepper (horizontal on desktop, vertical on mobile) for the simulated resource match.
- Demo-data pill, local-only banner, reset action and export/import controls.

### 10.7 Interaction and accessibility

- All controls are keyboard reachable and have accessible labels.
- Focus states are visible on every interactive element: 2px ring in `--cg-focus` on light surfaces, `--cg-focus-on-dark` on the sidebar.
- Use semantic HTML and correct heading order.
- Tables have descriptive column headings.
- Error messages identify the field and how to correct it.
- Confirm destructive or stock-reducing actions.
- Show success feedback after a completed transaction.
- Prevent double-submit of stock movements (disable the button on submit and use the transaction ID guard in Section 14.2.1).
- Provide empty, loading, error and offline/local states.
- Touch targets are at least 44×44px on mobile and tablet.
- Nothing essential is available only on hover; tooltips are supplements.
- Layouts survive 200% browser zoom without losing content or functionality.
- Text and control contrast follow Sections 10.3 and 10.4 (WCAG AA).

### 10.8 Responsive behaviour: mobile, tablet and desktop

**Priority.** The judging surface is a laptop or projector, so **desktop is the primary design target**. Mobile must be fully usable for the core workflows listed as Tier A below, and gracefully simplified for Tier B. Tablet landscape (≥1024px) is treated as desktop.

**Breakpoints and test sizes**

| Class | Width | Test at | Page padding | Grid |
|---|---|---|---|---|
| Mobile | 0–639px | 390×844 and 360×800 | 16px | 1 column |
| Tablet | 640–1023px | 768×1024 | 24px | 8 columns |
| Desktop | ≥1024px | 1280×800, 1440×900, 1920×1080 | 32px (max content width 1440px, centered) | 12 columns, 24px gutters |

**Mobile Tier A (must be fully usable):** Overview, Inventory and Product detail, Record flows (receive, consume), Recommendations.
**Mobile Tier B (simplified is acceptable; still no broken layout or horizontal page scroll):** Stock movements, Equipment, Analytics, Resource network, Settings / Data.

**App shell by breakpoint**

| Element | Mobile | Tablet | Desktop |
|---|---|---|---|
| Navigation | Bottom tab bar, 64px: **Overview, Inventory, Record (+, centered), Recommendations, More**. "More" opens a sheet with Movements, Equipment, Analytics, Resource network, Settings / Data. | Collapsed icon rail, 72px, labels on tap (expands as an overlay). | Persistent sidebar, 248px, collapsible to 72px. |
| Top bar | 56px. Logo mark, facility pill (tap opens a bottom sheet), search icon, overflow (notifications, role, profile). | 64px. Facility dropdown, search (icon that expands), notifications, role, profile. | 64px. Logo aligned to sidebar, facility dropdown, full search field, notifications, role selector, profile. |
| Demo indicator | Sticky 28px strip under the top bar: "Demo data · saved in this browser only". Not dismissible. | "Demo data" pill in the top bar. | "Demo data" pill in the top bar, full notice in Settings / Data. |
| Record action | Center tab opens a full-height bottom sheet. | Header button opens a 420px right drawer. | Header button opens a 480px right drawer. |
| Page header | Title and one primary action. Date range and filters move into a filter sheet. | Title, description, date range, primary action in one row. | Title, description, date range, primary action in one row. |

**Layout patterns by breakpoint**

| Pattern | Mobile | Tablet | Desktop |
|---|---|---|---|
| Metric cards | 2-up, compact | 2-up | 4-up |
| Data tables | **Row cards** (below). No horizontal page scroll. | Table inside a horizontally scrollable region with a sticky first column. | Full table with sort, filters and pagination. |
| Charts | Height 220px, legend below, tap for tooltip, at most 5 x-axis ticks | Height 260px | Height 320px, legend top-right, hover tooltip |
| Forms | Single column inside a full-height sheet; sticky 56px bottom action bar (Cancel / Confirm) that respects the safe area; `inputMode="decimal"` for quantities; native date input | Single column inside the drawer | Drawer with 2-column grouping for short pairs (quantity + unit, batch + expiry) |
| Confirmations | Bottom sheet | Centered modal | Centered modal, 440px |
| Detail pages | Stacked, with tabs: Overview, Batches, History | Two columns where it fits | Two columns: details (8 cols), timeline (4 cols) |
| Filters | Opened from a "Filter" button into a bottom sheet; active filters shown as chips | Inline toolbar | Inline toolbar |

**Row card (mobile replacement for a table row).** Shows the primary name, the status badge, and 2–3 key fields (usable quantity with unit, expiry date, location). Tapping opens the detail. Essential data is never hidden: **name, usable quantity with unit, and status are always visible.** Row height at least 56px.

**Per-screen behaviour**

| Screen | Mobile (<640) | Tablet (640–1023) | Desktop (≥1024) |
|---|---|---|---|
| Overview | Facility name, then summary cards 2×2, attention list first, trend chart, recent movements as row cards. Category breakdown collapsed under the chart. | Cards 2×2, attention list and chart side by side, movements below. | Cards 4-up, attention list and trend chart side by side, category breakdown and recent movements below, optional network card. |
| Inventory | Search on top, filter sheet, product row cards. Floating "Receive" shortcut opens the Record sheet. | Table with sticky first column, toolbar inline. | Full table with column sort, filters, add product, receive stock. |
| Product detail | Header (name, status, usable total) then tabs: Overview, Batches, History. Batch rows as stacked rows with expiry badge. | Two columns. | Two columns: batches and stock by location left, movement timeline right. |
| Stock movements | Row cards grouped by day; filter sheet. | Scrollable table. | Full table, detail in a side panel. |
| Record drawer | Full-height bottom sheet, type switcher as a horizontally scrollable chip row, sticky action bar. | 420px right drawer. | 480px right drawer. |
| Equipment | Row cards with condition and status badges; detail in a sheet. | Table. | Table with detail drawer. |
| Analytics | Filters in a sheet; charts stacked full width; "Export" hidden (P1). | Charts in a 2-column grid; table below. | 2-column chart grid, event-type labels visible, CSV export. |
| Recommendations | Stacked cards. Recommended quantity and action are visible; the formula inputs sit in an expandable "Why this?" section. | 2-up cards, rationale expanded. | 2-up cards, rationale **expanded by default** so the formula is visible during the demo. |
| Resource network | Match card stacked: sender, then receiver, then a vertical approval stepper and the "Simulated" label. | Horizontal sender → receiver layout. | Horizontal sender → receiver, horizontal approval stepper, rationale and limitations beside it. |
| Settings / Data | Single column list: reset, export, import, demo date. Reset uses a bottom-sheet confirmation. | Single column. | Single column, max width 720px. |

**Responsive rules for implementers**

- Mobile-first CSS: base styles are mobile, enhanced at `min-width: 640px` and `min-width: 1024px`.
- Use `dvh` (not `vh`) for full-height sheets and apply `env(safe-area-inset-*)` to the bottom tab bar and sticky action bars.
- No horizontal page scroll at any width. Wide content scrolls inside its own container.
- Use the same components at every size wherever possible. Switch layouts by breakpoint; do not build separate mobile pages.
- Verify at 390, 768 and 1280 before marking any screen done.


---

# PART IV — FUNCTIONAL REQUIREMENTS

## 11. Functional Requirements and Acceptance Criteria

Priority labels:

- **P0:** Required for the 48-hour demo.
- **P1:** Valuable demo enhancement if time allows.
- **P2:** Future phase; do not implement unless P0 is stable and the project lead approves.

### 11.1 Demo shell and facility context

**FR-001 (P0):** The application shall open into a usable demo environment with seeded synthetic data.  
**Acceptance:** A first-time user can load the app without a backend account and see the dashboard.

**FR-002 (P0):** The user shall be able to switch between seeded facilities.  
**Acceptance:** Switching facility updates the active facility context and all facility-scoped views; the UI indicates the selected facility.

**FR-003 (P0):** The app shall visibly identify itself as a local demo.  
**Acceptance:** A persistent notice or clear indicator states that changes are saved in this browser/device and are not synchronised to a server.

**FR-004 (P1):** The demo shall allow switching between representative user roles.  
**Acceptance:** The visible role changes the demonstration context; documentation states that this is not a security boundary.

### 11.2 Product catalogue

**FR-010 (P0):** A user shall view a searchable product catalogue.  
**Acceptance:** Search works across name, local code, category and brand/manufacturer where available.

**FR-011 (P0):** A user shall create and edit a product.  
**Acceptance:** Required fields are validated; duplicate local codes within the same facility or catalogue scope are warned against.

**FR-012 (P0):** The system shall keep quantity-tracked consumable products separate from individually tracked reusable equipment.  
**Acceptance:** Equipment lives in its own register with asset IDs (Section 12.2) and never appears in quantity stock, consumption or reorder calculations. A medicine, a laboratory consumable and a piece of equipment cannot share the same stock behaviour.

**FR-013 (P0):** Batch-tracked product configuration shall be supported.  
**Acceptance:** The product can require batch/lot and expiry data at receipt.

**FR-014 (P1):** Product catalogue data shall support an external identifier and a normalised product reference.  
**Acceptance:** A facility-specific code can be preserved while a future global mapping field remains optional.

### 11.3 Procurement and receipt

**FR-020 (P0):** A user shall record a purchase / goods receipt.  
**Acceptance:** A saved receipt creates a receipt transaction and increases stock at the selected location by the received quantity.

**FR-021 (P0):** A receipt shall capture product, quantity, unit, location, receipt date and supplier where available.  
**Acceptance:** Required values are validated and shown in the saved receipt detail.

**FR-022 (P0):** Batch-controlled receipts shall capture batch/lot number and expiry date.  
**Acceptance:** The form blocks saving when required batch or expiry data is absent or invalid.

**FR-023 (P0):** A receipt shall capture optional purchase reference, unit cost and total line cost.  
**Acceptance:** If unit cost and quantity are present, total cost is calculated and displayed consistently.

**FR-024 (P1):** The product shall distinguish order quantity from received quantity.  
**Acceptance:** Domain types support partial receipts even if the demo form records only received goods.

### 11.4 Inventory and movements

**FR-030 (P0):** The app shall calculate stock balances from movement history.  
**Acceptance:** The UI does not maintain an independent editable balance that can drift from the ledger.

**FR-031 (P0):** A user shall record an internal issue / transfer between storage locations.  
**Acceptance:** Source quantity decreases and destination quantity increases by the same amount within one logical transaction.

**FR-032 (P0):** A user shall record actual consumption.  
**Acceptance:** The selected department/location balance decreases and the amount appears in the consumption report, not just the issue report.

**FR-033 (P0):** A user shall record a return to a store.  
**Acceptance:** Return quantity is recorded as a new movement; it is not a deletion or edit of the original issue.

**FR-034 (P0):** A user shall record wastage or expiry.  
**Acceptance:** Quantity is removed from usable stock and the reason / event type appears in history.

**FR-035 (P0):** A user shall record a stock-count adjustment.  
**Acceptance:** A reason and counted quantity are required; the system creates an adjustment movement rather than overwriting the balance.

**FR-036 (P0):** The system shall prevent movements greater than available usable stock.  
**Acceptance:** Attempts to issue, consume, transfer or write off more than available stock are blocked with a clear message.

**FR-037 (P0):** Expired and quarantined quantities shall not be included in usable stock.  
**Acceptance:** Available quantity calculations exclude expired, recalled, damaged or quarantined stock where those statuses are represented.

**FR-038 (P1):** Stock selection shall suggest first-expiry-first-out (FEFO) batches.  
**Acceptance:** When multiple usable batches exist, the earliest-expiring eligible batch is surfaced first; the user can inspect and confirm.

### 11.5 Pharmacy demand and laboratory consumption

**FR-040 (P0):** Product and usage reports shall distinguish hospital clinical consumption, pharmacy retail sales / dispensing and laboratory use.  
**Acceptance:** They appear as separately labelled event types and are not merged into one unexplained usage number.

**FR-041 (P0):** The system shall allow a consumption or service event to include an aggregate service / diagnosis category.  
**Acceptance:** No patient identity field is required; category is optional and must be described as facility-recorded data.

**FR-042 (P0):** The application shall not infer disease prevalence from a product name or medicine sale alone.  
**Acceptance:** Condition reporting only uses explicitly recorded approved service / diagnosis categories. Product demand trends are labelled as product demand.

### 11.6 Equipment and assets

**FR-050 (P0):** A user shall create and view equipment assets.  
**Acceptance:** Asset records have a unique asset ID and fields appropriate to reusable equipment.

**FR-051 (P0):** A user shall update an asset's location, assignment and condition.  
**Acceptance:** The history records the change with a timestamp and reason where relevant.

**FR-052 (P1):** A user shall record checkout / return and maintenance events.  
**Acceptance:** Current status and previous events are visible on asset detail.

### 11.7 Analytics and reporting

**FR-060 (P0):** Dashboard cards shall reflect active facility data.  
**Acceptance:** Creating a receipt or movement updates relevant counts after save without a hard refresh.

**FR-061 (P0):** The app shall show top products by actual recorded consumption / sales.  
**Acceptance:** Purchase quantity is not substituted for consumption quantity.

**FR-062 (P0):** The app shall show usage trends over a selected period using seeded synthetic history.  
**Acceptance:** Chart labels, units, time range and data source are visible.

**FR-063 (P0):** The app shall show low-stock and expiry-risk lists.  
**Acceptance:** Each flag links to product, location and batch details where applicable.

**FR-064 (P1):** The app shall show service / diagnosis category distribution when aggregate category data exists.  
**Acceptance:** Empty or insufficient category data is handled clearly; the report does not invent a distribution.

**FR-065 (P1):** Reports shall be exportable to CSV.  
**Acceptance:** Export respects active filters and includes clear column names and units.

### 11.8 Recommendations and AI demonstration

**FR-070 (P0):** The app shall generate explainable low-stock / reorder recommendations from local data.  
**Acceptance:** Each recommendation shows the inputs or rule used, current stock, incoming quantity if modelled, lead time / safety stock assumption and recommended action.

**FR-071 (P0):** The app shall identify batches approaching expiry.  
**Acceptance:** The list shows expiry date, quantity and location and excludes expired stock from transfer suggestions.

**FR-072 (P0):** The app shall label demo forecasts as estimates based on synthetic data.  
**Acceptance:** No output claims to be clinically validated or a guaranteed prediction.

**FR-073 (P1):** The app may provide a natural-language summary generated from computed local metrics.  
**Acceptance:** The summary uses known computed values only and does not pretend to call an external LLM.

**FR-074 (P2):** A secure LLM-powered operations assistant may be added behind a server-side provider adapter.  
**Acceptance:** No secrets are exposed in browser code; answers are permission-scoped and grounded in retrieved platform records.

### 11.9 Resource exchange network demonstration

**FR-080 (P0):** The app shall show at least one synthetic surplus-to-shortage match between two facilities.  
**Acceptance:** The match is based on compatible product identity, usable quantity and non-expired batch data.

**FR-081 (P0):** A resource match shall show its rationale and required approvals.  
**Acceptance:** UI states that it is a simulated recommendation, not a completed transfer.

**FR-082 (P1):** The app shall allow the user to record a mock request / review state.  
**Acceptance:** The local demo state can move between proposed, under review, approved / declined and completed-simulation without any external action.

**FR-083 (P2):** Production transfer workflows shall include organisation verification, legal eligibility, chain of custody, dispatch and receipt confirmation.  
**Acceptance:** Not required for hackathon demo; see Section 20.

### 11.10 Local data management

**FR-090 (P0):** The app shall persist data locally across refresh.  
**Acceptance:** A saved product, receipt or stock movement remains after a browser refresh on the same origin and browser profile.

**FR-091 (P0):** The app shall support reset to seeded demo data.  
**Acceptance:** Reset requires confirmation and restores a known demo state.

**FR-092 (P1):** The app shall export demo data to JSON.  
**Acceptance:** Export includes a schema version and synthetic data records.

**FR-093 (P1):** The app may import a validated CareGrid JSON export.  
**Acceptance:** Invalid schema or unsupported versions are rejected with a useful error; import does not silently corrupt existing data.

---

# PART V — DOMAIN MODEL AND BUSINESS RULES

## 12. Domain Concepts

The frontend should use typed domain entities. UI components must not directly mutate raw database rows.

### 12.1 Organisation and facility

- **Organisation:** The legal or operating entity that owns one or more facilities.
- **Facility:** A hospital, clinic, pharmacy, laboratory or other operating location.
- **InventoryLocation:** A store, pharmacy shelf, lab store, ward, department or other location holding stock.

### 12.2 Product and asset distinction

- **Consumable product:** A quantity-based item depleted through use, dispensing, loss, expiry or other stock events.
- **Medicine:** A consumable product with medicine-specific attributes such as ingredient, strength, dosage form, pack and batch requirements.
- **Laboratory supply:** A consumable such as reagent, test kit or collection item, with relevant units, batch and expiry data.
- **Reusable equipment asset:** An individually identifiable item tracked by asset ID / serial number, location, condition, assignment and maintenance. It is not reduced as quantity consumption.

### 12.3 Procurement and receipt

- **PurchaseRecord:** Captures the intention / commercial purchase reference and supplier / cost context.
- **GoodsReceipt:** Captures what physically arrived and was accepted into a location.
- **GoodsReceiptLine:** Product, received quantity, unit, batch, expiry, unit cost and location.

For the demo, PurchaseRecord and GoodsReceipt may be created through one screen and one save operation. The domain layer must still represent the receipt event distinctly.

### 12.4 Stock ledger

Stock balance is derived from immutable movement events. Do not silently overwrite a balance.

Suggested movement types:

- `RECEIPT` — positive quantity into a location.
- `INTERNAL_TRANSFER_OUT` — negative quantity from a source location.
- `INTERNAL_TRANSFER_IN` — positive quantity into a destination location.
- `CONSUMPTION` — quantity consumed from a location.
- `PHARMACY_SALE` — quantity sold / dispensed from a pharmacy location.
- `RETURN_TO_STORE` — quantity returned to a location after usability checks.
- `WASTAGE` — quantity removed as damaged, spilled, contaminated or otherwise unusable.
- `EXPIRY` — quantity removed because it is expired.
- `ADJUSTMENT_IN` / `ADJUSTMENT_OUT` — stock-count correction with reason.
- `EXTERNAL_TRANSFER_OUT` / `EXTERNAL_TRANSFER_IN` — future inter-facility transfer legs.

A transfer is one logical transaction with linked movement legs. The same quantity must never be counted as both an internal transfer and consumption.

### 12.5 Service / diagnosis category

An optional, non-identifying category attached to a consumption or service summary. It may represent a facility-approved diagnosis group, service line or operational category. It must not contain patient identifiers or free text that may reveal an individual's identity.

### 12.6 Pharmacy sales versus hospital consumption

A retail pharmacy sale is a demand event for the pharmacy. A hospital's internal issue or consumption is a facility operational event. These can contribute to product-demand analytics but must remain separately filterable and labelled. A pharmacy sale does not reveal the patient's diagnosis.

## 13. Suggested TypeScript Domain Types

The exact implementation may adapt to repository patterns, but types should preserve these concepts.

```ts
export type OrganisationType =
  | "HOSPITAL_GROUP"
  | "PHARMACY_GROUP"
  | "INDEPENDENT_PROVIDER"
  | "LAB_NETWORK"
  | "OTHER";

export type FacilityType =
  | "HOSPITAL"
  | "CLINIC"
  | "PHARMACY"
  | "LABORATORY"
  | "PRIMARY_HEALTH_CENTRE";

export type ProductType = "MEDICINE" | "CONSUMABLE" | "LAB_SUPPLY";
export type TrackingMode = "BATCH" | "QUANTITY";
export type EquipmentCondition = "GOOD" | "NEEDS_SERVICE" | "DAMAGED" | "RETIRED";
export type StockMovementType =
  | "RECEIPT"
  | "INTERNAL_TRANSFER_OUT"
  | "INTERNAL_TRANSFER_IN"
  | "CONSUMPTION"
  | "PHARMACY_SALE"
  | "RETURN_TO_STORE"
  | "WASTAGE"
  | "EXPIRY"
  | "ADJUSTMENT_IN"
  | "ADJUSTMENT_OUT";
export type BatchStatus = "ACTIVE" | "QUARANTINED" | "RECALLED" | "EXPIRED";
export type ServiceCategoryType = "DIAGNOSIS_GROUP" | "SERVICE_LINE" | "OPERATIONAL_CATEGORY";

export interface Organisation {
  id: string;
  name: string;
  type: OrganisationType;
  createdAt: string;
  updatedAt: string;
}

export interface Facility {
  id: string;
  organisationId: string;
  name: string;
  type: FacilityType;
  code?: string;
  countryCode: string;
  timezone: string;
  currencyCode: string;
  isDemo: boolean;
}

export interface InventoryLocation {
  id: string;
  facilityId: string;
  name: string;
  type: "CENTRAL_STORE" | "PHARMACY" | "LAB" | "WARD" | "DEPARTMENT" | "OTHER";
  isActive: boolean;
}

export interface Product {
  id: string;
  organisationId?: string;
  facilityId?: string;
  name: string;
  localCode: string;
  productType: ProductType;
  category: string;
  unitOfMeasure: string;
  trackingMode: TrackingMode;
  requiresBatch: boolean;
  requiresExpiry: boolean;
  reorderPoint?: number;
  safetyStock?: number;
  supplierLeadTimeDays?: number;
  averageUnitCost?: number;
  currencyCode?: string;
  active: boolean;
  manufacturer?: string;
  ingredientOrSpecification?: string;
  strength?: string;
  dosageForm?: string;
  packDescription?: string;
  externalIdentifiers?: Record<string, string>;
}

export interface StockBatch {
  id: string;
  facilityId: string;
  productId: string;
  receivedLocationId: string; // where first received; current location is derived from movements
  batchNumber?: string;
  expiryDate?: string;
  status: BatchStatus;
  receivedAt: string;
  unitCost?: number;
  currencyCode?: string;
}

export interface PurchaseRecord {
  id: string;
  facilityId: string;
  supplierId?: string;
  purchaseReference?: string;
  purchasedAt?: string;
  status: "RECORDED" | "PARTIALLY_RECEIVED" | "RECEIVED";
  notes?: string;
}

export interface GoodsReceipt {
  id: string;
  purchaseRecordId?: string;
  facilityId: string;
  locationId: string;
  receivedAt: string;
  receivedByLabel?: string;
  reference?: string;
}

export interface GoodsReceiptLine {
  id: string;
  receiptId: string;
  productId: string;
  batchId?: string;
  receivedQuantity: number;
  unitOfMeasure: string;
  unitCost?: number;
  currencyCode?: string;
}

export interface StockMovement {
  id: string;
  transactionId: string;
  facilityId: string;
  productId: string;
  batchId?: string;
  locationId: string; // the location whose balance this movement changes
  type: StockMovementType;
  quantity: number; // always positive; direction is defined by movement type
  unitOfMeasure: string;
  occurredAt: string;
  sourceLocationId?: string; // informational; transfer legs are linked by transactionId
  destinationLocationId?: string;
  serviceCategoryId?: string;
  reasonCode?: string;
  notes?: string;
  referenceType?: string;
  referenceId?: string;
  createdByLabel?: string;
  isDemo: boolean;
}

export interface EquipmentAsset {
  id: string;
  facilityId: string;
  assetCode: string;
  name: string;
  category: string;
  manufacturer?: string;
  model?: string;
  serialNumber?: string;
  acquiredAt?: string;
  acquisitionCost?: number;
  currencyCode?: string;
  locationId: string;
  assignedDepartment?: string;
  condition: EquipmentCondition;
  status: "AVAILABLE" | "IN_USE" | "UNDER_MAINTENANCE" | "UNAVAILABLE" | "RETIRED";
  nextMaintenanceAt?: string;
  notes?: string;
}

export interface ServiceCategory {
  id: string;
  facilityId: string;
  label: string;
  type: ServiceCategoryType;
  code?: string;
  active: boolean;
}
```

### Type rules

- IDs must be stable strings generated by a single ID utility.
- Store timestamps in ISO 8601 format. Display according to active facility timezone.
- Store dates such as expiry as date-only values (`YYYY-MM-DD`) to avoid timezone shifts.
- Quantity must be a finite number greater than zero for movement inputs; movement direction is determined by type.
- Unit of measure must be stored with transaction lines. Never silently convert packs, units, ml, boxes or test kits.
- Currency must be explicit when costs are stored. Do not sum mixed currencies without conversion data.
- Preserve external / local product identifiers; do not fuzzy-merge products into a shared catalogue automatically.

## 14. Stock Ledger Rules and Calculations

### 14.1 Source of truth

The stock ledger is the source of truth. On-hand balance is calculated from opening demo balance plus movement events for a product, batch and location.

For a location-level balance:

`onHand = openingBalance + receipts + transferIns + returns + adjustmentIns - transferOuts - consumption - sales - wastage - expiry - adjustmentOuts`

The implementation may store a cached balance for performance in a future backend, but the ledger remains authoritative and a reconciliation process must exist.

### 14.2 Usable stock

`usableStock = onHand excluding expired, recalled, quarantined, damaged or otherwise unavailable quantities`

A batch that has passed its expiry date must not be available for issue, use or transfer. The prototype must calculate this relative to the current date, while seeded demo dates should be chosen so the key scenarios remain stable during the hackathon presentation. Provide a controlled demo date or seed configuration if a scenario depends on time.

### 14.2.1 Ledger clarifications (v1.1)

- **Opening stock.** In the demo `openingBalance` is always 0. Seed opening stock as `RECEIPT` movements with `reasonCode: "OPENING_STOCK"`, dated before the earliest history. Do not add an editable opening-balance field.
- **Expiry is derived, not scheduled.** Whether a batch is expired is calculated at read time from `expiryDate` against the app clock (Section 16.4). An expired batch is excluded from usable stock immediately but stays *on hand* until a user records an `EXPIRY` write-off. Do not mutate batch status on a timer.
- **A batch is a product lot, not a place.** Per-location balance is the sum of movements for a `(batchId, locationId)` pair. `StockBatch` therefore has no "current location".
- **Which location a movement changes.** `locationId` is always the location whose balance that movement changes. For a transfer, the OUT leg uses the source location and the IN leg the destination, sharing one `transactionId`.
- **No negative stock, even on double-click.** The availability check and the write happen inside the same database transaction.
- **Double-submit guard.** The form generates a `transactionId` when it opens. The repository rejects a second write with a `transactionId` it has already saved.

### 14.3 Transfer invariants

For an internal transfer:

- Source and destination must belong to the same facility in the demo.
- Product and unit must match.
- Batch is retained when batch tracking applies.
- Source has sufficient usable quantity.
- Sum of transfer-out and transfer-in quantities must reconcile exactly.
- Transfer is not reported as consumption.

### 14.4 Consumption invariants

- Consumption is a separate movement that reduces stock at the location where it was held.
- It must not repeat the earlier store issue decrement.
- It may link to an optional aggregate service category.
- It must reference the product and unit used.
- The system must not require patient identifiers.

### 14.5 FEFO

For batch-controlled products, suggest **first-expiry-first-out** (FEFO): among usable batches, present the batch with the earliest expiry first. The system should not silently select or issue stock without user confirmation. Expired, recalled and quarantined batches are excluded.

### 14.6 Reorder recommendation baseline

For the hackathon demo use a transparent rule-based baseline rather than a trained forecasting model.

Inputs:

- Average daily recorded consumption over a defined historical window.
- Supplier lead time in days (if known; otherwise use a clearly labelled sample assumption).
- Review period / planning horizon.
- Configured safety stock.
- Current usable stock.
- Confirmed incoming quantity, if represented.

Suggested calculation:

`targetStock = averageDailyConsumption × (leadTimeDays + reviewPeriodDays) + safetyStock`

`recommendedOrderQty = max(0, targetStock - usableStock - confirmedIncomingQty)`

The UI must show the inputs and explain that this is a planning estimate. If no meaningful consumption history or lead time exists, show **insufficient data** or a clearly labelled threshold-based warning. Do not show a fabricated percentage-confidence score.

### 14.7 Expiry risk baseline

Flag batches as:

- **Expired:** expiry date is before the active date.
- **Expiring soon:** within a configurable warning window (e.g. 30 days in the demo).
- **Monitor:** within a longer configurable window (e.g. 60–90 days) and with a positive quantity.

These windows are demo defaults and must be configurable later. Do not recommend redistribution merely because a batch is expiring; first check demand, remaining shelf life, regulation, storage and transport time.

### 14.8 Usage / disease analytics

- Rank products by recorded consumption or sales event type.
- Rank service categories only from explicitly recorded category events.
- Do not infer a diagnosis from a medicine, test kit or pharmacy sale.
- Clearly label whether figures refer to purchase, receipt, issue, consumption, dispensing / retail sales or waste.

---

# PART VI — LOCAL-FIRST FRONTEND ARCHITECTURE

## 15. Architecture Overview

Use a layered frontend architecture:

```text
Presentation layer (pages, components, charts, forms)
                    |
                    v
Application services / use cases
                    |
                    v
Domain logic (stock rules, validation, analytics, recommendations)
                    |
                    v
Repository interfaces
             /              \
            v                v
Local IndexedDB adapter    Future HTTP/API adapter
(Current demo)             (Future backend phase)
```

### 15.1 Required separation

- React components render UI and collect input.
- Application services coordinate a user action, validate data and call repositories.
- Domain functions calculate balances, metrics and recommendations.
- Repository interfaces describe what data can be read/written.
- IndexedDB implementation persists the demo.
- A future API implementation can satisfy the same interfaces without changing page components.

Do not put business rules directly inside page components or chart components.

### 15.2 Suggested project structure

Adapt to the existing repository. For a new project, a structure similar to this is recommended:

```text
src/
  app/                         # routes and layouts
  components/
    layout/                    # sidebar, topbar, shell
    ui/                        # reusable primitive components
    data-display/              # tables, metrics, charts, badges
    forms/                     # reusable form controls
  features/
    dashboard/
    inventory/
    procurement/
    stock-movements/
    equipment/
    analytics/
    recommendations/
    resource-network/
    data-management/
  domain/
    entities/
    enums/
    stock/
    forecasting/
    analytics/
    validation/
  services/
    inventory-service.ts
    procurement-service.ts
    equipment-service.ts
    analytics-service.ts
    recommendation-service.ts
  repositories/
    interfaces/
    local/
    http/                      # future; do not implement live backend now
  lib/
    db/
    dates/
    currency/
    ids/
    export/
  data/
    seed/
  styles/
  tests/
```

### 15.3 Service interface examples

```ts
export interface InventoryRepository {
  listProducts(query?: ProductQuery): Promise<Product[]>;
  getProduct(productId: string): Promise<Product | null>;
  saveProduct(product: Product): Promise<void>;
  listMovements(query: MovementQuery): Promise<StockMovement[]>;
  createMovement(command: CreateMovementCommand): Promise<StockMovement[]>;
  getBalances(query: StockBalanceQuery): Promise<StockBalance[]>;
}

export interface ProcurementRepository {
  createReceipt(command: CreateReceiptCommand): Promise<GoodsReceipt>;
  listReceipts(query: ReceiptQuery): Promise<GoodsReceipt[]>;
}
```

The local adapter and future API adapter should both implement these interfaces. Use async methods even when IndexedDB is local so a later network adapter does not force a UI rewrite.

## 16. Local Persistence Requirements

### 16.1 Storage choice

Use IndexedDB for structured records. A lightweight wrapper such as Dexie may be used if the repository does not already have a suitable abstraction.

Do not use `localStorage` as the primary database for the whole application. It may be used only for small UI preferences such as the selected facility or collapsed navigation state.

### 16.2 Persistence boundary

The local database is tied to the browser origin and browser profile on the local device. It is not:

- A file automatically saved to the user's operating-system folders.
- A central database.
- A backup system.
- A secure multi-user store.
- A cross-device sync service.

The user must be told that clearing browser site data can remove the demo records. Provide JSON export for preservation where time allows.

### 16.3 Suggested IndexedDB tables

- `organisations`
- `facilities`
- `locations`
- `products`
- `suppliers`
- `batches`
- `purchaseRecords`
- `goodsReceipts`
- `goodsReceiptLines`
- `stockMovements`
- `equipmentAssets`
- `equipmentEvents` (P1)
- `serviceCategories`
- `recommendationSnapshots` (optional; may be derived instead)
- `networkMatches` (demo fixtures / state)
- `appMetadata` (schema version and seed version)

Add indexes for facility ID, product ID, location ID, batch ID, date and transaction ID as appropriate.

### 16.4 Seed and reset behaviour

- Seed only when the database is empty or when seed version changes under an explicit migration strategy.
- Do not overwrite user-entered demo data on every page load.
- Provide a **Reset demo data** action with a clear warning.
- Reset should restore the exact known scenario used in the judge presentation.
- Include `isDemo` or equivalent metadata on seeded data.
- Store a `demoToday` date in `appMetadata`. All "now" logic (expiry windows, trends, "last 30 days") reads this app clock, which defaults to the real date unless demo mode pins it. Seed dates are generated **relative to `demoToday`** so the scenarios (for example a batch expiring in 21 days) stay true on presentation day. Expose it in Settings / Data as "Demo date" (pin / use today).

### 16.5 Import / export

If implemented:

- Export a versioned JSON envelope.
- Include a schema version and exported timestamp.
- Validate imports before writing.
- Reject unknown major schema versions.
- Never import executable content.
- Confirm before replacing local data.

---

# PART VII — DATA MODEL AND SEED SCENARIO

## 17. Minimum Demo Data Set

Use three fictional facilities to make the network story visible:

1. **Riverside General Hospital** — hospital with high outpatient usage and a shortage risk for selected consumables.
2. **Hillview Community Hospital** — hospital with eligible surplus of one compatible product and a different demand profile.
3. **Northstar Community Pharmacy** — pharmacy with retail sales and medicine demand trends.

The names are fictional and must be labelled as demo data.

### 17.1 Minimum seeded catalogue

Include a small, coherent product set with distinct categories, such as:

- Disposable examination gloves.
- Syringes (with clear size/unit).
- Gauze dressing.
- Oral rehydration salts (medicine product example).
- Paracetamol tablets (medicine product example; no prescribing claims).
- Malaria rapid diagnostic test kits.
- Laboratory reagent example.
- One or two reusable equipment assets (e.g. patient monitor and centrifuge).

Use generic demo products and non-sensitive sample data. Avoid presenting sample quantities as real hospital benchmarks.

### 17.2 Minimum historical records

Seed enough synthetic transaction history to demonstrate:

- A product with regular weekly consumption.
- A product with a seasonal or recent demand increase (clearly simulated).
- A product with an expiry risk.
- A facility with low usable stock.
- A facility with eligible surplus of the same product and unit.
- A pharmacy with retail sales separate from hospital consumption.
- At least two aggregate service categories to illustrate category-level reporting.

### 17.3 Demo consistency checks

Before presenting:

- Recalculate every seeded balance from movement history.
- Confirm transfers balance exactly.
- Confirm expired/quarantined quantities are not usable.
- Confirm each product's unit matches all movements.
- Confirm dashboard totals reconcile with inventory and reports.
- Confirm the recommendation engine has the required inputs.
- Confirm synthetic records are visibly labelled.

---

# PART VIII — ANALYTICS, FORECASTING AND AI

## 18. Analytics Definitions

| Metric | Definition | Caution |
|---|---|---|
| Quantity purchased | Ordered / commercially purchased quantity where recorded. | Does not equal received or used. |
| Quantity received | Quantity physically received and accepted. | This is what increases stock. |
| Quantity issued | Quantity transferred from one internal location to another. | Does not necessarily mean it was used. |
| Quantity consumed | Quantity recorded as actually used. | Use for consumption ranking. |
| Quantity sold / dispensed | Pharmacy retail / dispensing quantity. | Keep separate from hospital clinical consumption. |
| Quantity wasted | Quantity removed for damage, contamination, spillage or other waste reason. | Report reason where recorded. |
| Quantity expired | Quantity removed because expiry date passed. | Exclude from usable stock. |
| Usable stock | Current on-hand quantity in eligible active batches / locations. | Exclude expired, recalled, quarantined and damaged stock. |
| Days of stock on hand | Usable stock divided by average daily consumption. | Undefined or unavailable when consumption is zero / insufficient. |
| Stockout days | Number of days a product had zero usable stock while demand / need was recorded. | Requires reliable date-level data. |
| Inventory turnover | Consumption cost / average inventory value over period (if cost history is reliable). | Do not combine currencies without conversion. |

Every chart must identify the event type it represents. Do not use a vague label such as "usage" if it mixes issues, sales and consumption.

## 19. AI / Intelligence Scope by Phase

### Phase 0: Local transparent rules

The demo should use deterministic calculations and seeded historical transactions. The interface may use the label **CareGrid Intelligence** or **AI-assisted recommendation preview**, but the detail view must explain that results use demo data and baseline rules, not a trained clinical or production forecasting model.

Recommended demo functions:

- Rolling average consumption.
- Low-stock threshold.
- Reorder quantity estimate.
- Expiry-window alerts.
- Difference between current stock and projected need.
- Rule-based surplus / shortage candidate matching.
- Natural-language summary templates using computed metrics.

### Phase 2: Forecasting service

Once real operational data exists:

- Validate and clean historical movement data.
- Account for stockouts (observed consumption may be lower than unmet demand).
- Separate consumption from supply constraints.
- Include supplier lead time and delivery reliability.
- Evaluate baseline methods before more complex models.
- Compare forecast accuracy by product and facility.
- Display data sufficiency and error measures.
- Keep human approval for procurement and transfer decisions.

### Phase 3+: LLM operations assistant

A future assistant may answer questions about authorised facility data. It must:

- Retrieve only records the current user is allowed to access.
- Ground answers in actual platform data and show the supporting time range / source records.
- Distinguish data from inference.
- Avoid diagnosis, prescription or treatment advice.
- Never initiate a purchase or transfer without explicit human approval.
- Run through a secure backend; never embed provider API keys in frontend code.

## 20. Resource Matching Rules

For the demo, match only synthetic products with the same product identity and compatible units. A candidate must have:

- A positive usable quantity above the sender's configured minimum stock / safety buffer.
- Active, non-expired, non-recalled, non-quarantined batch status.
- Product specification and unit compatibility.
- Sufficient remaining shelf life for the hypothetical transport and use window.
- Clear facility and location provenance.

Display the matching rationale. Never describe a match as approved or completed unless a separate approval / fulfilment event exists.

### Production eligibility requirements (future)

Before enabling real transfers, product-specific rules must determine whether transfer is legally permitted. The workflow must consider licensing, product registration, batch authenticity, storage conditions, cold chain, remaining shelf life, recalls, tamper evidence, transport controls, documentation and local medicine distribution rules. Exclude controlled medicines, blood products and other restricted or high-risk categories until a formal regulatory and operational review is completed.

---

# PART IX — FUTURE BACKEND CONTRACT AND INTEGRATION BOUNDARY

## 21. Backend Architecture (Future; Not for Current Demo)

The eventual backend should provide:

- Identity and authentication.
- Server-side role-based access control.
- Organisation and facility tenancy boundaries.
- Product catalogue and master-data management.
- Procurement, goods receipt and stock ledger services.
- Inventory and equipment services.
- Analytics and forecasting jobs.
- Resource request, approval and transfer services.
- Audit logging, notifications and reporting.
- Integrations and data import.

A modular monolith is a reasonable initial backend shape unless scale or integration requirements justify service separation. Avoid premature microservices.

## 22. Suggested Future API Areas

These are design placeholders, not endpoints to implement in the current frontend-only phase.

| Area | Example operations |
|---|---|
| Identity | Sign in, current user, role and facility permissions. |
| Organisations | List organisations, facilities and locations. |
| Products | Search, create, update and map catalogue items. |
| Suppliers | List and maintain suppliers. |
| Procurement | Create purchase record, receive goods, view receipt history. |
| Inventory | Get balances, batches and movement history. |
| Movements | Issue, transfer internally, consume, return, waste and adjust. |
| Equipment | Register assets, assign, maintain and view history. |
| Analytics | Get usage, expiry, cost, stockout and service-category reports. |
| Recommendations | Generate and review reorder / expiry recommendations. |
| Network | Publish availability, request resources, approve and track transfer. |
| Audit | Query user action history. |

Use API DTOs and repository adapters to isolate the UI from future transport changes.

## 23. Integration and Standards Strategy

Future integrations should be additive and preserve the organisation's existing systems where possible.

Potential integrations:

- Hospital Information Systems / EMRs for approved aggregate service data.
- Pharmacy management / point-of-sale systems for sales and dispensing data.
- Laboratory information systems for reagent and test kit consumption.
- Procurement, accounting and enterprise resource planning platforms.
- Supplier catalogues and order / fulfilment systems.
- Barcode and product traceability standards where adopted.

Product matching must use reliable identifiers and human review. Similar product names are not sufficient to establish equivalence. GS1-compatible identifiers, batch / lot, expiry, serial and location data should be considered where applicable and adopted by the relevant participants.

---

# PART X — PRIVACY, SAFETY AND SECURITY

## 24. Privacy Requirements

### Demo

- Use synthetic data only.
- Do not collect real patient information.
- Do not ask users to paste patient records into the demo.
- Do not send locally entered data to a remote service.
- Explain that local data is stored in this browser profile and may be lost if site data is cleared.

### Production

- Apply data minimisation and purpose limitation.
- Store direct patient identifiers only if a documented product requirement and lawful basis justify them; they are not required for the core resource platform.
- Prefer aggregate / de-identified service categories for operational analytics.
- Define retention, deletion, access logging and data-subject processes for applicable jurisdictions.
- Use encryption in transit and at rest.
- Enforce tenant and facility scopes server-side.
- Apply least-privilege role permissions.
- Maintain audit trails for inventory changes and resource transfers.
- Review country-specific legal and regulatory requirements before deployment.

## 25. Security Requirements

- No secrets in client bundle, source maps or public environment variables.
- Validate form inputs at the UI and domain/service layers; repeat validation on backend later.
- Escape user-provided strings in rendered content; do not render raw HTML from data.
- Avoid dangerous dynamic evaluation.
- Protect import routines against malformed or excessively large files.
- Use stable IDs and do not trust IDs from import files without validation.
- Prevent duplicate submissions for stock-changing actions.
- Log transaction identifiers and actor labels in the demo; production must use authenticated actor IDs.
- Do not represent frontend role switching as security.

## 26. Clinical and Operational Safety

- CareGrid is not a medical device or clinical decision support tool in this scope.
- No diagnosis or treatment suggestion is permitted.
- No patient-level clinical recommendation is generated.
- Stock forecasts do not determine what treatment should be given.
- A shortage alert is an operational notice, not an instruction to substitute one medicine for another.
- Human review is required for stock adjustments, procurement, transfers and product eligibility.
- Expired, recalled, damaged and quarantined items cannot be included in usable stock or transfer recommendations.
- Product equivalence, pack conversion and unit conversion must not be guessed.

---

# PART XI — TESTING AND QUALITY

## 27. Required Tests

### Domain unit tests (P0)

- Stock balance calculation by product, location and batch.
- Paired internal transfer reconciliation.
- Consumption distinct from issue.
- Return / waste / expiry movements.
- Prevention of negative usable stock.
- Expired and quarantined batch exclusion.
- Reorder quantity calculation.
- Expiry-window calculation.
- Top-used product calculation based on consumption / sales event type.
- Diagnosis / service category reporting only from explicit category records.

### Workflow tests (P0)

- Receive stock -> inventory balance increases.
- Issue stock -> source decreases and destination increases.
- Consume stock -> destination decreases and consumption report increases.
- Record wastage -> usable stock decreases and waste report increases.
- Add product -> product appears in search and selection lists.
- Change facility -> facility-scoped inventory and dashboard change.
- Refresh page -> local data remains.
- Reset demo -> seed scenario is restored.

### UI checks (P0)

- No broken routes or missing pages.
- Layouts verified at 390, 768 and 1280 widths with no horizontal page scroll.
- All colours come from design tokens; no raw hex values in components.
- Status is never colour-only (icon and text label present).
- Text and control contrast meet the tokens in Section 10.
- Main tables remain readable and responsive.
- Forms show field-level errors.
- Stock-changing actions require confirmation.
- Success / failure feedback is visible.
- Demo-data indicator is visible.

### Manual scenario validation

Run the full judge demo from a clean reset and verify that every number shown reconciles with the seeded movement ledger.

## 28. Performance and Resilience

For the demo:

- Seed data should be small enough for immediate local loading.
- Avoid expensive recalculation on every keystroke; calculate on save or memoise derived data.
- Use pagination or simple filtering for long tables.
- Handle IndexedDB unavailability or read/write errors with a clear error state and fallback guidance; do not silently pretend data was saved.
- Avoid network dependencies for core demo workflows.

For production, further performance, availability, backup, disaster recovery and offline sync requirements must be defined separately.

---

# PART XII — 48-HOUR IMPLEMENTATION PLAN

## 29. Recommended Build Sequence

### Parallel tracks (hour 0 = start of the hackathon)

| Window | Track A — Foundation and logic | Track B — Interface and design |
|---|---|---|
| Hours 0–3 | Types, service interfaces with **stub implementations**, seed fixtures | Tokens into global styles (Appendix A), responsive app shell, base components |
| Hours 3–12 | IndexedDB adapter, ledger, seed and reset, demo clock | Overview, Inventory list and detail, Record drawer against the stubs |
| Hours 12–28 | Movements, analytics, recommendation calculations, domain tests | Movements, Analytics, Recommendations, Equipment screens |
| Hours 28–40 | Resource-match logic, reconciliation checks, swap remaining stubs for real services | Resource network screen, empty and error states, responsive pass at 390 / 768 / 1280 |
| Hours 40–48 | **Feature freeze.** Bug fixes only. Reset-and-run rehearsals (at least twice) on the presenting laptop and one phone. | Same |

Integrate and run the demo path every ~6 hours. The workstreams below describe *what* is built; the table above says *who* and *when*.

### Workstream 0 — Repository and product setup

- Inspect repository and document the actual stack.
- Create the application shell and route structure.
- Establish design tokens, typography, buttons, inputs, tables and status badges.
- Create sample facility and role context.

**Exit:** App runs locally; navigation and base layout are stable.

### Workstream 1 — Data model and persistence

- Define domain types and enums.
- Define repository interfaces.
- Create IndexedDB adapter.
- Add seed scenario and reset utility.
- Add local demo indicator.

**Exit:** Seed data loads once, persists after refresh and can be reset.

### Workstream 2 — Inventory and purchasing

- Product catalogue and product form.
- Inventory list and detail.
- Receive stock form.
- Batch / expiry support.
- Stock ledger and derived balances.

**Exit:** A user can create a product, receive a quantity and see the exact balance and receipt history.

### Workstream 3 — Movements and equipment

- Internal issue / transfer.
- Actual consumption.
- Return, wastage, expiry and adjustment.
- Equipment register and basic assignment / condition.

**Exit:** User can demonstrate stock movement without double-counting and can view an equipment register.

### Workstream 4 — Analytics and recommendations

- Dashboard summary cards.
- Consumption trend and top product ranking.
- Low-stock and expiry alerts.
- Reorder formula and rationale display.
- Service category distribution from explicit synthetic records.

**Exit:** Analytics change when data changes; recommendation reasoning is visible.

### Workstream 5 — Resource network and presentation polish

- Three-facility demo switcher.
- Surplus / shortage match card.
- Approval steps and simulated status only.
- Responsive polish, empty states, validation and demo reset.
- Full presentation rehearsal.

**Exit:** Complete demo story runs from a clean browser profile with reconciled synthetic data.

## 30. Scope Prioritisation if Time Becomes Limited

Protect the following sequence:

1. App shell and design system.
2. Local persistence and seed data.
3. Product catalogue and receive stock.
4. Stock ledger and issue / consumption distinction.
5. Dashboard and analytics that reconcile.
6. Explainable reorder and expiry recommendations.
7. Simulated network match.
8. Equipment register detail, export and additional UI polish.

Do not sacrifice data correctness to add more pages. A smaller application with coherent stock accounting is better than a large UI with contradictory numbers.

---

# PART XIII — DEMONSTRATION SCRIPT AND ACCEPTANCE

## 31. Judge Demonstration Script

### Scenario setup

- Riverside General Hospital has low usable stock of a selected consumable and rising recorded consumption.
- Hillview Community Hospital has eligible surplus of the same product and compatible unit.
- Northstar Community Pharmacy has retail sales data that appears separately from hospital usage.

### Presentation sequence

1. Show the overview dashboard and identify the selected facility.
2. Open Inventory and inspect a product's current batches and balance.
3. Record a receipt and show the new stock movement and balance.
4. Issue a quantity from central store to a department; show the internal transfer.
5. Record actual consumption from the department; show the consumption metric change.
6. Open Analytics and show top consumed products and service-category trends.
7. Open Recommendations and show a low-stock / reorder recommendation with its formula inputs.
8. Show an expiry-risk batch and explain why it is not eligible for transfer.
9. Open Resource Network and show the synthetic match from Hillview to Riverside, along with approval and traceability requirements.
10. Close with impact measures: fewer projected stockout days, reduced excess/expiry exposure and better visibility (all simulated in the demo).

### Required verbal caveats

- All records shown are synthetic.
- The forecast is a demo estimate / deterministic baseline.
- Resource exchange is a simulated recommendation, not a live transaction.
- The system does not diagnose or prescribe.
- The frontend stores data locally; there is no central backend yet.

## 32. Definition of Done — Hackathon Frontend

The demo is ready when:

- [ ] The app launches locally without a backend.
- [ ] Core navigation works.
- [ ] The demo data indicator is visible.
- [ ] Seed data loads reliably and is not duplicated on refresh.
- [ ] User-created records persist in IndexedDB.
- [ ] Reset restores a known scenario.
- [ ] Product catalogue supports create, search and view.
- [ ] Receipt adds stock through a ledger movement.
- [ ] Internal transfer reconciles source and destination.
- [ ] Consumption is separate from issue.
- [ ] Return, wastage, expiry and adjustment paths are available or clearly marked as supported in the demo.
- [ ] Equipment register is present.
- [ ] Analytics accurately reflect movements.
- [ ] Recommendations show their inputs and limitations.
- [ ] Resource match is clearly simulated and approval-aware.
- [ ] No patient-identifiable data or API secret is included.
- [ ] Layout is usable at laptop, tablet and mobile widths (verified at 1280, 768 and 390).
- [ ] Mobile Tier A screens are fully usable at 390px: Overview, Inventory / Product detail, Record (receive, consume), Recommendations.
- [ ] No horizontal page scroll at any tested width.
- [ ] All colours come from the design tokens in Appendix A; no raw hex values in components.
- [ ] Status is shown with icon, label and colour; contrast meets Section 10.
- [ ] Demo data indicator visible at every breakpoint.
- [ ] Demo script has been rehearsed from reset.

## 33. Known Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Too much scope for 48 hours | Incomplete or shallow product | Protect inventory ledger, persistence and analytics first. |
| Inconsistent movement calculations | Dashboard cannot be trusted | Derive balances from movement ledger and test invariants. |
| Data entry is burdensome | Poor adoption | Optimise frequent flows, use defaults and future barcode/import support. |
| Insufficient historical data | Forecast is unreliable | Use transparent baseline, show data sufficiency and label estimates. |
| Condition data inferred from drugs | Misleading health insights | Require explicit aggregate service / diagnosis category. |
| Unsafe transfer matching | Product / patient safety risk | Restrict demo to synthetic simple consumables and require future compliance gates. |
| Local data mistaken for production storage | Data loss / false security expectations | Show local-only notice and offer export / reset. |
| Existing software already holds the data | Duplicate manual work | Future integration and import strategy; position CareGrid as an intelligence and coordination layer. |

## 34. Open Product Decisions

Decisions to make with the product lead, without blocking the initial build:

1. Final brand name and logo (CareGrid is a working name). The palette in Section 10 is the working visual identity.
2. Whether the product catalogue is shared across an organisation or separately configured by facility in the first backend release.
3. Which diagnosis / service category vocabulary to use for the demo and future markets.
4. Which product categories will be exchange-eligible in the first production release.
5. Whether the first commercial pilot targets public facilities, private facilities, pharmacies or a mixed pilot.
6. Which existing facility systems are available for integration in a pilot market.
7. The backend stack, hosting region, data residency and applicable compliance requirements.

## 35. Reference Material

1. Federal Ministry of Health and Social Welfare, Nigeria. *National Health Product Supply Chain Strategy 2.0, 2026–2030.* https://www.health.gov.ng/wp-content/uploads/2026/11/National-Health-Product-Supply-Chain-Strategy-2026-2030.pdf
2. Nigeria National Bureau of Statistics. *National Health Facility Survey 2023* survey catalogue. https://microdata.nigerianstat.gov.ng/index.php/catalog/149
3. The Guardian Nigeria. *Only 35% of sampled Nigerian health facilities have essential drugs – NBS* (December 2024). https://guardian.ng/news/only-35-of-sampled-facilities-have-essential-drugs-nbs/
4. World Health Organization. *Health-care waste* (24 October 2024). https://www.who.int/news-room/fact-sheets/detail/health-care-waste
5. GS1 Nigeria. *Healthcare FAQs: Traceability standards and product identification.* https://gs1ng.org/healthcare-faqs/

---

# APPENDIX A — DESIGN TOKENS (CSS VARIABLES)

Copy into the global stylesheet. Map these to the Tailwind theme (`theme.extend.colors` in v3, or `@theme` in v4) so components use semantic classes such as `bg-surface` and `text-secondary`, never raw hex values.

```css
:root {
  /* Identity (from reference palette) */
  --cg-ink: #000018;
  --cg-ivory: #D8F0F0;
  --cg-cyan: #90E0F0;            /* dark surfaces only */
  --cg-rose: #9C5460;
  --cg-rose-soft: #D8A8A8;
  --cg-caput: #603030;
  --cg-flesh: #B48478;

  /* Surfaces */
  --cg-bg: #F3F9F9;
  --cg-surface: #FFFFFF;
  --cg-tint: #D8F0F0;            /* selected rows, active filters */
  --cg-hover: #EAF5F5;
  --cg-border: #C9DADA;          /* decorative dividers only */
  --cg-border-strong: #7D93A6;   /* inputs and controls (3:1) */

  /* Text */
  --cg-text: #000018;
  --cg-text-secondary: #44586C;
  --cg-text-on-primary: #FFFFFF;

  /* Primary */
  --cg-primary: #3A5269;
  --cg-primary-hover: #2A3D50;
  --cg-primary-tint: #E4ECF3;
  --cg-focus: #3A5269;
  --cg-focus-on-dark: #90E0F0;

  /* Sidebar */
  --cg-sidebar-bg: #000018;
  --cg-sidebar-text: #D8F0F0;
  --cg-sidebar-muted: #A9C2C8;
  --cg-sidebar-marker: #90E0F0;
  --cg-sidebar-hover: rgba(216, 240, 240, 0.08);

  /* Status: solid / text / tint */
  --cg-critical: #C03030;  --cg-critical-text: #901010;  --cg-critical-tint: #F8E4E4;
  --cg-warning:  #A35F00;  --cg-warning-text:  #7A4A00;  --cg-warning-tint:  #FBEFD6;
  --cg-success:  #2A6767;  --cg-success-text:  #2A6767;  --cg-success-tint:  #E1F0EE;
  --cg-info:     #3A5269;  --cg-info-text:     #3A5269;  --cg-info-tint:     #E4ECF3;

  /* Demo indicator (not a status colour) */
  --cg-demo-bg: #F4E4E4;
  --cg-demo-text: #603030;

  /* Charts */
  --cg-chart-1: #607890;
  --cg-chart-2: #9C5460;
  --cg-chart-3: #5E9494;
  --cg-chart-4: #B48478;
  --cg-chart-5: #603030;
  --cg-chart-grid: #E2ECEC;

  /* Shape and spacing */
  --cg-radius-sm: 6px;
  --cg-radius-md: 8px;
  --cg-radius-lg: 12px;
  --cg-space-1: 4px;
  --cg-space-2: 8px;
  --cg-space-3: 12px;
  --cg-space-4: 16px;
  --cg-space-6: 24px;
  --cg-space-8: 32px;

  /* Layout */
  --cg-topbar-h: 64px;
  --cg-topbar-h-mobile: 56px;
  --cg-tabbar-h: 64px;
  --cg-sidebar-w: 248px;
  --cg-sidebar-w-collapsed: 72px;
  --cg-drawer-w-tablet: 420px;
  --cg-drawer-w-desktop: 480px;
}
```

**Breakpoints:** `640px` (tablet starts) and `1024px` (desktop starts). Mobile-first.

---

**End of Engineering PRD.** Any implementation that changes the local-only boundary, exposes real patient data, automates regulated actions or broadens the clinical scope requires explicit product-lead approval and a new version of this specification.
