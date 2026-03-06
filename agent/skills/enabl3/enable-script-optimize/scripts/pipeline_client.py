"""
pipeline_client.py — 7-Step Self-Improving Voice Agent Pipeline
================================================================
pip install supabase python-dotenv requests
================================================================
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)


# ============================================================
# STEP 1 — INGEST: New call → conversations table
# ============================================================

def ingest_call(call_data: dict) -> Optional[dict]:
    """Save a new call transcript to the conversations table."""
    call_id = f"CALL-{int(time.time() * 1000)}"
    active_script = get_active_script()

    result = supabase.table("conversations").insert({
        "call_id": call_id,
        "status": "new",
        "transcript": call_data["transcript"],
        "call_duration_seconds": call_data.get("duration"),
        "customer_name": call_data.get("customer_name"),
        "customer_phone": call_data.get("customer_phone"),
        "service_type": call_data.get("service_type"),
        "urgency": call_data.get("urgency"),
        "property_type": call_data.get("property_type"),
        "property_age": call_data.get("property_age"),
        "budget_range": call_data.get("budget_range"),
        "decision_maker": call_data.get("decision_maker"),
        "lead_score": call_data.get("lead_score"),
        "call_outcome": call_data.get("call_outcome"),
        "call_notes": call_data.get("call_notes"),
        "script_version": active_script["version_label"],
    }).execute()

    if result.data:
        print(f"[STEP 1] Call ingested: {call_id}")
        return result.data[0]

    print(f"[STEP 1] Ingest failed for {call_id}")
    return None


# ============================================================
# STEP 2 — WEBHOOK HANDLER
# Flask/FastAPI endpoint that Supabase webhook POSTs to
# ============================================================

def create_webhook_handler():
    """
    Returns a handler function for your web framework.
    
    Flask example:
        @app.route('/webhook/new-call', methods=['POST'])
        def handle_webhook():
            return webhook_handler(request.json)
    
    FastAPI example:
        @app.post('/webhook/new-call')
        async def handle_webhook(payload: dict):
            return webhook_handler(payload)
    """
    def handler(payload: dict) -> dict:
        record = payload.get("record", {})
        if not record or record.get("status") != "new":
            return {"skipped": True}

        call_id = record.get("call_id")
        print(f"[STEP 2] Webhook received for {call_id}")
        
        # In production, queue this for async processing
        # For now, process inline
        return {"accepted": True, "call_id": call_id}

    return handler


# ============================================================
# STEPS 3-4 — ANALYZE: Agent scores transcript, writes back
# ============================================================

def analyze_call(call_id: str, analysis: dict) -> Optional[dict]:
    """Save Agent 2's analysis results back to the conversation row."""
    scores = analysis["scores"]
    
    # Composite 1-10 average → 1-5 rating
    composite = (
        scores["rapport"] +
        scores["discovery"] +
        scores["adaptability"] +
        scores["objection_handling"] +
        scores["closing"]
    ) / 5.0

    rating = min(5, max(1, round(composite / 2)))
    should_flag = rating <= 2

    status = "flagged" if should_flag else "complete"
    priority = "High" if rating == 1 else "Medium" if rating == 2 else None

    result = supabase.table("conversations").update({
        "status": status,
        "rating": rating,
        "score_rapport": scores["rapport"],
        "score_discovery": scores["discovery"],
        "score_adaptability": scores["adaptability"],
        "score_objection_handling": scores["objection_handling"],
        "score_closing": scores["closing"],
        "analysis_summary": analysis.get("summary", ""),
        "strengths": analysis.get("strengths", []),
        "failures": analysis.get("failures", []),
        "analyzed_at": datetime.utcnow().isoformat(),
    }).eq("call_id", call_id).execute()

    if result.data:
        row = result.data[0]
        print(f"[STEP 3-4] {call_id} → rating: {rating}/5 → {status}")
        return row

    print(f"[STEP 3-4] Analysis save failed for {call_id}")
    return None


# ============================================================
# STEP 5 — OPTIMIZE: Tournament selection with evidence scoring
# ============================================================

