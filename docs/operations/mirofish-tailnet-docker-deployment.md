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
- host binds:
  - `127.0.0.1:13000 -> 3000`
  - `127.0.0.1:15001 -> 5001`
- Tailscale Serve:
  - `tailscale serve --bg --https=13000 http://127.0.0.1:13000`

## Why This Layout

The upstream Docker setup publishes `3000` and `5001` directly. For an internal deployment, loopback-only binds are safer:

- the UI remains inaccessible from the public internet;
- Tailscale acts as the only exposure layer;
- the backend API can stay private even if the UI is shared within the tailnet.

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
4. Validate the compose config:

```bash
sudo docker compose -f deploy/docker-compose.tailnet.yml --env-file deploy/.env config
```

5. Start the stack:

```bash
sudo docker compose -f deploy/docker-compose.tailnet.yml --env-file deploy/.env up -d
```

6. Publish the UI only to the tailnet:

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

## Known Limitation In Upstream Image

The upstream Docker image currently starts `npm run dev`, which means:

- Vite dev server for frontend
- Flask debug server for backend

This is acceptable for internal evaluation deployments, but it is not a production-grade runtime. A safer long-term path is to replace it with:

- a built frontend served by nginx
- a backend served by gunicorn
- explicit healthchecks and pinned image versions

## Rollback

```bash
sudo docker compose -f deploy/docker-compose.tailnet.yml --env-file deploy/.env down
sudo tailscale serve --https=13000 off
```
