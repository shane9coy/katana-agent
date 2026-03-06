#!/usr/bin/env python3
"""
orchestrator.py — 7-Step Pipeline Runner
==========================================

THE 7 STEPS:
  1. Call ends → transcript saved to conversations table
  2. Supabase webhook fires → POSTs to your endpoint
  3. Agent analyzes transcript with scoring algorithms
  4. Agent writes rating (1-5) + analysis back to row
  5. Weekly: Agent summarizes failures/wins, generates 3
     candidate scripts, tournament-selects the best one
  6. Slack/email notification → human approves/rejects
  7. On approval: deploy to production + push to git

Usage:
  python orchestrator.py                      Process new calls (Steps 2-4)
  python orchestrator.py --listen             Real-time listener
  python orchestrator.py --optimize           Weekly optimization (Step 5)
  python orchestrator.py --approve SUG-xxx    Approve pending script (Step 6b → 7)
  python orchestrator.py --reject SUG-xxx     Reject pending script
  python orchestrator.py --rollback "reason"  Revert to previous script
  python orchestrator.py --archive            Monthly archive + report
  python orchestrator.py --status             Pipeline dashboard
"""

import sys
import signal
import random
import time
from datetime import datetime

from pipeline_client import (
    supabase,
    analyze_call,
    run_optimization_cycle,
    notify_pending_script,
    approve_script,
    reject_script,
    rollback_script,
    archive_month,
    get_pipeline_status,
    get_new_calls,
    update_status,
    listen_for_new_calls,
    listen_for_approvals,
)


# ============================================================
# STEPS 2-4: Process new calls
# ============================================================

def process_new_calls():
    """Batch-process all calls with status 'new'."""
    new_calls = get_new_calls()

    if not new_calls:
        print("No new calls to process.")
        return

    print(f"Processing {len(new_calls)} new calls...\n")

    for call in new_calls:
        call_id = call["call_id"]
        try:
            # Mark as analyzing
            update_status(call_id, "analyzing")
            print(f"[{call_id}] Analyzing...")

            # ---------------------------------------------------
            # HOOK: Replace with your Katana agent call
            # analysis = katana_agent.run_skill("/review-call", {
            #     "transcript": call["transcript"],
            #     "context": {
            #         "service_type": call.get("service_type"),
            #         "urgency": call.get("urgency"),
            #         "lead_score": call.get("lead_score"),
            #     }
            # })
            # ---------------------------------------------------

            # Placeholder
            analysis = simulate_analysis(call)

            # Write results back (Step 4)
            result = analyze_call(call_id, analysis)
            if result:
                print(f"[{call_id}] Rating: {result['rating']}/5 → {result['status']}")

        except Exception as e:
            print(f"[{call_id}] Error: {e}")
            update_status(
                call_id,
                "error",
                error_message=str(e),
                retry_count=(call.get("retry_count") or 0) + 1,
            )

    print("\nProcessing complete.")


# ============================================================
# REAL-TIME LISTENER (Steps 2-4 continuous)
# ============================================================

