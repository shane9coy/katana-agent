# Enabl3.ai — Self-Improving Voice Agent Pipeline v3

## The 7 Steps

```
STEP 1                    STEP 2                  STEPS 3-4
─────────────────────    ─────────────────────    ─────────────────────
Call ends                Supabase webhook         Agent analyzes
Transcript → row in      fires on INSERT          transcript, writes
conversations table      POSTs to endpoint        rating (1-5) + scores
status: new              Orchestrator wakes       back to same row

        │                        │                        │
        ▼                        ▼                        ▼

┌──────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│ conversations │────▶│ Webhook fires    │────▶│ Agent 2: /review-call │
│              │     │ on INSERT        │     │                      │
│ status: new  │     │ status = 'new'   │     │ Scores 5 dimensions  │
│ transcript   │     │                  │     │ Rates 1-5            │
│ call data    │     └──────────────────┘     │ Logs strengths +     │
│ lead score   │                              │ failures             │
└──────────────┘                              └──────────┬───────────┘
                                                         │
                                              rating ≤ 2 │ rating ≥ 3
                                              ┌──────────┴──────────┐
                                              ▼                     ▼
                                        status: flagged       status: complete
                                              │
                                              ▼
STEP 5 — WEEKLY OPTIMIZATION
──────────────────────────────────────────────────────────────────────
Batch all flagged (rating ≤ 2) + high-performing (rating ≥ 4) calls

Agent 3: /optimize-prompt
  │
  ├── Summarize what went WRONG (from low-rated calls)
  ├── Summarize what went WELL (from high-rated calls)
  │
  ├── Generate 3 candidate script modifications
  │   ├── Candidate 1: targets objection handling gaps
  │   ├── Candidate 2: rewrites discovery flow
  │   └── Candidate 3: adds urgency-based branching
  │
  ├── TOURNAMENT SELECTION
  │   Score each candidate against failure patterns:
  │   ├── Failure coverage (% of patterns addressed)
  │   ├── Preservation score (keeps what works)
  │   ├── Specificity (targeted vs broad changes)
  │   └── Implementation risk
  │
  └── Winner → pending_scripts table (STAGING, not production)

──────────────────────────────────────────────────────────────────────

STEP 6 — HUMAN IN THE LOOP
──────────────────────────────────────────────────────────────────────
Slack notification fires:

  ┌─────────────────────────────────────────────────┐
  │ 📋 New Script Suggestion                         │
  │                                                  │
  │ From: v1.0  →  To: v1.1                          │
  │ Calls Analyzed: 47                               │
  │ Selected: Candidate 3 of 3                       │
  │                                                  │
  │ What Changed:                                    │
  │ Added urgency-based branching for emergency      │
  │ vs routine calls. Addresses 80% of recurring     │
  │ adaptability failures.                           │
  │                                                  │
  │ Why:                                             │
  │ Candidate 3 covers 80% of failure patterns.      │
  │ Preserves rapport flow that scored 8.1 avg.      │
  │ Other candidates only covered 45-65%.            │
  │                                                  │
  │ [✅ Approve]  [❌ Reject]                         │
  └─────────────────────────────────────────────────┘

Human reviews diff, approves or rejects.

──────────────────────────────────────────────────────────────────────

STEP 7 — DEPLOY + GIT
──────────────────────────────────────────────────────────────────────
On approval:
  1. New script inserted into script_versions (active: true)
  2. Previous script deactivated (active: false)
  3. Git commit with version + change summary
  4. All flagged calls marked complete
  5. change_log entry created (full audit trail)
  6. All new calls now use updated script

On rejection:
  1. pending_scripts status → rejected
  2. Reason logged
  3. No changes to production

Rollback available at any time:
  node orchestrator.js --rollback "scores dropped after v1.1"
  → Reverts to previous version
  → Git revert
  → Logged in change_log
──────────────────────────────────────────────────────────────────────

MONTHLY
──────────────────────────────────────────────────────────────────────
End of month:
  1. All completed conversations → conversations_archive_YYYY_MM
  2. Active table cleared for fresh month
  3. Monthly report auto-generated:
     - Total calls, avg rating, rating distribution
     - Score trends across all 5 dimensions
     - Flagged count, optimization cycles run
     - Scripts proposed / approved / rejected
     - Improvement vs previous month
──────────────────────────────────────────────────────────────────────
```

## Files

| File | Purpose |
|------|---------|
| `supabase-schema.sql` | Full database: conversations, script_versions, pending_scripts, optimization_log, change_log, monthly_reports, views, RLS |
| `pipeline-client.js` | All Supabase operations: ingest, analyze, optimize, approve, reject, deploy, rollback, archive |
| `orchestrator.js` | CLI runner with all 7 steps as commands |
| `optimize-prompt-skill.md` | Agent 3 skill: tournament selection with evidence-based scoring |
| `call-agent-skill.md` | Agent 1 skill: sales call handler (from v1) |
| `review-call-skill.md` | Agent 2 skill: call performance analyzer (from v1) |

## Commands

```bash
# Day-to-day: process incoming calls
node orchestrator.js --process          # Batch process new calls
node orchestrator.js --listen           # Real-time listener

# Weekly: optimization cycle
node orchestrator.js --optimize         # Analyze + generate + notify

# Human review
node orchestrator.js --approve SUG-xxx  # Deploy approved script
node orchestrator.js --reject SUG-xxx   # Reject with reason

# Emergency
node orchestrator.js --rollback "reason" # Revert to previous version

# Monthly
node orchestrator.js --archive          # Archive + report

# Dashboard
node orchestrator.js --status           # Pipeline overview
```

## Key Design Decisions

**Why 1-5 rating instead of 1-10?**
Simpler for humans to validate. A call is either bad (1-2), okay (3), or good (4-5). When you see the Supabase dashboard, you instantly know what needs attention.

**Why 3 candidates with tournament selection?**
Single-shot optimization is a gamble. Three candidates with evidence-based scoring means the agent is reasoning about tradeoffs, not just guessing. The selection reasoning becomes documentation for why the script changed.

**Why staging table before production?**
Trust is earned. The first few cycles, humans review every suggestion. Once the team sees consistent quality, you can discuss auto-deploy for low-risk changes. The staging table is the trust-building mechanism.

**Why Slack notification with diff?**
Approval shouldn't require logging into Supabase. The Slack message shows what changed, why, and has approve/reject buttons. Decision happens in 30 seconds, not 10 minutes.

**Why git versioning?**
Rollback safety net. If v1.3 tanks performance, `git revert` gets you back to v1.2 in seconds. The change_log in Supabase is the queryable audit trail; git is the executable rollback.

**Why monthly archiving?**
Active table stays lean (fast queries). Historical data is preserved and queryable. Monthly reports show improvement over time — which is the whole pitch to Enabl3's clients.
