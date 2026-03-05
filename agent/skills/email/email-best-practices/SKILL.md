---
name: email-best-practices
description: Use when building email features, emails going to spam, high bounce rates, setting up SPF/DKIM/DMARC authentication, implementing email capture, ensuring compliance (CAN-SPAM, GDPR, CASL), handling webhooks, retry logic, or deciding transactional vs marketing.
---

# Email Best Practices

Guidance for building deliverable, compliant, user-friendly emails.

## Architecture Overview

```
[User] → [Email Form] → [Validation] → [Double Opt-In]
                                              ↓
                                    [Consent Recorded]
                                              ↓
[Suppression Check] ←──────────────[Ready to Send]
        ↓
[Idempotent Send + Retry] ──────→ [Email API]
                                       ↓
                              [Webhook Events]
                                       ↓
              ┌────────┬────────┬─────────────┐
              ↓        ↓        ↓             ↓
         Delivered  Bounced  Complained  Opened/Clicked
                       ↓        ↓
              [Suppression List Updated]
                       ↓
              [List Hygiene Jobs]
```

## Quick Reference

| Need to... | See |
|------------|-----|
| Set up SPF/DKIM/DMARC, fix spam issues | [Deliverability](deliverability.md) |
| Build password reset, OTP, confirmations | [Transactional Emails](transactional-emails.md) |
| Plan which emails your app needs | [Transactional Email Catalog](transactional-email-catalog.md) |
| Build newsletter signup, validate emails | [Email Capture](email-capture.md) |
| Send newsletters, promotions | [Marketing Emails](marketing-emails.md) |
| Ensure CAN-SPAM/GDPR/CASL compliance | [Compliance](compliance.md) |
| Decide transactional vs marketing | [Email Types](email-types.md) |
| Handle retries, idempotency, errors | [Sending Reliability](sending-reliability.md) |
| Process delivery events, set up webhooks | [Webhooks & Events](webhooks-events.md) |
| Manage bounces, complaints, suppression | [List Management](list-management.md) |

## Start Here

**New app?**
Start with the [Catalog](transactional-email-catalog.md) to plan which emails your app needs (password reset, verification, etc.), then set up [Deliverability](deliverability.md) (DNS authentication) before sending your first email.

**Spam issues?**
Check [Deliverability](deliverability.md) first—authentication problems are the most common cause. Gmail/Yahoo reject unauthenticated emails.

**Marketing emails?**
Follow this path: [Email Capture](email-capture.md) (collect consent) → [Compliance](compliance.md) (legal requirements) → [Marketing Emails](marketing-emails.md) (best practices).

**Production-ready sending?**
Add reliability: [Sending Reliability](sending-reliability.md) (retry + idempotency) → [Webhooks & Events](webhooks-events.md) (track delivery) → [List Management](list-management.md) (handle bounces).
