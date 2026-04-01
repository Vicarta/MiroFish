# MiroFish English Localization Plan

## Goal

Replace the current Chinese-first product surface with English-first behavior for the deployed MiroFish instance exposed through Tailscale.

## Current State

- The frontend does not have an i18n layer or language switch.
- User-facing text is hardcoded directly in Vue templates, client-side logs, alerts, placeholders, and metadata.
- Backend APIs and task/report flows also return Chinese status and error messages that surface in the UI.
- Several backend prompts and report-generation instructions are explicitly Chinese-oriented.

## Scope

### In Scope

- Frontend page titles, labels, placeholders, buttons, badges, empty states, tooltips, alerts, and progress logs.
- Frontend metadata such as `lang`, page title, and meta description.
- Client-side API helper fallback messages that can surface to users.
- Backend API responses and task status messages that are shown in the UI.
- Report-generation and profile-generation prompts where the product currently hardcodes Chinese output.
- Deployment verification on the production-safe Docker runtime and Tailnet URL.

### Out of Scope

- Internal developer comments and code comments.
- Test-only helper scripts and one-off maintenance scripts that do not affect the product surface.
- A full reusable multilingual framework with runtime language switching.

## Execution Plan

### Phase 1. Audit and Baseline

- Identify all frontend files with hardcoded Chinese strings.
- Identify backend API and service files whose messages surface in the UI.
- Keep the first pass focused on product-visible output, not internal comments.

### Phase 2. Frontend English Pass

- Translate all product-visible strings in:
  - landing/home views
  - process and simulation views
  - graph, report, and interaction components
  - client-side alerts, logs, and placeholder text
- Update `frontend/index.html` metadata to English.
- Keep the current structure and component behavior unchanged.

### Phase 3. Backend User-Facing English Pass

- Translate API response messages and task status strings used by the frontend.
- Translate report/progress messages that appear in logs or UI polling flows.
- Update prompts that currently force Chinese output so reports and generated personas default to English.
- Preserve schema/field names and behavioral logic.

### Phase 4. Verification and Deployment

- Search again for remaining Chinese characters in product-visible frontend and backend surfaces.
- Build and redeploy the Docker Compose runtime on the server.
- Verify the Tailnet UI is English on the main screens and that backend health remains green.

## Acceptance Criteria

- The deployed Tailnet UI no longer displays Chinese in the main application flow.
- Graph build, simulation prep, report generation, and interaction flows surface English status and error text.
- HTML metadata and browser language attributes are English.
- Backend health and frontend availability remain unchanged after deployment.

## Risks

- Some generated content may still reflect source-language input if user materials are Chinese.
- Prompt translation can alter tone or output shape; changes must preserve JSON/structured-output constraints.
- Report/log text can come from multiple layers, so verification must include real workflow checks rather than static search alone.