def run_optimization_cycle() -> Optional[dict]:
    """
    Pull flagged + high-performing calls, run Agent 3,
    save winning candidate to pending_scripts (staging).
    """
    opt_id = f"OPT-{int(time.time() * 1000)}"
    current_script = get_active_script()
    version_num = float(current_script["version_label"].replace("v", ""))
    new_version = f"v{version_num + 0.1:.1f}"

    # Get batch
    low_rated, high_rated, all_analyzed = get_optimization_batch()

    if len(low_rated) < 3:
        print(f"[STEP 5] Not enough low-rated calls ({len(low_rated)}/3 minimum)")
        return None

    print(f"[STEP 5] Running optimization cycle {opt_id}")
    print(f"  Low-rated (≤2): {len(low_rated)} calls")
    print(f"  High-rated (≥4): {len(high_rated)} calls")

    # Extract patterns
    failure_patterns = extract_patterns(low_rated, "failures")
    strength_patterns = extract_patterns(high_rated, "strengths")
    recurring_issues = find_recurring_issues(failure_patterns)

    # -----------------------------------------------------------
    # HOOK: Replace with your Katana agent call
    #
    # optimization_result = katana_agent.run_skill("/optimize-prompt", {
    #     "current_script": current_script["script_text"],
    #     "what_went_wrong": failure_patterns,
    #     "what_went_well": strength_patterns,
    #     "low_rated_calls": low_rated,
    #     "high_rated_calls": high_rated,
    # })
    # -----------------------------------------------------------

    # Placeholder (replace with actual agent output)
    optimization_result = {
        "candidate_1": {
            "script_text": "Candidate 1 script...",
            "reasoning": "Focuses on improving objection handling transitions",
            "projected_impact": {"objection_handling": "+1.5", "closing": "+0.8"},
            "failure_coverage": 0.65,
        },
        "candidate_2": {
            "script_text": "Candidate 2 script...",
            "reasoning": "Rewrites discovery questions for better rapport",
            "projected_impact": {"rapport": "+2.0", "discovery": "+1.2"},
            "failure_coverage": 0.45,
        },
        "candidate_3": {
            "script_text": "Candidate 3 script...",
            "reasoning": "Adds urgency-based branching for better adaptability",
            "projected_impact": {"adaptability": "+1.8", "closing": "+1.0"},
            "failure_coverage": 0.80,
        },
        "selected_candidate": 3,
        "selection_reasoning": (
            "Candidate 3 addresses 80% of recurring failure patterns, "
            "specifically the adaptability gaps seen in 12 of 18 flagged calls. "
            "It preserves the discovery flow that scored well in high-rated calls "
            "while adding branching logic for urgency scenarios where the current "
            "script consistently fails."
        ),
        "proposed_script": "Candidate 3 full script text...",
    }

    # Build diff summary
    diff_summary = build_diff_summary(current_script["script_text"], optimization_result)

    # Save to pending_scripts (STAGING)
    suggestion_id = f"SUG-{int(time.time() * 1000)}"
    expires_at = (datetime.utcnow() + timedelta(days=7)).isoformat()

    supabase.table("pending_scripts").insert({
        "suggestion_id": suggestion_id,
        "status": "pending_review",
        "candidate_1": optimization_result["candidate_1"],
        "candidate_2": optimization_result["candidate_2"],
        "candidate_3": optimization_result["candidate_3"],
        "selected_candidate": optimization_result["selected_candidate"],
        "selection_reasoning": optimization_result["selection_reasoning"],
        "proposed_script": optimization_result["proposed_script"],
        "current_version": current_script["version_label"],
        "proposed_version": new_version,
        "diff_summary": diff_summary,
        "calls_analyzed": len(all_analyzed),
        "failure_patterns": failure_patterns,
        "recurring_issues": recurring_issues,
        "period_start": all_analyzed[-1]["call_timestamp"] if all_analyzed else None,
        "period_end": all_analyzed[0]["call_timestamp"] if all_analyzed else None,
        "projected_improvement": optimization_result["candidate_3"]["projected_impact"],
        "expires_at": expires_at,
    }).execute()

    # Save optimization log
    supabase.table("optimization_log").insert({
        "optimization_id": opt_id,
        "calls_analyzed": len(all_analyzed),
        "calls_rated_low": len(low_rated),
        "calls_rated_high": len(high_rated),
        "period_start": all_analyzed[-1]["call_timestamp"] if all_analyzed else None,
        "period_end": all_analyzed[0]["call_timestamp"] if all_analyzed else None,
        "what_went_wrong": failure_patterns,
        "what_went_well": strength_patterns,
        "recurring_patterns": recurring_issues,
        "suggestion_id": suggestion_id,
        "previous_version": current_script["version_label"],
        "proposed_version": new_version,
    }).execute()

    # Audit log
    log_change(
        "script_proposed",
        current_script["version_label"],
        new_version,
        suggestion_id,
        opt_id,
        "system",
        f"Analyzed {len(all_analyzed)} calls. {len(low_rated)} low-rated, {len(high_rated)} high-rated.",
    )

    print(f"[STEP 5] Suggestion {suggestion_id} → pending_review")
    print(f"  Selected: Candidate {optimization_result['selected_candidate']}")

    return {"suggestion_id": suggestion_id, "opt_id": opt_id}


