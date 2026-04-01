# MiroFish Settings Secrets Page Plan

## Goal

Add a dedicated `/settings` page where an operator can enter or replace runtime service credentials without ever exposing already stored secret values in the browser UI.

## Constraints

- Existing secret values must never be returned to the frontend.
- The UI may show only presence state such as "configured" / "not configured".
- The saved settings must survive container restarts and image rebuilds in the Docker Compose deployment.
- Updated settings must be picked up by the backend runtime without requiring a manual container rebuild.

## Desired Operator Flow

1. Open `/settings`.
2. See whether each required credential is configured.
3. Enter new values only for the fields that need to be set or rotated.
4. Save.
5. Receive confirmation that the configuration was updated.
6. Return later and still see only status, never the stored secret value.

## Scope

### In Scope

- Backend API for reading non-secret configuration status.
- Backend API for updating secrets and selected non-secret LLM connection settings.
- Persistent runtime settings storage mounted into the backend container.
- Frontend `/settings` route and form.
- Docker Compose changes required to persist runtime settings.
- Deployment and verification on the existing Tailnet-exposed server.

### Out of Scope

- Full auth or RBAC.
- Encrypting secrets with an external KMS.
- Arbitrary environment-variable editing from the UI.
- Showing masked or partial secret values.

## Technical Approach

### 1. Persistent Runtime Settings Layer

- Introduce a dedicated runtime env file separate from the build-time example config.
- Mount a persistent host directory into the backend container, for example `../data/config`.
- Store operator-managed values in a file such as `/app/backend/runtime-config/settings.env`.

### 2. Backend Configuration Reload

- Extend `Config` to load both the project `.env` and the runtime settings file.
- Add a reload method so the backend can refresh config values after an update.
- Call this reload path before request handling so all workers converge on the latest saved settings.

### 3. Settings API Contract

- `GET /api/settings`
  - Returns:
    - `llm_api_key_configured: boolean`
    - `zep_api_key_configured: boolean`
    - `llm_base_url: string`
    - `llm_model_name: string`
- `PUT /api/settings`
  - Accepts optional fields:
    - `llm_api_key`
    - `zep_api_key`
    - `llm_base_url`
    - `llm_model_name`
  - Empty secret fields mean "leave unchanged".
  - Response returns success metadata and refreshed configured-state booleans, but never the stored values.

### 4. Frontend Page

- Add a dedicated `/settings` view.
- Add a lightweight settings API module.
- Show:
  - LLM API key input
  - Zep API key input
  - LLM base URL input
  - LLM model name input
- Secret inputs always render empty.
- Display configured-state badges instead of masked values.
- Explain that leaving a secret input empty will preserve the currently stored value.

### 5. Navigation

- Add a visible link to `/settings` from the landing page navigation.
- Keep the styling aligned with the current product surface.

## Validation Plan

1. Static checks:
   - Python syntax validation for backend changes.
   - Frontend production build.
2. Behavioral checks:
   - `GET /api/settings` returns booleans and non-secret connection fields only.
   - `PUT /api/settings` persists updates without returning secrets.
   - A follow-up `GET /api/settings` still does not expose secret values.
3. Deployment checks:
   - Docker Compose backend and frontend both become healthy.
   - `/settings` is accessible through the Tailnet URL.

## Risks

- Gunicorn multi-worker behavior can cause stale config if updates only mutate process-local memory; this is why file-backed reload is required.
- Existing services rely on `Config` class attributes, so reload behavior must update those shared values consistently.
- Without authentication, anyone who reaches the UI can edit settings; that remains a deployment-level trust boundary issue.
