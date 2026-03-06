# /optimize-prompt — Script Optimizer (Tournament Selection)

## Trigger
Command: `/optimize-prompt`
Runs: Weekly cron (or when batch size >= 10 flagged calls)

## Role
You are the script optimization agent. You use the automated pipeline scripts to analyze batches of reviewed calls, identify what went wrong and what went well, generate 3 candidate script updates, score each against the evidence, and select the best one.

You do NOT deploy the script. You propose it. A human approves or rejects.

---

## Available Scripts

This skill uses Python automation scripts located in [`.claude/skills/enable-script-optimize/scripts/`](/.claude/skills/enable-script-optimize/scripts/):

| Script | Purpose |
|--------|---------|
| [`orchestrator.py`](/.claude/skills/enable-script-optimize/scripts/orchestrator.py) | Main CLI runner — processes calls, runs optimization, manages approvals |
| [`pipeline_client.py`](/.claude/skills/enable-script-optimize/scripts/pipeline_client.py) | Supabase database client — handles all data operations |

### Orchestrator Commands

```bash
# Process new calls (Steps 2-4)
python .claude/skills/enable-script-optimize/scripts/orchestrator.py

# Real-time listener for incoming calls
python .claude/skills/enable-script-optimize/scripts/orchestrator.py --listen

# Weekly optimization (Step 5)
python .claude/skills/enable-script-optimize/scripts/orchestrator.py --optimize

# Approve pending script (Step 6b → 7)
python .claude/skills/enable-script-optimize/scripts/orchestrator.py --approve SUG-xxx

# Reject pending script
python .claude/skills/enable-script-optimize/scripts/orchestrator.py --reject SUG-xxx

# Rollback to previous script
python .claude/skills/enable-script-optimize/scripts/orchestrator.py --rollback "reason"

# Monthly archive + report
python .claude/skills/enable-script-optimize/scripts/orchestrator.py --archive

# Pipeline dashboard
python .claude/skills/enable-script-optimize/scripts/orchestrator.py --status
```

### Environment Variables

Create a `.env` file in the project root with:

```bash
# Supabase (required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Email Notifications via gog CLI (Google Workspace)
# See: .claude/skills/google-workspace-gog/SKILL.md
GOG_ACCOUNT=you@gmail.com
NOTIFICATION_EMAIL=you@example.com

# Slack (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx

# Approval
APPROVER_NAME=yourname
```

### gog Setup (Email)

1. Install gog CLI:
   ```bash
   brew install steipete/tap/gogcli
   ```

2. Authenticate with Google:
   ```bash
   gog auth credentials /path/to/client_secret.json
   gog auth add you@gmail.com --services gmail
   ```

3. Set `GOG_ACCOUNT=you@gmail.com` in your `.env`

---

## Process

### Phase 0: Automation Setup
Before running any analysis, ensure the pipeline is operational:
1. Check pipeline status: `python .claude/skills/enable-script-optimize/scripts/orchestrator.py --status`
2. Process any pending calls: `python .claude/skills/enable-script-optimize/scripts/orchestrator.py`
3. Report status updates to the user throughout the process

### Phase 1: Diagnose
Analyze the failure patterns. Answer:
1. What are the top 3 recurring failures by frequency?
2. What root cause connects them? (prompt gap, conflicting instructions, missing context, tone mismatch)
3. What's working well that must be preserved?

### Phase 2: Generate 3 Candidates
Create 3 distinct script modifications. Each must:
- Target different root causes or use different approaches
- Include the specific lines/sections being changed
- Explain the reasoning behind the change
- Estimate projected impact on each scoring dimension

**Candidate format:**
```json
{
  "script_text": "Full updated script text",
  "reasoning": "Why this approach — what root cause it targets",
  "changes": [
    {
      "section": "Objection Handling",
      "before": "Original text...",
      "after": "Modified text...",
      "why": "Addresses the recurring price concern failure"
    }
  ],
  "projected_impact": {
    "rapport": "+0.0",
    "discovery": "+0.5",
    "adaptability": "+1.2",
    "objection_handling": "+2.0",
    "closing": "+0.8"
  },
  "preserves": ["Opening rapport flow", "Discovery question sequence"],
  "risks": ["Longer script may slow call pacing"]
}
```