# ============================================================
# STEP 6 — NOTIFY: Slack/email with diff
# ============================================================

# ============================================================
# EMAIL NOTIFICATIONS (via gog CLI)
# ============================================================

def send_email(to_email: str, subject: str, html_body: str) -> Optional[dict]:
    """Send email notification via gog CLI (Google Workspace).
    
    Requires gog CLI to be installed and authenticated.
    See: .claude/skills/google-workspace-gog/SKILL.md
    
    Setup:
      brew install steipete/tap/gogcli
      gog auth add you@gmail.com --services gmail
    
    Set GOG_ACCOUNT env var to default account.
    """
    import subprocess
    
    # Check if gog is available
    try:
        subprocess.run(["which", "gog"], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("[EMAIL] gog CLI not installed - skipping email")
        print("[EMAIL] Install: brew install steipete/tap/gogcli")
        return None
    
    # Build command
    cmd = ["gog", "gmail", "send", f"--to={to_email}", f"--subject={subject}"]
    
    # Add body - strip HTML tags for plain text email
    import re
    plain_body = re.sub('<[^<]+?>', '', html_body)
    plain_body = plain_body.replace('\n', ' ').replace('  ', ' ')
    cmd.extend(["--body", plain_body])
    
    # Set account if specified
    account = os.getenv("GOG_ACCOUNT")
    if account:
        cmd.extend(["--account", account])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"[EMAIL] Sent to {to_email} via gog")
            return {"status": "sent", "to": to_email}
        else:
            print(f"[EMAIL] Failed: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print("[EMAIL] gog command timed out")
        return None
    except Exception as e:
        print(f"[EMAIL] Error: {e}")
        return None


def notify_pending_script(suggestion_id: str) -> Optional[dict]:
    """Send Slack + Email notification with approve/reject details."""
    result = supabase.table("pending_scripts") \
        .select("*") \
        .eq("suggestion_id", suggestion_id) \
        .single() \
        .execute()

    if not result.data:
        print("[STEP 6] Suggestion not found")
        return None

    s = result.data

    # Build Slack payload
    slack_payload = {
        "text": "New script suggestion ready for review",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "📋 New Script Suggestion"},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*From:* {s['current_version']}"},
                    {"type": "mrkdwn", "text": f"*To:* {s['proposed_version']}"},
                    {"type": "mrkdwn", "text": f"*Calls Analyzed:* {s['calls_analyzed']}"},
                    {"type": "mrkdwn", "text": f"*Selected:* Candidate {s['selected_candidate']} of 3"},
                ],
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*What Changed:*\n{s['diff_summary']}"},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Why:*\n{s['selection_reasoning']}"},
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "✅ Approve"},
                        "style": "primary",
                        "action_id": "approve_script",
                        "value": suggestion_id,
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "❌ Reject"},
                        "style": "danger",
                        "action_id": "reject_script",
                        "value": suggestion_id,
                    },
                ],
            },
        ],
    }

    # -----------------------------------------------------------
    # HOOK: Send to Slack
    # webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    # if webhook_url:
    #     requests.post(webhook_url, json=slack_payload)
    # -----------------------------------------------------------

    # Send email notification
    to_email = os.getenv("NOTIFICATION_EMAIL", "")
    if to_email:
        email_html = f"""
        <h2>📋 Script Optimization Ready for Review</h2>
        <p><strong>Suggestion ID:</strong> {suggestion_id}</p>
        <p><strong>From:</strong> {s.get('current_version', 'N/A')}</p>
        <p><strong>To:</strong> {s.get('proposed_version', 'N/A')}</p>
        <p><strong>Calls Analyzed:</strong> {s.get('calls_analyzed', 0)}</p>
        <p><strong>Selected:</strong> Candidate {s.get('selected_candidate', '?')} of 3</p>
        <hr>
        <h3>What Changed:</h3>
        <p>{s.get('diff_summary', 'N/A')}</p>
        <h3>Why:</h3>
        <p>{s.get('selection_reasoning', 'N/A')}</p>
        <hr>
        <h3>Actions:</h3>
        <p>Approve: <code>python orchestrator.py --approve {suggestion_id}</code></p>
        <p>Reject: <code>python orchestrator.py --reject {suggestion_id}</code></p>
        """
        send_email(to_email, f"Script {suggestion_id} - Pending Approval", email_html)

    supabase.table("pending_scripts").update({
        "slack_notified": True,
        "notification_sent_at": datetime.utcnow().isoformat(),
    }).eq("suggestion_id", suggestion_id).execute()

    print(f"[STEP 6] Notification sent for {suggestion_id}")
    return slack_payload


