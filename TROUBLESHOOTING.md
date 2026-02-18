# Troubleshooting Burnar

## Common Issues

### 1. Service Won't Start: "Permission denied: 'data'"

**Symptoms:**
* Service fails to start.
* Logs show: `PermissionError: [Errno 13] Permission denied: 'data'`

**Cause:**
Burnar tries to create a `data/` directory in its working directory to store secrets. The user running the service (e.g., `www-data`) does not have write permissions to the application directory.

**Fix:**
Pre-create the data directory and assign ownership to the service user.

```bash
# 1. Go to your application directory
cd /path/to/burnar

# 2. Create the data directory manually
sudo mkdir -p data

# 3. Give ownership to the service user (usually www-data)
sudo chown -R www-data:www-data data

# 4. Set secure permissions (only owner can read/write)
sudo chmod 700 data

# 5. Restart the service
sudo systemctl restart burnar
```

---

### 2. Service Running locally, but 404/502 via Nginx/Apache

**Symptoms:**
* `curl http://127.0.0.1:8248` works on the server.
* `curl https://site.com/burnar/` returns 404 Not Found or 502 Bad Gateway.

**Cause:**
* **404:** Often caused by missing the trailing slash in the `proxy_pass` directive, or FastAPI not knowing its `root_path`.
* **502:** The reverse proxy cannot connect to the backend (wrong port or backend not running).

**Fixes:**

**Check Nginx/Apache Config:**
Ensure you have the trailing slash at the end of the `proxy_pass` URL to strip the path prefix:
```nginx
# Correct (strips /burnar/)
proxy_pass http://127.0.0.1:8248/;

# Incorrect (passes /burnar/ to backend -> 404)
proxy_pass http://127.0.0.1:8248;
```

**Check FastAPI startup:**
Ensure `uvicorn` is started with `--root-path /burnar` so it generates correct links.

---

### 3. "Internal Server Error" when viewing a secret

**Cause:**
This can happen if file permissions on the `data/` directory are incorrect, or if the server ran out of disk space.

**Fix:**
Check logs for specific Python tracebacks:
```bash
journalctl -u burnar -f
```

---

## Debugging Steps

If you are unsure what is wrong, follow this checklist.

### 1. Check Service Status
Is the backend actually running?
```bash
sudo systemctl status burnar
# OR
docker compose ps
```

### 2. Check Application Logs
Look for Python exceptions or startup errors.
```bash
# Systemd
sudo journalctl -u burnar -f

# Docker
docker compose logs -f
```

### 3. Verify Local Connectivity
Bypass the reverse proxy and talk to uvicorn directly.
```bash
# Check if port is open
ss -tlnp | grep 8248

# Curl the endpoint (should return HTML)
curl -v http://127.0.0.1:8248/
```

### 4. Verify Public Connectivity
Test through the public URL.
```bash
# Headers only
curl -I https://site.com/burnar/

# Static file check (verifies path mapping)
curl -I https://site.com/burnar/static/style.css
```
