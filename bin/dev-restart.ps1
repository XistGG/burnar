#!/usr/bin/env pwsh
# Copyright (c) 2026 Xist.GG LLC

$ErrorActionPreference = "Stop"

Write-Host "Restarting Burnar..."
./bin/dev-stop.ps1
./bin/dev-start.ps1
