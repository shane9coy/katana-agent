# X API Pay-Per-Use Cost Reference (Feb 2026)

## Per-Action Costs

| Action | Endpoint | Cost |
|--------|----------|------|
| Search recent tweets | `GET /2/tweets/search/recent` | $0.005 |
| Check followers | `GET /2/users/:id/followers` | $0.005 |
| Post a tweet (reply) | `POST /2/tweets` | $0.005 |
| Send a DM | `POST /2/dm_conversations/with/:id/messages` | $0.015 |

## Deduplication

Same resource requested twice in a 24-hour UTC window = charged once. Resets midnight UTC.

## Budget Estimation

| Campaign size | ~70% followers | ~30% non-followers | Total cost |
|--------------|---------------|-------------------|------------|
| 50 replies | 35 × $0.025 | 15 × $0.040 | ~$1.48 |
| 100 replies | 70 × $0.025 | 30 × $0.040 | ~$2.95 |
| 500 replies | 350 × $0.025 | 150 × $0.040 | ~$14.75 |

## Polling Overhead

At `polling_interval_seconds=90`: ~40 search calls/hr = ~$0.20/hr idle cost.
