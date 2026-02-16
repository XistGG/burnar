#!/usr/bin/env pwsh
# Copyright (c) 2026 Xist.GG LLC

$ErrorActionPreference = "Stop"

Write-Host "Stopping Burnar Development Environment..."
docker-compose down
Write-Host "Stopped."