# ============================================================
# STEP 6b — APPROVE / REJECT
# ============================================================

def approve_script(suggestion_id: str, approved_by: str, notes: str = "") -> Optional[dict]:
    """Approve a pending script and deploy it."""
    result = supabase.table("pending_scripts") \
        .select("*") \
        .eq("suggestion_id", suggestion_id) \
        .eq("status", "pending_review") \
        .single() \
        .execute()

    if not result.data:
        print("Suggestion not found or already processed")
        return None

    suggestion = result.data

    # Mark approved
    supabase.table("pending_scripts").update({
        "status": "approved",
        "reviewed_by": approved_by,
        "review_notes": notes,
        "reviewed_at": datetime.utcnow().isoformat(),
    }).eq("suggestion_id", suggestion_id).execute()

    print(f"[STEP 6b] {suggestion_id} approved by {approved_by}")

    # Deploy (Step 7)
    return deploy_script(suggestion, approved_by)


def reject_script(suggestion_id: str, rejected_by: str, reason: str = "") -> None:
    """Reject a pending script."""
    supabase.table("pending_scripts").update({
        "status": "rejected",
        "reviewed_by": rejected_by,
        "review_notes": reason,
        "reviewed_at": datetime.utcnow().isoformat(),
    }).eq("suggestion_id", suggestion_id).execute()

    log_change("script_rejected", None, None, suggestion_id, None, rejected_by, reason)
    print(f"[STEP 6b] {suggestion_id} rejected by {rejected_by}: {reason}")


# ============================================================
# STEP 7 — DEPLOY: Activate new script + git push
# ============================================================

def deploy_script(suggestion: dict, deployed_by: str) -> Optional[dict]:
    """Activate approved script, deactivate old, log everything."""
    # Deactivate current
    supabase.table("script_versions") \
        .update({"active": False}) \
        .eq("active", True) \
        .execute()

    # Insert new version as active
    result = supabase.table("script_versions").insert({
        "version_label": suggestion["proposed_version"],
        "script_text": suggestion["proposed_script"],
        "optimization_id": suggestion["suggestion_id"],
        "change_summary": suggestion["diff_summary"],
        "active": True,
        "approved_by": deployed_by,
        "approved_at": datetime.utcnow().isoformat(),
    }).execute()

    if not result.data:
        print("[STEP 7] Deployment failed")
        return None

    new_version = result.data[0]

    # -----------------------------------------------------------
    # HOOK: Git push
    # import subprocess
    # commit_msg = f"Deploy {suggestion['proposed_version']}: {suggestion['diff_summary']}"
    # subprocess.run(["git", "add", "scripts/"], check=True)
    # subprocess.run(["git", "commit", "-m", commit_msg], check=True)
    # subprocess.run(["git", "push", "origin", "main"], check=True)
    #
    # git_hash = subprocess.run(
    #     ["git", "rev-parse", "HEAD"],
    #     capture_output=True, text=True
    # ).stdout.strip()
    #
    # supabase.table("script_versions").update({
    #     "git_commit_hash": git_hash
    # }).eq("version_label", suggestion["proposed_version"]).execute()
    # -----------------------------------------------------------

    # Mark flagged conversations as complete
    supabase.table("conversations") \
        .update({"status": "complete"}) \
        .eq("status", "flagged") \
        .execute()

    # Audit log
    log_change(
        "script_deployed",
        suggestion["current_version"],
        suggestion["proposed_version"],
        suggestion["suggestion_id"],
        None,
        deployed_by,
        f"Approved and deployed. {suggestion['diff_summary']}",
    )

    print(f"[STEP 7] Script {suggestion['proposed_version']} is now LIVE")
    return new_version


# ============================================================
# ROLLBACK
# ============================================================

