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

1.  Copy the application to your server.
2.  Run `bin/deploy.ps1`.

## License

MIT
