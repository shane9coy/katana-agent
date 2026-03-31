# Oracle Agent — Hermes Build Guide

This folder is the Oracle source pack.
Treat it as the canonical build kit for a Hermes-native Oracle companion.

Source pack location:
- `./oracle/` (repo-relative)

Live runtime targets:
- `project-root/SOUL.md`
- `~/.hermes/oracle/*`
- `~/.hermes/skills/oracle/astro-companion/*`

Important design decision:
- Astrovisor.io is a REST API in v1
- It is not configured as an MCP server unless you later build a proper MCP bridge
- `natal-mcp` remains the optional local fallback under `mcp_servers`

---

## Architecture Summary

```text
project-root/
  SOUL.md

~/.hermes/
  config.yaml
  google_token.json
  oracle/
    .env
    .env.example
    user_profile.json
    consent.yaml
    scoring_weights.yaml
    cache/
    reports/
    journal/
  skills/
    oracle/
      astro-companion/
        SKILL.md
        scripts/
          oracle_utils.py
          oracle_astrology.py
          oracle_profile.py
          oracle_scoring.py
          oracle_digest.py
        references/
          operating-model.md
          safety-policy.md
          data-contracts.md
          prompt-recipes.md
        templates/
          daily_brief.txt
          weekly_review.txt
        ui/
          oracle_chart.html
```

---

## Design Principles

- SOUL.md sounds like Oracle: warm, cosmic, poetic, intimate, grounded
- SKILL.md sounds like an operator manual: dry, precise, procedural
- Scripts are boring and deterministic: no personality in code
- Consent rules are explicit and checked before every Google access
- Outputs are poetic but explainable
- Browser visualization is illustrative; Astrovisor remains the preferred calculation engine when available

This separation is what makes the agent feel premium instead of delusional.

---

## Canonical Domain Taxonomy

Use these keys everywhere:

- `communication`
- `relationships`
- `finance`
- `creativity`
- `rest`
- `decisive_action`
- `launches`
- `health`
- `spiritual`

Do not mix singular/plural variants like `relationship` vs `relationships`.
Do not use ambiguous aliases like `action` when you mean `decisive_action`.

---

## Phase 1 — Patch the Seed Files

These files are the source-of-truth pack and should exist in `./oracle/`:

- `SOUL.md`
- `SKILL.md`
- `config.yaml`
- `user_profile.json`
- `consent.yaml`
- `scoring_weights.yaml`
- `.env.example`

What changed from the earlier concept:

1. `config.yaml` no longer treats Astrovisor as an MCP server
2. `SKILL.md` now uses a single canonical domain taxonomy
3. `user_profile.json` aligns with scoring keys
4. `scoring_weights.yaml` aligns with the profile schema
5. `.env.example` exists because the token is consumed by the REST client, not config.yaml

---

## Phase 2 — Build the Runtime Skill Pack

Under `./oracle/astro-companion/` create:

- `scripts/oracle_utils.py`
- `scripts/oracle_astrology.py`
- `scripts/oracle_profile.py`
- `scripts/oracle_scoring.py`
- `scripts/oracle_digest.py`
- `references/operating-model.md`
- `references/safety-policy.md`
- `references/data-contracts.md`
- `references/prompt-recipes.md`
- `templates/daily_brief.txt`
- `templates/weekly_review.txt`
- `ui/oracle_chart.html`

### Script Intent

#### `oracle_utils.py`
Shared boring infrastructure:
- path resolution
- env loading
- minimal YAML parsing
- JSON helpers
- cache helpers
- safe HTTP JSON calls

#### `oracle_astrology.py`
Direct Astrovisor client:
- reads `ASTROVISOR_TOKEN` from env or `~/.hermes/oracle/.env`
- uses `POST /api/solar/calculate` for natal
- uses `POST /api/transits/calculate` for transits
- falls back cleanly when token is missing
- normalizes raw API responses into a stable wrapper
- caches by endpoint + request hash

#### `oracle_profile.py`
Profile and consent manager:
- read/write `~/.hermes/oracle/user_profile.json`
- validate birth data
- geocode location with Nominatim
- resolve timezone from coordinates
- load consent flags

#### `oracle_scoring.py`
Timing engine:
- tag decision objects by domain
- compute support / friction by domain
- output ranked windows with reasons and cautions
- operate even when astrology data is missing by using a neutral fallback band

#### `oracle_digest.py`
Presentation engine:
- daily brief
- weekly brief
- compact one-liner
- terminal dashboard / chart
- graceful fallback when Astrovisor or Google auth is unavailable