def rollback_script(reason: str, rolled_back_by: str) -> Optional[dict]:
    """Revert to the previous script version."""
    versions = supabase.table("script_versions") \
        .select("*") \
        .order("created_at", desc=True) \
        .limit(2) \
        .execute()

    if not versions.data or len(versions.data) < 2:
        print("No previous version to rollback to")
        return None

    current = versions.data[0]
    previous = versions.data[1]

    # Swap active
    supabase.table("script_versions") \
        .update({"active": False}) \
        .eq("version_label", current["version_label"]) \
        .execute()

    supabase.table("script_versions") \
        .update({"active": True}) \
        .eq("version_label", previous["version_label"]) \
        .execute()

    # -----------------------------------------------------------
    # HOOK: git revert
    # if current.get("git_commit_hash"):
    #     subprocess.run(["git", "revert", "--no-commit", current["git_commit_hash"]])
    #     subprocess.run(["git", "commit", "-m", f"Rollback {current['version_label']}"])
    #     subprocess.run(["git", "push", "origin", "main"])
    # -----------------------------------------------------------

    log_change(
        "script_rolled_back",
        current["version_label"],
        previous["version_label"],
        None,
        None,
        rolled_back_by,
        reason,
    )

    print(f"[ROLLBACK] {current['version_label']} → {previous['version_label']}")
    print(f"  Reason: {reason}")
    return previous


# ============================================================
# MONTHLY ARCHIVE
# ============================================================

def archive_month(year_month: str = None) -> bool:
    """Move completed conversations to archive table, generate report."""
    if not year_month:
        now = datetime.utcnow()
        year_month = f"{now.year}-{now.month:02d}"

    table_id = year_month.replace("-", "_")

    # Create archive table
    try:
        supabase.rpc("create_monthly_archive", {"year_month": year_month}).execute()
    except Exception as e:
        print(f"Archive table creation failed: {e}")
        return False

    # Get completed conversations for the month
    start_date = f"{year_month}-01"
    end_date_obj = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=32)
    end_date = end_date_obj.replace(day=1).strftime("%Y-%m-%d")

    to_archive = supabase.table("conversations") \
        .select("*") \
        .eq("status", "complete") \
        .gte("call_timestamp", start_date) \
        .lt("call_timestamp", end_date) \
        .execute()

    if not to_archive.data:
        print(f"No conversations to archive for {year_month}")
        return False

    calls = to_archive.data

    # Insert into archive
    supabase.table(f"conversations_archive_{table_id}").insert(calls).execute()

    # Delete from active table
    call_ids = [c["call_id"] for c in calls]
    supabase.table("conversations") \
        .delete() \
        .in_("call_id", call_ids) \
        .execute()

    # Generate monthly report
    generate_monthly_report(year_month, calls)

    print(f"Archived {len(calls)} conversations for {year_month}")
    return True


def generate_monthly_report(year_month: str, calls: list) -> None:
    """Auto-generate monthly summary stats."""
    rated = [c for c in calls if c.get("rating") is not None]

    def avg(field):
        vals = [c[field] for c in rated if c.get(field) is not None]
        return round(sum(vals) / len(vals), 2) if vals else None

    # Rating distribution
    distribution = {str(i): 0 for i in range(1, 6)}
    for c in rated:
        distribution[str(c["rating"])] = distribution.get(str(c["rating"]), 0) + 1

    # Previous month comparison
    prev_date = datetime.strptime(f"{year_month}-01", "%Y-%m-%d") - timedelta(days=1)
    prev_month = f"{prev_date.year}-{prev_date.month:02d}"

    prev_report = supabase.table("monthly_reports") \
        .select("avg_rating") \
        .eq("month", prev_month) \
        .execute()

    current_avg = avg("rating")
    improvement = None
    if prev_report.data and current_avg:
        prev_avg = prev_report.data[0].get("avg_rating")
        if prev_avg:
            improvement = round(current_avg - float(prev_avg), 2)

    supabase.table("monthly_reports").insert({
        "month": year_month,
        "total_calls": len(calls),
        "avg_rating": current_avg,
        "rating_distribution": distribution,
        "avg_rapport": avg("score_rapport"),
        "avg_discovery": avg("score_discovery"),
        "avg_adaptability": avg("score_adaptability"),
        "avg_objection_handling": avg("score_objection_handling"),
        "avg_closing": avg("score_closing"),
        "flagged_count": len([c for c in calls if c.get("flagged_at")]),
        "improvement_vs_previous": improvement,
    }).execute()

    print(f"Monthly report generated for {year_month}")


# ============================================================
# REAL-TIME LISTENERS (Supabase Realtime)
# ============================================================

