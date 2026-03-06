-- ============================================================
-- ENABL3 CALL PIPELINE v3 — SUPABASE SCHEMA
-- 7-Step Self-Improving Voice Agent Pipeline
-- ============================================================
-- Run this in your Supabase SQL Editor
-- ============================================================


-- ============================================================
-- 1. CONVERSATIONS TABLE
-- Every call lands here. This is the source of truth.
-- ============================================================

CREATE TABLE conversations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  call_id VARCHAR(50) UNIQUE NOT NULL,
  
  -- Pipeline Status
  status VARCHAR(20) NOT NULL DEFAULT 'new'
    CHECK (status IN ('new', 'analyzing', 'analyzed', 'flagged', 'complete', 'error')),
  
  -- Raw Call Data
  transcript TEXT NOT NULL,
  call_duration_seconds INTEGER,
  customer_name VARCHAR(255),
  customer_phone VARCHAR(50),
  service_type VARCHAR(100),
  urgency VARCHAR(50),
  property_type VARCHAR(50),
  property_age VARCHAR(100),
  budget_range VARCHAR(100),
  decision_maker VARCHAR(20),
  
  -- Agent 1 Output (from the call itself)
  lead_score INTEGER CHECK (lead_score BETWEEN 1 AND 10),
  call_outcome VARCHAR(50),  -- booked, callback, lost, escalated
  call_notes TEXT,
  
  -- Analysis Results (populated by Agent 2 — Step 3-4)
  rating INTEGER CHECK (rating BETWEEN 1 AND 5),
  score_rapport INTEGER CHECK (score_rapport BETWEEN 1 AND 10),
  score_discovery INTEGER CHECK (score_discovery BETWEEN 1 AND 10),
  score_adaptability INTEGER CHECK (score_adaptability BETWEEN 1 AND 10),
  score_objection_handling INTEGER CHECK (score_objection_handling BETWEEN 1 AND 10),
  score_closing INTEGER CHECK (score_closing BETWEEN 1 AND 10),
  analysis_summary TEXT,
  strengths JSONB DEFAULT '[]'::jsonb,
  failures JSONB DEFAULT '[]'::jsonb,
  
  -- Script Version Used
  script_version VARCHAR(20) DEFAULT 'v1.0',
  
  -- Error Handling
  error_message TEXT,
  retry_count INTEGER DEFAULT 0,
  
  -- Timestamps
  call_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  analyzed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for pipeline queries
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_new ON conversations(status) WHERE status = 'new';
CREATE INDEX idx_conversations_flagged ON conversations(status) WHERE status = 'flagged';
CREATE INDEX idx_conversations_rating ON conversations(rating);
CREATE INDEX idx_conversations_call_timestamp ON conversations(call_timestamp);


-- ============================================================
-- 2. SCRIPT VERSIONS (Production Scripts)
-- Only approved, active scripts live here
-- ============================================================

CREATE TABLE script_versions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  version_label VARCHAR(20) UNIQUE NOT NULL,
  script_text TEXT NOT NULL,
  
  -- What triggered this version
  optimization_id VARCHAR(50),
  change_summary TEXT,
  
  -- Performance tracking (updated as calls come in)
  total_calls INTEGER DEFAULT 0,
  avg_rating DECIMAL(3,2),
  avg_score DECIMAL(4,2),
  
  -- Status
  active BOOLEAN DEFAULT FALSE,
  
  -- Git tracking
  git_commit_hash VARCHAR(40),
  git_branch VARCHAR(100) DEFAULT 'main',
  
  -- Approval
  approved_by VARCHAR(255),
  approved_at TIMESTAMPTZ,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Only one active script at a time
CREATE UNIQUE INDEX idx_active_script ON script_versions(active) WHERE active = TRUE;


-- ============================================================
-- 3. PENDING SCRIPTS (Staging / Hold Table)
-- Generated suggestions land here BEFORE going to production.
-- Human reviews, approves or rejects.
-- ============================================================

CREATE TABLE pending_scripts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  suggestion_id VARCHAR(50) UNIQUE NOT NULL,
  
  -- Status
  status VARCHAR(20) NOT NULL DEFAULT 'pending_review'
    CHECK (status IN ('pending_review', 'approved', 'rejected', 'expired')),
  
  -- The 3 candidates Agent 3 generated
  candidate_1 JSONB NOT NULL,  -- { script_text, reasoning, projected_impact }
  candidate_2 JSONB NOT NULL,
  candidate_3 JSONB NOT NULL,
  
  -- Tournament selection results
  selected_candidate INTEGER NOT NULL CHECK (selected_candidate IN (1, 2, 3)),
  selection_reasoning TEXT NOT NULL,  -- Why this one won against failure patterns
  
  -- The winning script
  proposed_script TEXT NOT NULL,
  
  -- Diff from current production
  current_version VARCHAR(20) NOT NULL,
  proposed_version VARCHAR(20) NOT NULL,
  diff_summary TEXT NOT NULL,  -- Human-readable: what changed and why
  
  -- Evidence base
  calls_analyzed INTEGER,
  failure_patterns JSONB DEFAULT '[]'::jsonb,
  recurring_issues JSONB DEFAULT '[]'::jsonb,
  period_start TIMESTAMPTZ,
  period_end TIMESTAMPTZ,
  
  -- Projected impact
  projected_improvement JSONB,  -- { metric: expected_change }
  
  -- Review
  reviewed_by VARCHAR(255),
  review_notes TEXT,
  reviewed_at TIMESTAMPTZ,
  
  -- Notification tracking
  slack_notified BOOLEAN DEFAULT FALSE,
  email_notified BOOLEAN DEFAULT FALSE,
  notification_sent_at TIMESTAMPTZ,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '7 days')
);

