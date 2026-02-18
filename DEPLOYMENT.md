# Deployment Guide — Serving Burnar at `/burnar/`

> See [`AGENTS.md`](./AGENTS.md) for project conventions and development environment details.

This guide explains how to add burnar to an **existing** Apache or Nginx virtual
host so that `https://site.com/burnar/` serves the application.

Burnar is a FastAPI/Uvicorn application.  When placed behind a reverse proxy at a
sub-path, two things must happen:

1. **The reverse proxy** must strip (or forward) the `/burnar/` prefix correctly.
2. **FastAPI** must know its own base path so that generated URLs (links, redirects,
   static assets) include `/burnar/`.

---

## 1. Configure FastAPI's `root_path`

FastAPI uses the ASGI `root_path` setting to prefix all generated URLs.  Set it
when launching uvicorn:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8248 --root-path /burnar
```

Or via the `UVICORN_ROOT_PATH` environment variable:

```bash
export UVICORN_ROOT_PATH=/burnar
uvicorn app.main:app --host 127.0.0.1 --port 8248
```

> **Note:** `--root-path` does **not** include a trailing slash.

When `root_path` is set, FastAPI's `request.url_for()` helper automatically
prepends `/burnar` to every route, so generated secret links will look like
`https://site.com/burnar/secret/<uuid>#<key>`.

### Template Sub-path Support

Templates use `url_for()` to generate links. This function automatically respects
the configured `root_path`. Therefore, it is **critical** that `root_path` is
configured correctly as described above. If `root_path` is missing, both the
generated "Share" links AND the internal navigation (CSS, buttons) will be broken
when running at a sub-path.

---

## 2. Nginx Configuration

Add a `location` block to your **existing** `server { }`:

```nginx
server {
    listen 443 ssl;
    server_name site.com;

    # ... existing SSL, root, and other location blocks ...

    # ── Burnar reverse proxy ──────────────────────────────────
    
    # Redirect /burnar -> /burnar/ (enforce trailing slash)
    location = /burnar {
        return 301 /burnar/;
    }

    location /burnar/ {
        proxy_pass http://127.0.0.1:8248/;   # trailing slash strips the prefix
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### How it works

| Client requests                        | Nginx forwards to            |
|----------------------------------------|------------------------------|
| `GET /burnar/`                         | `GET /`                      |
| `GET /burnar/static/style.css`         | `GET /static/style.css`      |
| `POST /burnar/create`                  | `POST /create`               |
| `GET /burnar/secret/<uuid>#<key>`      | `GET /secret/<uuid>`         |

The key detail is the **trailing slash** on `proxy_pass`.  Nginx strips the
matching `/burnar/` prefix before forwarding, so uvicorn sees plain routes.
FastAPI's `root_path` then adds `/burnar` back into any URLs it generates.

### Optional: HTTP → HTTPS redirect

```nginx
server {
    listen 80;
    server_name site.com;
    return 301 https://$host$request_uri;
}
```

---

## 3. Apache Configuration

Enable required modules first:

```bash
sudo a2enmod proxy proxy_http headers
sudo systemctl restart apache2
```

Then add to your **existing** `<VirtualHost>`:

```apache
<VirtualHost *:443>
    ServerName site.com

    # ... existing SSL, DocumentRoot, other config ...

    # ── Burnar reverse proxy ──────────────────────────────────
    ProxyPreserveHost On

    # Redirect /burnar -> /burnar/ (enforce trailing slash)
    RedirectMatch permanent ^/burnar$ /burnar/

    ProxyPass        /burnar/ http://127.0.0.1:8248/
    ProxyPassReverse /burnar/ http://127.0.0.1:8248/

    <Location /burnar/>
        RequestHeader set X-Forwarded-Proto "https"
    </Location>
</VirtualHost>
```

### How it works

`ProxyPass /burnar/ http://127.0.0.1:8248/` strips the `/burnar/` prefix
before forwarding (same trailing-slash behavior as Nginx).
`ProxyPassReverse` rewrites `Location:` headers in responses so redirects
resolve correctly through the proxy.

### Optional: HTTP → HTTPS redirect

```apache
<VirtualHost *:80>
    ServerName site.com
    Redirect permanent / https://site.com/
</VirtualHost>
```

---

## 4. Running Burnar as a Service

### Option A: systemd (recommended for bare-metal)

Create `/etc/systemd/system/burnar.service`:

```ini
[Unit]
Description=Burnar - Burn After Reading
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/burnar
ExecStart=/opt/burnar/.venv/bin/uvicorn app.main:app \
    --host 127.0.0.1 \
    --port 8248 \
    --root-path /burnar
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Create data directory and set permissions
mkdir data
sudo chown www-data:www-data data
sudo chmod 700 data

# Install and start
sudo systemctl daemon-reload
sudo systemctl enable --now burnar

# View logs
sudo journalctl -u burnar -f
```

### Option B: Docker Compose

Update `docker-compose.yml` to pass `root_path`:

```yaml
services:
  burnar:
    build: .
    ports:
      - "127.0.0.1:8248:8248"
    volumes:
      - ./data:/app/data
    command: >
      uv run uvicorn app.main:app
      --host 0.0.0.0
      --port 8248
      --root-path /burnar
    restart: unless-stopped
```

> **Security:** Bind to `127.0.0.1:8248` so only the local reverse proxy can
> reach the container.  Never expose port 8248 to the public internet.

---

## 5. Verifying the Deployment

After starting burnar and configuring your reverse proxy:

```bash
# Health check — should return 200 with HTML
curl -sI https://site.com/burnar/ | head -5

# Static asset — should return 200
curl -sI https://site.com/burnar/static/style.css | head -5

# Create a secret (form post)
curl -s -X POST https://site.com/burnar/create -d 'content=hello'
```

If any of these return `404` or `502`:

- Confirm uvicorn is running on the expected port (`ss -tlnp | grep 8248`).
- Confirm `--root-path /burnar` is set.
- Check the reverse proxy error log (`/var/log/nginx/error.log` or
  `/var/log/apache2/error.log`).
- Verify trailing slashes in `proxy_pass` / `ProxyPass` directives.

---

## 6. Security Checklist

- [ ] **HTTPS only** — Serve burnar exclusively over TLS.
- [ ] **Bind locally** — uvicorn listens on `127.0.0.1`, not `0.0.0.0`.
- [ ] **Firewall** — Port 8248 is not externally reachable.
- [ ] **Data directory** — `./data/` is not under the web docroot.
- [ ] **File permissions** — `./data/` is owned by the service user with `700`.

---

## 7. Updating Burnar

Whenever you update the application code (e.g. `git pull`), you **MUST** restart
the service for changes to take effect:

```bash
sudo systemctl restart burnar
```