def start_listener():
    """Run as a daemon — processes calls as they arrive."""
    print("Pipeline listener active. Waiting for calls...\n")

    def on_new_call(call):
        call_id = call["call_id"]
        print(f"\nNew call detected: {call_id}")

        update_status(call_id, "analyzing")
        analysis = simulate_analysis(call)
        result = analyze_call(call_id, analysis)

        if result:
            print(f"{call_id} → Rating: {result['rating']}/5 → {result['status']}")

    def on_approval(approved):
        print(f"\nScript {approved['suggestion_id']} approved — deploying...")

    listen_for_new_calls(on_new_call)
    listen_for_approvals(on_approval)

    print("Press Ctrl+C to stop.\n")

    # Keep alive
    def shutdown(signum, frame):
        print("\nListener stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    while True:
        time.sleep(1)


# ============================================================
# STEP 5: Weekly Optimization
# ============================================================

def run_optimization():
    """Analyze flagged calls, generate candidates, notify for approval."""
    print("=== WEEKLY OPTIMIZATION CYCLE ===\n")

    result = run_optimization_cycle()

    if not result:
        print("Optimization skipped — insufficient data.")
        return

    print(f"\nOptimization complete.")
    print(f"  Suggestion: {result['suggestion_id']}")
    print(f"  Optimization: {result['opt_id']}")

    # Auto-notify (Step 6)
    print("\nSending notification...")
    notify_pending_script(result["suggestion_id"])

    print("\nScript is now pending human review.")
    print(f"Run: python orchestrator.py --approve {result['suggestion_id']}")


# ============================================================
# STEP 6b: Approve / Reject
# ============================================================

def handle_approve(suggestion_id: str):
    """Approve and deploy a pending script."""
    import os
    approver = os.getenv("APPROVER_NAME", "admin")
    print(f"Approving {suggestion_id} as {approver}...")

    deployed = approve_script(suggestion_id, approver, "Approved via CLI")

    if deployed:
        print(f"\nScript {deployed['version_label']} is now LIVE.")
        print("All new calls will use this script version.")


def handle_reject(suggestion_id: str, reason: str = "Rejected via CLI"):
    """Reject a pending script."""
    import os
    rejector = os.getenv("APPROVER_NAME", "admin")
    reject_script(suggestion_id, rejector, reason)
    print(f"{suggestion_id} rejected.")


# ============================================================
# ROLLBACK
# ============================================================

def handle_rollback(reason: str = "Performance regression detected"):
    """Revert to the previous script version."""
    import os
    rolled_back_by = os.getenv("APPROVER_NAME", "admin")
    previous = rollback_script(reason, rolled_back_by)
    if previous:
        print(f"Rolled back to {previous['version_label']}")


# ============================================================
# MONTHLY ARCHIVE
# ============================================================

def run_archive():
    """Archive completed conversations and generate monthly report."""
    now = datetime.utcnow()
    year_month = f"{now.year}-{now.month:02d}"

    print(f"Archiving conversations for {year_month}...")
    success = archive_month(year_month)

    if success:
        print("Active conversations table is now clean for next month.")
    else:
        print("Archive skipped or failed.")


# ============================================================
# STATUS DASHBOARD
# ============================================================

def show_status():
    """Print pipeline status to terminal."""
    status = get_pipeline_status()

    print()
    print("╔══════════════════════════════════════╗")
    print("║     ENABL3 PIPELINE STATUS            ║")
    print("╚══════════════════════════════════════╝")
    print()

    if status.get("overview"):
        print("QUEUE:")
        for s in status["overview"]:
            bar = "█" * min(s.get("count", 0), 30)
            rating = s.get("avg_rating", "—")
            print(f"  {s['status']:<12} {bar} {s['count']} (avg rating: {rating})")
        print()

    if status.get("pending"):
        print("PENDING APPROVALS:")
        for p in status["pending"]:
            expired = " ⚠️ EXPIRED" if p.get("is_expired") else ""
            print(
                f"  {p['suggestion_id']} | "
                f"{p['current_version']} → {p['proposed_version']} | "
                f"{p['calls_analyzed']} calls analyzed{expired}"
            )
        print()

    if status.get("trend"):
        print("WEEKLY TREND:")
        for t in status["trend"][:5]:
            week = t["week"][:10] if t.get("week") else "—"
            print(
                f"  {week} | {t['total_calls']} calls | "
                f"avg: {t['avg_rating']} | low: {t['low_rated']} | high: {t['high_rated']}"
            )
        print()

    if status.get("script_perf"):
        print("SCRIPT PERFORMANCE:")
        for p in status["script_perf"]:
            print(
                f"  {p['script_version']} | {p['total_calls']} calls | "
                f"avg: {p['avg_rating']} | worst: {p['worst_rating']} | low: {p['low_rated']}"
            )
        print()


# ============================================================
# SIMULATE ANALYSIS (Replace with Katana agent)
# ============================================================

def simulate_analysis(call: dict) -> dict:
    """Placeholder — replace with actual agent call."""
    scores = {
        "rapport": 5 + random.randint(0, 4),
        "discovery": 4 + random.randint(0, 5),
        "adaptability": 5 + random.randint(0, 4),
        "objection_handling": 3 + random.randint(0, 6),
        "closing": 5 + random.randint(0, 4),
    }

    strengths = []
    failures = []

    if scores["rapport"] >= 8:
        strengths.append({"what_worked": "Strong opening rapport", "category": "rapport"})
    if scores["objection_handling"] <= 5:
        failures.append({"what_happened": "Failed to address price concern", "category": "objection_handling"})
    if scores["closing"] <= 5:
        failures.append({"what_happened": "Weak close — no clear next step", "category": "closing"})

    return {
        "scores": scores,
        "summary": f"Simulated analysis for {call['call_id']}",
        "strengths": strengths,
        "failures": failures,
    }


# ============================================================
# MAIN
# ============================================================

def main():
    args = sys.argv[1:]
    mode = args[0] if args else "--process"
    arg = args[1] if len(args) > 1 else None
    extra = args[2] if len(args) > 2 else None

    try:
        if mode == "--process":
            process_new_calls()

        elif mode == "--listen":
            start_listener()

        elif mode == "--optimize":
            run_optimization()

        elif mode == "--approve":
            if not arg:
                print("Usage: python orchestrator.py --approve <suggestion_id>")
                return
            handle_approve(arg)

        elif mode == "--reject":
            if not arg:
                print("Usage: python orchestrator.py --reject <suggestion_id> [reason]")
                return
            handle_reject(arg, extra or "Rejected via CLI")

        elif mode == "--rollback":
            handle_rollback(arg or "Performance regression detected")

        elif mode == "--archive":
            run_archive()

        elif mode == "--status":
            show_status()

        else:
            print("Enabl3 Pipeline Orchestrator v3\n")
            print("Commands:")
            print("  --process                    Process new calls (Steps 2-4)")
            print("  --listen                     Real-time listener (daemon)")
            print("  --optimize                   Weekly optimization (Step 5)")
            print("  --approve <id>               Approve pending script (→ deploy)")
            print("  --reject <id> [reason]       Reject pending script")
            print("  --rollback [reason]           Revert to previous script")
            print("  --archive                    Monthly archive + report")
            print("  --status                     Pipeline dashboard")

    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
