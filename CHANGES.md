# Session Changes (May 2026)

## What Changed

### Labels in the App
- Column "Recovery" → "Total Value"
- Column "Net Value" → "Projected Recovery"
- Column "Confidence" → "Acceptance Likelihood"
- Metric "High-Value Corrections" → "Closest Deadline" (shows how many days until the claim expires)

### Sliders (the four controls at the top)
1. **Financial Value** — unchanged
2. **Days Remaining** — new control for prioritizing claims that have more time left before they expire
3. **Acceptance Likelihood** — controls how confident the system is about the correction
4. **Manual Review Effort** — controls how much time you're willing to spend on each claim

### New Data
- Each claim now has a "days remaining" value (how many days until it expires)
- Expired claims (0 days) don't show in filtered view, but do show in unfiltered view

### What "Closest Deadline" Means
The metric card shows the claim in your current view that expires soonest. Shows as "5d" (5 days) or "Expired".

## Files Modified
- `scoring.py` — how claims are ranked
- `app.py` — backend calculations
- `templates/index.html` — what you see on screen
- `claims.json` — the data (added days_remaining to each claim)
- RAG documents — context Claude uses to answer questions

## What You Can Do Now
- Slide "Days Remaining" to prioritize claims that have lots of time vs. claims running out of time
- See at a glance how urgent your deadlines are via the "Closest Deadline" metric
- Ask Claude "show me CLM-058" and it will filter the table to just that claim (instead of explaining it)
