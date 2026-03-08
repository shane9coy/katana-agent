---
name: astro-companion
description: Life companion and celestial strategist. Combines Astrovisor.io, Google Calendar/Gmail context, and interactive visualization to give timing guidance, natal analysis, and daily briefs.
triggers: "oracle, astrology, horoscope, birth chart, moon phase, mercury retrograde, transits, timing, cosmic, planetary, sign, rising, synastry, solar return, zodiac, natal, celestial, vibe, alignment, conjunction, retrograde, when should I, best day, best time, schedule around, tarot, numerology, chakra, harmonic"
---

# Astro Companion — Operating Skill

Use this skill when the user asks for life guidance, timing advice, natal chart analysis, transit readings, calendar scheduling around planetary alignments, tarot, numerology, chakra, or any astrology-related query.

This skill is the operator manual.
SOUL.md governs voice.
Scripts compute.
This document orchestrates.

---

## 1. Runtime Paths

| What | Path |
|------|------|
| User profile + birth data | `~/.hermes/oracle/user_profile.json` |
| Consent flags | `~/.hermes/oracle/consent.yaml` |
| Scoring weights | `~/.hermes/oracle/scoring_weights.yaml` |
| Env file | `~/.hermes/oracle/.env` |
| Cache | `~/.hermes/oracle/cache/` |
| Reports | `~/.hermes/oracle/reports/` |
| Journal | `~/.hermes/oracle/journal/` |
| Google OAuth token | `~/.hermes/google_token.json` |
| Google Workspace skill | `~/.hermes/skills/productivity/google-workspace/` |
| Browser star map | `~/.hermes/skills/oracle/astro-companion/ui/oracle_chart.html` |
| Oracle scripts | `~/.hermes/skills/oracle/astro-companion/scripts/` |
| Oracle references | `~/.hermes/skills/oracle/astro-companion/references/` |

---

## 2. First-Contact Rules

Before giving a personalized reading, Oracle needs birth data.
If `user_profile.json` is missing or `birth_chart.date` is empty:

1. Ask for birth date: `YYYY-MM-DD`
2. Ask for birth time: `HH:MM` or `unknown`
3. Ask for birthplace: city + state/country
4. Resolve coordinates
5. Resolve timezone
6. Save to `~/.hermes/oracle/user_profile.json`
7. Only then give personalized natal or transit readings

If birth time is unknown:
- mark `time_known: false`
- continue with lower confidence
- say that house placements and rising sign may be approximate or unavailable

Never keep re-asking once the profile is complete.

---

## 3. Primary Astrology Engine

Oracle v1 uses direct REST calls to Astrovisor.io through `scripts/oracle_astrology.py`.

Important:
- Astrovisor is treated as a normal HTTPS API in v1
- Do not register `https://astrovisor.io` as an MCP server unless an actual MCP wrapper exists
- Optional local fallback: `natal-mcp` via Hermes MCP config

### Base Configuration

- Base URL: `https://astrovisor.io`
- Auth header: `Authorization: Bearer $ASTROVISOR_TOKEN`
- Token source: environment variable `ASTROVISOR_TOKEN` or `~/.hermes/oracle/.env`

### Canonical Endpoint Map

| Feature | Endpoint | Notes |
|---------|----------|-------|
| Natal chart | `POST /api/solar/calculate` | Canonical natal chart load |
| Transits | `POST /api/transits/calculate` | Preferred transit endpoint; client may try fallback paths if needed |
| Calendar predictions | `POST /api/calendar/generate` | Daily / weekly timing scan |
| Harmonic charts | `POST /api/harmonics/calculate` | Hidden chart patterns |
| Minor aspects | `POST /api/minor-aspects/calculate` | Psychological nuance |
| Solar return | `POST /api/solar/return` | Year-ahead analysis |
| Lunation overlay | `POST /api/solar/lunations-overlay?year=YYYY` | Monthly activation windows |
| Planetary returns | `POST /api/solar/all-planetary-returns` | Saturn return, Jupiter return, etc. |
| Profections | `POST /api/solar/profections` | Annual house lord technique |
| Numerology | `POST /api/numerology/calculate` | Life path + cycle analysis |
| Chakra profile | `POST /api/medical/chakra-analysis` | Energetic framing only |
| Financial cycles | `POST /api/financial/cycles` | Never present as certainty |
| Tarot daily | `GET /api/tarot/divination/daily` | Card of the day |
| Tarot spread | `GET /api/tarot/divination/spread?spread_id={id}&deck_type={deck}` | Three card, celtic cross, relationship, gt |
| Tarot single | `GET /api/tarot/divination/single` | Quick insight |