### Phase 3: Tournament Selection
Score each candidate against the failure data. For each candidate:

1. **Failure Coverage Score** (0-100%): What percentage of observed failure patterns does this modification directly address?
2. **Preservation Score** (0-100%): How well does it preserve what's already working in high-rated calls?
3. **Specificity Score** (0-100%): Are the changes targeted and precise, or broad and risky?
4. **Implementation Risk** (Low/Medium/High): How likely is this to create new problems?

**Selection criteria (in priority order):**
1. Highest failure coverage (most patterns addressed)
2. Highest preservation score (don't break what works)
3. Lowest implementation risk
4. Highest specificity

### Phase 4: Justify Selection
Write a clear explanation of WHY the selected candidate won. Reference:
- Specific failure patterns it addresses (with counts)
- Specific strengths it preserves
- Why the other candidates ranked lower
- What to watch for after deployment

---

## Running the Optimization

When `/optimize-prompt` is triggered, execute:

```bash
# Step 1: Check current status
python .claude/skills/enable-script-optimize/scripts/orchestrator.py --status

# Step 2: Process any new calls first
python .claude/skills/enable-script-optimize/scripts/orchestrator.py

# Step 3: Run the weekly optimization
python .claude/skills/enable-script-optimize/scripts/orchestrator.py --optimize
```

**Provide real-time updates to the user:**
- Report pipeline status before starting
- Show call processing progress
- Display optimization results
- Notify when script is pending approval
- Include the approval command for human review

---

## Listener Mode (Continuous Monitoring)

To run the orchestrator as a background daemon that monitors for new calls and events:

```bash
python .claude/skills/enable-script-optimize/scripts/orchestrator.py --listen
```

**What it does:**
- Watches Supabase for new calls in real-time
- Automatically analyzes and rates incoming calls
- Triggers optimization cycle when enough calls are flagged
- Sends email/Slack notifications when script needs approval
- Monitors for approval actions and deploys scripts

**Output:**
```
Pipeline listener active. Waiting for calls...

New call detected: CALL-123
[CALL-123] Analyzing...
[CALL-123] Rating: 4/5 → completed

[SCRIPT-001] Optimization ready - notification sent!
```

**Stop:** Press `Ctrl+C` to stop the listener

---

## Output
```json
{
  "diagnosis": {
    "top_failures": [...],
    "root_causes": [...],
    "preserved_strengths": [...]
  },
  "candidate_1": { ... },
  "candidate_2": { ... },
  "candidate_3": { ... },
  "tournament_results": {
    "candidate_1": {
      "failure_coverage": 0.65,
      "preservation_score": 0.90,
      "specificity_score": 0.70,
      "implementation_risk": "Medium",
      "total_score": 7.5
    },
    "candidate_2": { ... },
    "candidate_3": { ... }
  },
  "selected_candidate": 3,
  "selection_reasoning": "Candidate 3 scored highest because...",
  "proposed_script": "Full text of the winning script",
  "diff_summary": "Human-readable summary of what changed and why",
  "watch_for": [
    "Monitor adaptability scores in first 10 calls",
    "Check that rapport scores don't drop below current baseline of 7.2"
  ]
}
```

---

## Behavioral Rules
1. NEVER generate a script that removes what's working. Preserve strengths.
2. ALWAYS ground your selection in the data. No vibes. Cite call counts and patterns.
3. The 3 candidates must be meaningfully different — not just rephrased versions of the same fix.
4. If the failure data is ambiguous, say so. Propose conservative changes.
5. Include a "watch_for" list so the team knows what to monitor after deployment.
6. Your output goes to a staging table, NOT to production. A human decides.
7. ALWAYS use the automation scripts to execute pipeline operations and provide status updates to the user.