CREATE INDEX idx_pending_scripts_status ON pending_scripts(status);
CREATE INDEX idx_pending_review ON pending_scripts(status) WHERE status = 'pending_review';


-- ============================================================
-- 4. OPTIMIZATION LOG
-- Full audit trail of every optimization cycle
-- ============================================================

CREATE TABLE optimization_log (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  optimization_id VARCHAR(50) UNIQUE NOT NULL,
  
  -- What was analyzed
  calls_analyzed INTEGER,
  calls_rated_low INTEGER,   -- rating <= 2
  calls_rated_high INTEGER,  -- rating >= 4
  period_start TIMESTAMPTZ,
  period_end TIMESTAMPTZ,
  
  -- Analysis
  what_went_wrong JSONB DEFAULT '[]'::jsonb,   -- from rating < 3
  what_went_well JSONB DEFAULT '[]'::jsonb,    -- from rating >= 4
  recurring_patterns JSONB DEFAULT '[]'::jsonb,
  
  -- Results
  suggestion_id VARCHAR(50),  -- links to pending_scripts
  previous_version VARCHAR(20),
  proposed_version VARCHAR(20),
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================================
-- 5. CHANGE LOG
-- Git-style audit of every script change
-- ============================================================

CREATE TABLE change_log (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  
  action VARCHAR(30) NOT NULL,  -- 'script_proposed', 'script_approved', 'script_rejected', 'script_deployed', 'script_rolled_back'
  
  version_from VARCHAR(20),
  version_to VARCHAR(20),
  
  suggestion_id VARCHAR(50),
  optimization_id VARCHAR(50),
  
  actor VARCHAR(255),       -- who did it (human name or 'system')
  reason TEXT,
  
  git_commit_hash VARCHAR(40),
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_change_log_action ON change_log(action);


-- ============================================================
-- 6. MONTHLY REPORTS
-- ============================================================

CREATE TABLE monthly_reports (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  month VARCHAR(7) NOT NULL UNIQUE,  -- YYYY-MM
  
  total_calls INTEGER,
  avg_rating DECIMAL(3,2),
  avg_score DECIMAL(4,2),
  
  rating_distribution JSONB,  -- { "1": count, "2": count, ... "5": count }
  
  avg_rapport DECIMAL(4,2),
  avg_discovery DECIMAL(4,2),
  avg_adaptability DECIMAL(4,2),
  avg_objection_handling DECIMAL(4,2),
  avg_closing DECIMAL(4,2),
  
  flagged_count INTEGER,
  optimization_cycles INTEGER,
  scripts_proposed INTEGER,
  scripts_approved INTEGER,
  scripts_rejected INTEGER,
  
  improvement_vs_previous DECIMAL(3,2),
  
  top_failures JSONB DEFAULT '[]'::jsonb,
  top_strengths JSONB DEFAULT '[]'::jsonb,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================================
-- 7. ARCHIVE TABLE TEMPLATE
-- ============================================================

CREATE OR REPLACE FUNCTION create_monthly_archive(year_month TEXT)
RETURNS VOID AS $$
BEGIN
  EXECUTE format('
    CREATE TABLE IF NOT EXISTS conversations_archive_%s (
      LIKE conversations INCLUDING ALL
    )', replace(year_month, '-', '_'));
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- 8. AUTO-UPDATE TIMESTAMP TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER conversations_updated_at
  BEFORE UPDATE ON conversations
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();


-- ============================================================
-- 9. REAL-TIME SUBSCRIPTIONS
-- ============================================================

-- Orchestrator listens for new calls
ALTER PUBLICATION supabase_realtime ADD TABLE conversations;
-- Dashboard listens for pending approvals
ALTER PUBLICATION supabase_realtime ADD TABLE pending_scripts;


-- ============================================================
-- 10. ROW LEVEL SECURITY
-- ============================================================

ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE script_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE pending_scripts ENABLE ROW LEVEL SECURITY;
ALTER TABLE optimization_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE change_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE monthly_reports ENABLE ROW LEVEL SECURITY;

-- Service role (backend/orchestrator) — full access
CREATE POLICY "Service full access" ON conversations FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service full access" ON script_versions FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service full access" ON pending_scripts FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service full access" ON optimization_log FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service full access" ON change_log FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service full access" ON monthly_reports FOR ALL USING (auth.role() = 'service_role');

-- Authenticated users (dashboard) — read + approve/reject pending scripts
CREATE POLICY "Auth read" ON conversations FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Auth read" ON script_versions FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Auth read" ON pending_scripts FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Auth update pending" ON pending_scripts FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "Auth read" ON optimization_log FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Auth read" ON change_log FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Auth read" ON monthly_reports FOR SELECT USING (auth.role() = 'authenticated');


-- ============================================================
-- 11. DASHBOARD VIEWS
-- ============================================================

-- Pipeline status at a glance
CREATE VIEW pipeline_overview AS
SELECT
  status,
  COUNT(*) as count,
  ROUND(AVG(rating), 2) as avg_rating,
  ROUND(AVG(
    (score_rapport + score_discovery + score_adaptability + 
     score_objection_handling + score_closing) / 5.0
  ), 2) as avg_composite_score
FROM conversations
GROUP BY status;

-- Rating distribution
CREATE VIEW rating_distribution AS
SELECT
  rating,
  COUNT(*) as count,
  ROUND(COUNT(*)::decimal / SUM(COUNT(*)) OVER() * 100, 1) as percentage
FROM conversations
WHERE rating IS NOT NULL
GROUP BY rating
ORDER BY rating;

-- Weekly trend
CREATE VIEW weekly_trend AS
SELECT
  DATE_TRUNC('week', call_timestamp) AS week,
  COUNT(*) AS total_calls,
  ROUND(AVG(rating), 2) AS avg_rating,
  ROUND(AVG(score_rapport), 2) AS avg_rapport,
  ROUND(AVG(score_discovery), 2) AS avg_discovery,
  ROUND(AVG(score_adaptability), 2) AS avg_adaptability,
  ROUND(AVG(score_objection_handling), 2) AS avg_objection,
  ROUND(AVG(score_closing), 2) AS avg_closing,
  SUM(CASE WHEN rating <= 2 THEN 1 ELSE 0 END) AS low_rated,
  SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END) AS high_rated
FROM conversations
WHERE rating IS NOT NULL
GROUP BY DATE_TRUNC('week', call_timestamp)
ORDER BY week DESC;

-- Script version performance comparison
CREATE VIEW script_performance AS
SELECT
  script_version,
  COUNT(*) AS total_calls,
  ROUND(AVG(rating), 2) AS avg_rating,
  ROUND(AVG(score_rapport), 2) AS avg_rapport,
  ROUND(AVG(score_discovery), 2) AS avg_discovery,
  ROUND(AVG(score_adaptability), 2) AS avg_adaptability,
  ROUND(AVG(score_objection_handling), 2) AS avg_objection,
  ROUND(AVG(score_closing), 2) AS avg_closing,
  MIN(rating) AS worst_rating,
  MAX(rating) AS best_rating,
  SUM(CASE WHEN rating <= 2 THEN 1 ELSE 0 END) AS low_rated
FROM conversations
WHERE rating IS NOT NULL
GROUP BY script_version
ORDER BY script_version;

-- Top failure patterns
CREATE VIEW common_failures AS
SELECT
  failure->>'what_happened' AS failure_type,
  failure->>'category' AS category,
  COUNT(*) AS occurrences,
  ROUND(AVG(rating), 2) AS avg_call_rating
FROM conversations,
  jsonb_array_elements(failures) AS failure
WHERE failures != '[]'::jsonb
GROUP BY failure->>'what_happened', failure->>'category'
ORDER BY occurrences DESC
LIMIT 20;

-- Top strengths
CREATE VIEW common_strengths AS
SELECT
  strength->>'what_worked' AS strength_type,
  strength->>'category' AS category,
  COUNT(*) AS occurrences,
  ROUND(AVG(rating), 2) AS avg_call_rating
FROM conversations,
  jsonb_array_elements(strengths) AS strength
WHERE strengths != '[]'::jsonb
GROUP BY strength->>'what_worked', strength->>'category'
ORDER BY occurrences DESC
LIMIT 20;

-- Pending approvals (for Slack/dashboard)
CREATE VIEW pending_approvals AS
SELECT
  suggestion_id,
  status,
  current_version,
  proposed_version,
  diff_summary,
  calls_analyzed,
  selected_candidate,
  selection_reasoning,
  created_at,
  expires_at,
  (expires_at < NOW()) as is_expired
FROM pending_scripts
WHERE status = 'pending_review'
ORDER BY created_at DESC;


-- ============================================================
-- 12. AUTO-EXPIRE PENDING SCRIPTS (Optional cron)
-- ============================================================

CREATE OR REPLACE FUNCTION expire_old_suggestions()
RETURNS VOID AS $$
BEGIN
  UPDATE pending_scripts
  SET status = 'expired'
  WHERE status = 'pending_review'
    AND expires_at < NOW();
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- 13. SEED DATA
-- ============================================================

INSERT INTO script_versions (version_label, script_text, active, change_summary)
VALUES ('v1.0', 'Initial sales agent script — see /call-agent skill file', TRUE, 'Initial deployment');

INSERT INTO change_log (action, version_to, actor, reason)
VALUES ('script_deployed', 'v1.0', 'system', 'Initial pipeline setup');
