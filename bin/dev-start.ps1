#!/usr/bin/env pwsh
# Copyright (c) 2026 Xist.GG LLC

$ErrorActionPreference = "Stop"

Write-Host "Starting Burnar Development Environment..."

# Check if docker is running
docker info > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Docker is not running. Attempting to start local uvicorn..."
    if (Get-Command "uv" -ErrorAction SilentlyContinue) {
        uv run uvicorn app.main:app --reload --port 8248
    }
    else {
        Write-Error "Docker is not running and 'uv' is not found. Please install uv or start Docker."
    }
}
else {
    Write-Host "Docker is running. Starting containers..."
    docker-compose up -d --build
    Write-Host "Burnar is running at http://localhost:8248"
}