---

## Phase 3 — Build the Installer

Create `install_oracle.py` in the source pack root.

Responsibilities:
- copy `SOUL.md` to `project-root/SOUL.md`
- copy seed state files to `~/.hermes/oracle/`
- copy the skill pack to `~/.hermes/skills/oracle/astro-companion/`
- create `cache/`, `reports/`, `journal/`
- install `.env.example`
- optionally create `.env` if missing
- merge the natal MCP snippet into `~/.hermes/config.yaml` safely
- back up config before editing

Important:
- do not inject Astrovisor as MCP
- do not overwrite user secrets
- do not destroy existing files if they already contain user data

---

## Phase 4 — Reference Documents

### `references/operating-model.md`
Define:
- what Oracle does
- what Oracle does not do
- what data it needs
- what outputs it can produce
- what layer is authoritative for what

### `references/safety-policy.md`
Expand the safety rules:
- astrology is advisory, not deterministic
- medical / legal / financial certainty prohibited
- external writes require confirmation
- consent checked before Gmail / Calendar access
- missing data lowers certainty

### `references/data-contracts.md`
Document the schemas for:
- `user_profile.json`
- `decision_object`
- `scored_window`
- `daily_brief`
- normalized Astrovisor response wrapper

### `references/prompt-recipes.md`
Include 5 polished examples in Oracle voice:
1. Morning briefing
2. Pre-meeting timing advice
3. Inbox guidance
4. Relationship guidance
5. Launch timing recommendation

---

## Phase 5 — Templates

### `templates/daily_brief.txt`
The daily reading shell.
Should support:
- cosmic weather
- natal overlay
- aspects
- timing windows
- calendar overlay
- action items

### `templates/weekly_review.txt`
A seven-day outlook shell.
Should support:
- daily headers
- best day for communication
- best day for launches
- best day for money/admin
- best day for love / repair
- best day for rest / reset

---

## Phase 6 — Browser Star Map

`ui/oracle_chart.html` is a self-contained HTML file with no build step.

Requirements:
- Three.js r128 via CDN
- orbit / zoom controls
- starfield
- zodiac wheel
- planet markers
- date/time controls
- event click → time jump
- reading drawer
- copyable share link
- clear note that the browser chart is illustrative and Astrovisor is the preferred engine for final guidance

---

## Phase 7 — Tests

The source pack should include lightweight tests for the deterministic core:

- profile validation
- YAML loading
- scoring penalties and boosts
- astrology cache behavior

These tests can live under `./oracle/tests/`.

Recommended command:

```bash
python3 -m unittest discover ./oracle/tests -v
```

---

## Phase 8 — Install to Live Hermes

Recommended command:

```bash
python3 ./oracle/install_oracle.py \
  --project-root .
```

Expected results:
- `./SOUL.md` exists
- `~/.hermes/oracle/` contains state files and dirs
- `~/.hermes/skills/oracle/astro-companion/` exists
- `~/.hermes/config.yaml` contains a safe natal MCP snippet

---

## Phase 9 — Verify

Run these in order:

```bash
# Profile / consent
python3 ~/.hermes/skills/oracle/astro-companion/scripts/oracle_profile.py show

# Astrology wrapper (will return structured error if token missing)
python3 ~/.hermes/skills/oracle/astro-companion/scripts/oracle_astrology.py natal

# Scoring engine
python3 ~/.hermes/skills/oracle/astro-companion/scripts/oracle_scoring.py --date 2026-03-10

# Daily brief
python3 ~/.hermes/skills/oracle/astro-companion/scripts/oracle_digest.py daily

# Terminal chart
python3 ~/.hermes/skills/oracle/astro-companion/scripts/oracle_digest.py chart

# Browser star map
open ~/.hermes/skills/oracle/astro-companion/ui/oracle_chart.html
```

A clean v1 is allowed to degrade gracefully when:
- `ASTROVISOR_TOKEN` is missing
- Google auth is missing
- Rich is not installed

Graceful degradation means:
- no crash
- clear warning
- structured output that says what is missing

---

## Key Reminders

- SOUL.md = personality
- SKILL.md = operating system
- Scripts = deterministic computation
- `~/.hermes/oracle/*` = durable local state
- Astrovisor.io = primary REST engine for astrology in v1
- natal-mcp = optional local fallback / enhancement
- Google Workspace skill = existing, reuse it
- Browser map = visualization layer, not final truth source
- Consent = explicit and always checked