def listen_for_new_calls(callback):
    """Subscribe to new call inserts via Supabase Realtime."""
    channel = supabase.channel("new_calls")
    channel.on_postgres_changes(
        event="INSERT",
        schema="public",
        table="conversations",
        filter="status=eq.new",
        callback=lambda payload: callback(payload["new"]),
    ).subscribe()

    print("[LISTENER] Watching for new calls...")
    return channel


def listen_for_approvals(callback):
    """Subscribe to script approval events."""
    channel = supabase.channel("approvals")
    channel.on_postgres_changes(
        event="UPDATE",
        schema="public",
        table="pending_scripts",
        callback=lambda payload: (
            callback(payload["new"])
            if payload["new"].get("status") == "approved"
            else None
        ),
    ).subscribe()

    print("[LISTENER] Watching for script approvals...")
    return channel


# ============================================================
# STATUS DASHBOARD
# ============================================================

def get_pipeline_status() -> dict:
    """Pull all dashboard views."""
    overview = supabase.table("pipeline_overview").select("*").execute()
    trend = supabase.table("weekly_trend").select("*").limit(8).execute()
    script_perf = supabase.table("script_performance").select("*").execute()
    pending = supabase.table("pending_approvals").select("*").execute()

    return {
        "overview": overview.data,
        "trend": trend.data,
        "script_perf": script_perf.data,
        "pending": pending.data,
    }


# ============================================================
# HELPERS
# ============================================================

def get_active_script() -> dict:
    """Get the currently active production script."""
    result = supabase.table("script_versions") \
        .select("*") \
        .eq("active", True) \
        .single() \
        .execute()

    if result.data:
        return result.data
    return {"version_label": "v1.0", "script_text": ""}


def get_new_calls() -> list:
    """Get all calls with status 'new'."""
    result = supabase.table("conversations") \
        .select("*") \
        .eq("status", "new") \
        .order("created_at") \
        .execute()
    return result.data or []


def update_status(call_id: str, status: str, **extra) -> None:
    """Update a conversation's pipeline status."""
    supabase.table("conversations") \
        .update({"status": status, **extra}) \
        .eq("call_id", call_id) \
        .execute()


def get_optimization_batch() -> tuple:
    """Get low-rated, high-rated, and all analyzed calls for optimization."""
    all_analyzed = supabase.table("conversations") \
        .select("*") \
        .in_("status", ["complete", "flagged"]) \
        .not_.is_("rating", "null") \
        .order("call_timestamp", desc=True) \
        .execute()

    calls = all_analyzed.data or []
    low_rated = [c for c in calls if c["rating"] <= 2]
    high_rated = [c for c in calls if c["rating"] >= 4]

    return low_rated, high_rated, calls


def extract_patterns(calls: list, field: str) -> list:
    """Extract and count recurring patterns from a JSONB field."""
    patterns = {}
    for call in calls:
        items = call.get(field) or []
        for item in items:
            key = item.get("what_happened") or item.get("what_worked") or "unknown"
            if key not in patterns:
                patterns[key] = {
                    "description": key,
                    "category": item.get("category", "general"),
                    "count": 0,
                    "examples": [],
                }
            patterns[key]["count"] += 1
            if len(patterns[key]["examples"]) < 3:
                patterns[key]["examples"].append(call["call_id"])

    return sorted(patterns.values(), key=lambda p: p["count"], reverse=True)


def find_recurring_issues(patterns: list) -> list:
    """Filter to patterns appearing in 30%+ of calls."""
    total = sum(p["count"] for p in patterns)
    if total == 0:
        return []
    return [p for p in patterns if (p["count"] / total) >= 0.3]


def build_diff_summary(current_script: str, result: dict) -> str:
    """Build a human-readable summary of what changed and why."""
    candidate_key = f"candidate_{result['selected_candidate']}"
    candidate = result[candidate_key]
    return "\n".join([
        f"Selected candidate {result['selected_candidate']} of 3.",
        f"Focus: {candidate['reasoning']}",
        f"Projected impact: {json.dumps(candidate['projected_impact'])}",
        f"Failure coverage: {round(candidate.get('failure_coverage', 0) * 100)}% of observed patterns addressed.",
    ])


def log_change(action, version_from, version_to, suggestion_id, optimization_id, actor, reason):
    """Write to the change_log audit trail."""
    supabase.table("change_log").insert({
        "action": action,
        "version_from": version_from,
        "version_to": version_to,
        "suggestion_id": suggestion_id,
        "optimization_id": optimization_id,
        "actor": actor,
        "reason": reason,
    }).execute()
