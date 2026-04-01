# MiroFish Tailnet Docker Deployment

## Goal

Розгорнути MiroFish через Docker Compose так, щоб:

- UI не був публічно відкритий;
- доступ до UI був тільки через Tailscale;
- дані зберігалися на хості;
- конфіг був відділений від git.

## Recommended Layout

- app directory: `/home/mirofish/apps/mirofish`
- compose file: `deploy/docker-compose.tailnet.yml`
- env file: `deploy/.env` on the server
- persistent data:
  - `/home/mirofish/apps/mirofish/data/uploads`
  - `/home/mirofish/apps/mirofish/data/logs`
- host binds:
  - `127.0.0.1:13000 -> 80`
  - `127.0.0.1:15001 -> 5001`
- Tailscale Serve:
  - `tailscale serve --bg --https=13000 http://127.0.0.1:13000`

## Runtime Model

This deployment replaces the upstream single dev container with two production-oriented services:

- `frontend`: static Vite build served by nginx
- `backend`: Flask app served by gunicorn

The upstream Docker setup publishes `3000` and `5001` directly and runs `npm run dev`. For an internal deployment, loopback-only binds plus a production runtime are safer:

- the UI remains inaccessible from the public internet;
- Tailscale acts as the only exposure layer;
- the backend API can stay private even if the UI is shared within the tailnet.
- the frontend no longer depends on Vite dev server;
- the backend no longer depends on Flask debug server.

## Required Secrets

Create a runtime `.env` from `deploy/mirofish.tailnet.env.example` and fill:

- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL_NAME`
- `ZEP_API_KEY`

Optional:

- `LLM_BOOST_API_KEY`
- `LLM_BOOST_BASE_URL`
- `LLM_BOOST_MODEL_NAME`

Without valid LLM and Zep credentials, the UI can load but graph build, persona generation, simulation preparation and report generation will not work correctly.

## Deploy Steps

1. Copy deployment files to the server.
2. Create `data/uploads`.
3. Create `.env` with production values and set `chmod 600`.
4. Create persistent directories:

```bash
mkdir -p data/uploads data/logs
```

5. Validate the compose config:

```bash
sudo docker compose -f deploy/docker-compose.tailnet.yml --env-file deploy/.env config
```

6. Build and start the stack:

```bash
sudo docker compose -f deploy/docker-compose.tailnet.yml --env-file deploy/.env up -d --build
```

7. Publish the UI only to the tailnet:

```bash
sudo tailscale serve --bg --https=13000 http://127.0.0.1:13000
```

## Verification

Check container state:

```bash
sudo docker compose -f deploy/docker-compose.tailnet.yml --env-file deploy/.env ps
```

Check backend health:

```bash
curl http://127.0.0.1:15001/health
```

Check local port binds:

```bash
sudo ss -ltnp | grep -E '127.0.0.1:(13000|15001)'
```

Check Tailscale serve config:

```bash
sudo tailscale serve status
```

Expected UI URL:

- `https://<your-tailnet-node>:13000/`

## Why This Is Safer Than Upstream Docker

The upstream Docker image starts `npm run dev`, which means:

- Vite dev server for frontend
- Flask debug server for backend

This deployment replaces that with:

- prebuilt frontend assets served by nginx
- gunicorn for backend
- explicit healthchecks
- split services with clearer failure domains
- loopback-only port publishing for both UI and API

## Rollback

```bash
sudo docker compose -f deploy/docker-compose.tailnet.yml --env-file deploy/.env down
sudo tailscale serve --https=13000 off
```
