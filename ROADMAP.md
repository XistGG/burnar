# Burnar Roadmap

Planned improvements and known issues for the burnar project.

---

## Planned

### 🎨 Update Color Scheme to Match x157.github.io

Restyle the web UI to match the terminal/hacker aesthetic of
[x157.github.io](https://x157.github.io).

**Current colors** (in `app/static/style.css`):

| Token              | Current Value                   |
|--------------------|---------------------------------|
| `--bg-color`       | `#121212` (dark gray)           |
| `--text-color`     | `#e0e0e0` (light gray)         |
| `--primary-color`  | `#ff3d00` (red-orange)         |
| `--secondary-color`| `#292929` (dark gray)          |
| `--accent-color`   | `#ff9100` (orange)             |
| `--card-bg`        | `rgba(255,255,255,0.05)`       |
| `--border-color`   | `rgba(255,255,255,0.1)`        |

**Target colors** (extracted from x157.github.io):

| Token              | New Value                       | Notes                              |
|--------------------|---------------------------------|------------------------------------|
| `--bg-color`       | `#151515`                       | Slightly darker background         |
| `--text-color`     | `#cccccc`                       | Primary body text                  |
| `--primary-color`  | `#00cc00`                       | Bright green (headings, borders)   |
| `--secondary-color`| `#282828`                       | Code/input backgrounds             |
| `--accent-color`   | `#b5e853`                       | Yellow-green highlight             |
| `--link-color`     | `#ddaadd`                       | Soft lavender links                |
| `--link-hover`     | `#cccc00`                       | Gold on hover                      |
| `--card-bg`        | `rgba(40,40,40,0.8)`           | Darker card background             |
| `--border-color`   | `#00cc00` (dashed)              | Green dashed borders               |

**Tasks:**

- [ ] Update CSS custom properties in `app/static/style.css`
- [ ] Switch font stack to monospace (Verdana → monospace fallback chain)
- [ ] Change heading gradient to solid `#00cc00`
- [ ] Change button gradient to green tones
- [ ] Update link styles (lavender default, gold hover)
- [ ] Use dashed green borders instead of solid subtle ones
- [ ] Add subtle `text-shadow` glow on headings (`rgba(181,232,83,0.1)`)
- [ ] Verify all pages render correctly with new scheme

---

### 🖥️ CLI for Secret Management

Add a command-line interface to inspect and manage the burnar data directory
without needing the web UI.

**Proposed command:** `burnar-cli` (or `python -m app.cli`)

#### Subcommands

| Command                     | Description                                            |
|-----------------------------|--------------------------------------------------------|
| `burnar-cli status`         | Show storage directory path, file count, total size    |
| `burnar-cli list`           | List all secrets: UUID, creation time, remaining TTL   |
| `burnar-cli remove <uuid>`  | Delete a single secret by UUID                         |
| `burnar-cli reset`          | Delete **all** secrets (with confirmation prompt)      |

#### Example Output

```
$ burnar-cli status
Storage path : ./data
Secrets      : 3
Total size   : 12.4 KB

$ burnar-cli list
UUID                                  Created              TTL Remaining
────────────────────────────────────  ───────────────────  ─────────────
a1b2c3d4-e5f6-7890-abcd-ef1234567890  2026-02-16 10:00:05  6d 14h 00m
b2c3d4e5-f6a7-8901-bcde-f12345678901  2026-02-16 12:30:00  6d 16h 30m
c3d4e5f6-a7b8-9012-cdef-123456789012  2026-02-16 15:00:00  6d 19h 00m

$ burnar-cli remove a1b2c3d4-e5f6-7890-abcd-ef1234567890
Removed secret a1b2c3d4-...

$ burnar-cli reset
This will delete ALL 2 secrets. Continue? [y/N] y
All secrets removed.
```

**Tasks:**

- [ ] Create `app/cli.py` with `argparse` or `click`
- [ ] Implement `status` subcommand (reads `data/` dir stats)
- [ ] Implement `list` subcommand (reads file metadata, computes TTL from `cleanup.max_age_seconds`)
- [ ] Implement `remove <uuid>` subcommand (reuses `storage.delete`)
- [ ] Implement `reset` subcommand (iterates + deletes, requires confirmation)
- [ ] Add `[project.scripts]` entry in `pyproject.toml` for `burnar-cli`
- [ ] Add tests for CLI commands

---

## Known Issues

_None currently tracked._

---

## Completed

_No items completed yet._