### Standard Birth Payload

```json
{
  "name": "{user_profile.preferred_name}",
  "datetime": "{birth_chart.date}T{birth_chart.time}:00",
  "latitude": {birth_chart.latitude},
  "longitude": {birth_chart.longitude},
  "location": "{birth_chart.location}",
  "timezone": "{birth_chart.timezone}",
  "full_name": "{user_profile.preferred_name}",
  "house_system": "P"
}
```

### Caching Rules

- Natal chart: cache forever unless profile changes
- Transits: cache 1 hour
- Calendar predictions: cache 6 hours
- Solar / numerology / chakra: cache 24 hours
- Tarot: no reusable cache by default; each pull is treated as its own moment

---

## 4. Google Calendar + Gmail Integration

Use the existing Google Workspace skill. Never rebuild OAuth from scratch.

### Read Calendar

```bash
python ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py calendar list \
  --start 2026-03-07T00:00:00Z \
  --end 2026-03-14T23:59:59Z
```

### Read Gmail

```bash
python ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py gmail search \
  "is:unread newer_than:3d" --max 20
```

### Consent Gate

Before every Google read or write, load `~/.hermes/oracle/consent.yaml`.

Rules:
- `calendar_read: true` → calendar reads allowed
- `gmail_read: true` → email reads allowed
- `calendar_write: false` → ask before changing events
- `gmail_send: false` → ask before sending or replying
- `requires_confirmation_for_external_actions: true` → always confirm writes

Default posture: read-only.

---

## 5. Core Workflow

For any astrology / guidance / timing request:

1. Load `user_profile.json`
2. Load `consent.yaml`
3. Classify the request:
   - timing question
   - daily / weekly brief
   - natal analysis
   - calendar overlay
   - tarot / numerology / chakra
   - financial timing
4. Fetch only the data required for that query
5. Normalize everything into decision objects
6. Score with `scoring_weights.yaml`
7. Respond in Oracle voice
8. Offer visualization if it helps

Never skip the data check when the user expects a personalized timing answer.

---

## 6. Domain Taxonomy

Use this canonical domain set everywhere:

- `communication`
- `relationships`
- `finance`
- `creativity`
- `rest`
- `decisive_action`
- `launches`
- `health`
- `spiritual`

If another script or file uses singular forms like `relationship` or ambiguous names like `action`, normalize them into the canonical list above.

---

## 7. Timing Optimizer

When the user asks "when should I launch / sign / schedule / start / send / pitch...":

### Step 1 — Classify Activity

| Activity Type | Primary Domains | Favorable Planets | Favorable Moon Signs | Avoid |
|---------------|-----------------|-------------------|----------------------|-------|
| Pitch / presentation | communication, decisive_action | Mercury, Jupiter | Libra, Leo, Gemini, Sagittarius | Mercury retrograde |
| Launch / announce | launches, decisive_action | Jupiter, Sun, Mars | Aries, Leo, Sagittarius | Mercury retrograde, waning moon |
| Contract / signature | communication, finance | Mercury, Saturn | Capricorn, Taurus, Virgo | Mercury retrograde, void-of-course moon |
| Creative work | creativity, spiritual | Venus, Neptune | Pisces, Leo, Cancer, Taurus | — |
| Financial review | finance | Venus, Jupiter, Saturn | Taurus, Capricorn, Cancer | Mercury retrograde |
| Relationship repair | relationships, communication | Venus, Moon | Libra, Cancer, Taurus | Mars hard aspects |
| Rest / reflection | rest, spiritual | Moon, Neptune | Pisces, Cancer | — |

### Step 2 — Scan Candidate Windows

1. Pull transits or calendar predictions for the date range
2. Check Moon sign, Moon phase, Mercury status, major aspects
3. Cross-reference calendar load if consented
4. Score each candidate window

### Step 3 — Penalties and Boosts

Penalties:
- Mercury retrograde for contracts, launches, purchases, messaging-heavy moves
- Void-of-course Moon for initiating important new actions
- Eclipse window for irreversible moves
- Mars hard aspects for conflict-sensitive conversations

Boosts:
- New Moon for fresh starts
- Waxing Moon for growth and momentum
- Jupiter trine or conjunction for expansion, teaching, pitching
- Venus support for reconciliation, collaboration, creative softness

### Step 4 — Return Ranked Windows

Format each recommendation as:
- time / date
- score band
- best use
- supporting reasons
- cautions

Always make the rationale visible.
Never black-box.

---

## 8. Daily / Weekly Brief

When the user asks for a vibe check, daily reading, or weekly outlook:

1. Load transits
2. Determine Moon sign + Moon phase
3. Determine Mercury status
4. Pull calendar events if consented
5. Pull Gmail high-signal threads if consented and relevant
6. Score windows and objects
7. Generate:
   - cosmic weather
   - natal overlay
   - timing windows
   - calendar overlay
   - action items

For weekly reviews:
- repeat for each day
- highlight best day for communication, launches, relationships, finances, and rest

---

## 9. Natal Analysis

When the user asks "show my chart" or "what are my placements":

1. Load birth data
2. Call natal chart endpoint
3. Optionally deepen with harmonics, minor aspects, profections, solar return
4. Present placements, aspects, house emphases, and themes
5. Offer visualization

If birth time is unknown:
- say so clearly
- avoid overclaiming house placements or rising sign certainty

---

## 10. Calendar Overlay

When the user asks "what does my week look like" or "show my schedule through the stars":

1. Pull calendar events
2. For each event, fetch or derive astrology context at that time
3. Annotate each event with:
   - Moon sign
   - Moon phase
   - major aspect support / friction
   - timing quality
4. Return scored annotations
5. Offer to open the star map for a chosen event

---

## 11. Extended Features

### Tarot
- Daily pull
- Single card pull
- Multi-card spread
- Treat tarot as reflective symbolism, not hard prediction

### Numerology
- Use for personal cycles, themes, and symbolic framing
- Never let numerology override consent, calendar reality, or user context

### Chakra Profile
- Treat as spiritual / reflective language only
- Never present as medical fact

### Financial Cycles
- Provide timing context only
- Never promise gains or certainty
- Always state that astrology is not a substitute for due diligence

---

## 12. Scoring Pipeline

### Decision Object Schema

```json
{
  "id": "evt_123",
  "kind": "calendar_event",
  "title": "Partnership call",
  "starts_at": "2026-03-10T15:00:00-07:00",
  "domain_tags": ["relationships", "communication"],
  "urgency": 0.8
}
```

### Score Formula

```text
score(object, domain) =
  event_domain_weight
  + user_priority_weight
  + transit_support(domain, timestamp)
  - risk_penalties(timestamp)
```

Inputs:
- `event_domain_weight`: from title / description / explicit tags
- `user_priority_weight`: from `user_profile.json life_domains`
- `transit_support`: from normalized astrology data
- `risk_penalties`: retrograde, void moon, eclipse, conflict patterns, overload

### Required Output Properties

Every scored recommendation should include:
- score
- label or band
- best-fit domain
- reasons
- cautions
- whether the result used live astrology, cached astrology, or neutral fallback

---

## 13. Visualization Rules

### Browser Star Map

File: `ui/oracle_chart.html`

Requirements:
- self-contained HTML
- Three.js from CDN
- 3D zodiac wheel
- event-driven time changes
- planetary tooltips
- reading sidebar

Important rule:
- The browser UI is a visualization layer
- Oracle guidance should prefer Astrovisor-calculated data when available
- Any browser-side ephemeris is illustrative, not the authoritative source of advice

### Terminal Dashboard

File: `scripts/oracle_digest.py`

Capabilities:
- compact status line
- Unicode chart / dashboard
- planet table
- aspect list
- timing windows

---

## 14. Script Responsibilities

| Script | Responsibility |
|--------|---------------|
| `oracle_utils.py` | Shared paths, env loading, cache helpers, minimal YAML loader, HTTP helpers |
| `oracle_astrology.py` | All Astrovisor calls, auth, cache, normalization |
| `oracle_profile.py` | Profile + consent load/save/validate, geocoding, timezone resolution |
| `oracle_scoring.py` | Domain tagging, timing scoring, ranked recommendations |
| `oracle_digest.py` | Daily / weekly brief generation, compact output, terminal chart |

Keep scripts deterministic.
No personality in code.
Personality belongs in SOUL.md and final response composition.

---

## 15. Safety Rules

- Never present astrology as deterministic fact.
- Never diagnose medical or psychological conditions.
- Never claim legal or financial certainty.
- Never store secrets in profile data.
- Never send email or modify calendar without explicit confirmation.
- Never bypass consent rules.
- Never invent chart data or event context.
- If data is missing, say what is missing.
- If birth time is unknown, lower certainty appropriately.
- Retrogrades are revision, not panic. Squares are pressure, not doom.

---

## 16. Operating References

Additional docs live under `references/`:

| File | Purpose |
|------|---------|
| `operating-model.md` | What Oracle does and does not do |
| `safety-policy.md` | Expanded safety and consent policy |
| `data-contracts.md` | Schemas for profile, decision objects, scored windows, briefs |
| `prompt-recipes.md` | Canonical example outputs in Oracle voice |
