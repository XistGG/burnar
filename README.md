# Burnar

Burnar is a secure, ephemeral content sharing application ("Burn After Reading").

## Features

- **Ephemeral Storage**: Content is deleted immediately after viewing.
- **Encryption**: Content seems encrypted at rest.
- **No Database**: Uses file-based storage with locking mechanisms.
- **Dockerized**: Easy to run via Docker.

## Quick Start

### Development

1.  Ensure you have `uv` installed.
2.  Run `bin/dev-start.ps1`.
3.  Access at `http://localhost:8248`.

### Production

Burnar is designed to run behind an Nginx or Apache reverse proxy at a sub-path
(e.g. `https://site.com/burnar/`).  Launch uvicorn with `--root-path /burnar`
and point a `proxy_pass` / `ProxyPass` directive at `127.0.0.1:8248`.

See **[DEPLOYMENT.md](./DEPLOYMENT.md)** for full Nginx/Apache configuration,
systemd/Docker setup, and a security checklist.

> **Troubleshooting:** See [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md) if you encounter startup errors like "Permission denied".

## Limitations

Burnar uses local file locking ([portalocker](https://pypi.org/project/portalocker/))
to guard concurrent access to secrets on disk.  File locks are per-host and do
not synchronize across machines, so **burnar must run on a single server**.
Multi-server or load-balanced deployments would require replacing the storage
backend with a shared store (e.g. Redis, a database).

## License

MIT
