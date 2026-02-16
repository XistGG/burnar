#!/usr/bin/env pwsh
# Copyright (c) 2026 Xist.GG LLC

$ErrorActionPreference = "Stop"

$DIST_DIR = "dist"

if (Test-Path $DIST_DIR) {
    Remove-Item -Recurse -Force $DIST_DIR
}
New-Item -ItemType Directory -Force -Path $DIST_DIR | Out-Null

Write-Host "Building distribution in '$DIST_DIR'..."

# Copy files
Copy-Item -Recurse "app" "$DIST_DIR/app"
Copy-Item "pyproject.toml" "$DIST_DIR/"
Copy-Item "README.md" "$DIST_DIR/"
Copy-Item "Dockerfile" "$DIST_DIR/"
Copy-Item "docker-compose.yml" "$DIST_DIR/"

# Create a production start script (Linux)
$PROD_START = @"
#!/bin/bash
# Install dependencies
uv sync --no-cache
# Run uvicorn
uvicorn app.main:app --host 127.0.0.1 --port 8000
"@
Set-Content -Path "$DIST_DIR/start.sh" -Value $PROD_START
# Note: In a real deploy you might use valid certs and not --reload

Write-Host "Distribution ready in '$DIST_DIR'."
Write-Host "To deploy:"
Write-Host "1. Copy contents of '$DIST_DIR' to your server."
Write-Host "2. Ensure Python 3.11 is installed."
Write-Host "3. Run './start.sh' or configure a systemd service."
