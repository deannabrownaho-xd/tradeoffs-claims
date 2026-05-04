"""
FlaskServer: Claims Prioritization Web Application

Flask backend that serves the claims prioritization UI and handles all data processing.
Manages claim scoring, filtering, metrics calculation, and Claude AI integration.

USAGE:
1. Install dependencies:  pip install flask anthropic
2. Set API key:           export ANTHROPIC_API_KEY="sk-ant-..."
3. Run the server:        python app.py
4. Open in browser:       http://127.0.0.1:5000

ROUTES:
- GET  /                  Serve the main UI (index.html)
- GET  /claims            Return all 60 claims as JSON
- POST /optimize          Score and rank claims based on slider weights
- POST /chat              Send message to Claude, get filtered results

FEATURES:
- Dynamic scoring based on four optimization sliders
- Hard filtering by payer, issue_type, confidence, value, days_remaining
- Expires expired claims in filtered mode (days_remaining == 0)
- Claude integration for natural language filtering and analysis
- Real-time metrics calculation (recovery, count, deadline, acceptance, effort)
"""

import json
from flask import Flask, render_template, jsonify, request
from scoring import rank_claims
from claude_client import chat

app = Flask(__name__)


# --- Load claims once when the server starts ---
with open("claims.json") as f:
    ALL_CLAIMS = json.load(f)

# Valid sortable fields — maps to raw claim keys
SORT_FIELDS = {"recovery_potential", "net_value", "correction_confidence", "effort_hours"}


# --- Route 1: GET / ---
@app.route("/")
def index():
    return render_template("index.html")


# --- Route 2: GET /claims ---
@app.route("/claims")
def claims():
    return jsonify(ALL_CLAIMS)


# --- Sort helper ---
def apply_sort(claims_list, sort_field):
    """
    Sorts a list of claims by a raw field, descending.
    Ignores the request silently if the field isn't present on claims.
    """
    if sort_field not in SORT_FIELDS:
        return claims_list
    return sorted(claims_list, key=lambda c: c.get(sort_field, 0), reverse=True)


# --- Route 3: POST /optimize ---
# Called every time a slider moves, Top N changes, or toggle switches.
@app.route("/optimize", methods=["POST"])
def optimize():
    data = request.get_json()

    weights = {
        "financial_value": data.get("financial_value", 1.0),
        "confidence":      data.get("confidence", 0.5),
        "effort":          data.get("effort", 0.5),
        "risk":            data.get("risk", 0.5),
    }

    top_n_raw = data.get("top_n", 25)
    if top_n_raw == "all":
        top_n = None
    else:
        top_n = int(top_n_raw)

    filtered = data.get("filtered", True)

    # Optional hard filters from Claude — e.g. {payer: "UnitedHealth", issue_type: "missing_auth"}
    active_filters = data.get("filters", {}) or {}

    # Optional sort field from Claude — e.g. "recovery_potential"
    sort_field = data.get("sort")

    ranked = rank_claims(ALL_CLAIMS, weights)

    # Apply hard filters before score filtering
    if active_filters:
        ranked = apply_filters(ranked, active_filters)

    # Score-based filtering: keep only positive-scoring claims in filtered mode
    if filtered and not active_filters:
        pool = [c for c in ranked if c["score"] > 0]
    else:
        pool = ranked

    # Deadline-based filtering: remove expired claims in filtered mode (May 2026)
    # Claims with days_remaining == 0 cannot be filed and should not appear in prioritized list
    if filtered:
        pool = [c for c in pool if c.get("days_remaining", 0) > 0]

    is_empty = len(pool) == 0

    visible = pool if top_n is None else pool[:top_n]

    # Apply raw sort if requested (overrides score-based order)
    if sort_field:
        visible = apply_sort(visible, sort_field)

    if visible:
        net_recovery     = sum(c["net_value"] for c in visible)
        min_days_remaining = min([c.get("days_remaining", 0) for c in visible]) if visible else 0
        avg_confidence   = sum(c["correction_confidence"] for c in visible) / len(visible)
        total_effort     = sum(c["effort_hours"] for c in visible)
    else:
        net_recovery     = 0
        min_days_remaining = 0
        avg_confidence   = 0
        total_effort     = 0

    return jsonify({
        "claims": visible,
        "metrics": {
            "net_recovery":      round(net_recovery, 2),
            "prioritized_count": len(visible),
            "days_remaining":    round(min_days_remaining, 0),
            "avg_confidence":    round(avg_confidence, 3),
            "total_effort":      round(total_effort, 2),
        },
        "empty": is_empty,
    })


# --- Filter helper ---
def apply_filters(claims, filters):
    """
    Applies hard filters to a list of claims.
    Supported filters:
      claim_id       — exact match e.g. "CLM-058"
      payer          — exact match e.g. "UnitedHealth"
      issue_type     — exact match e.g. "missing_auth"
      min_confidence — e.g. 0.90 keeps claims with confidence >= 0.90
      max_confidence — e.g. 0.90 keeps claims with confidence <= 0.90
      min_net_value  — e.g. 5000 keeps claims with net_value >= 5000
      max_net_value  — e.g. 20000 keeps claims with net_value <= 20000
    """
    result = claims
    if filters.get("claim_id"):
        result = [c for c in result if c["id"].upper() == filters["claim_id"].upper()]
    if filters.get("payer"):
        result = [c for c in result if c["payer"].lower() == filters["payer"].lower()]
    if filters.get("issue_type"):
        result = [c for c in result if c["issue_type"].lower() == filters["issue_type"].lower()]
    if filters.get("min_confidence") is not None:
        threshold = float(filters["min_confidence"])
        result = [c for c in result if c["correction_confidence"] >= threshold]
    if filters.get("max_confidence") is not None:
        threshold = float(filters["max_confidence"])
        result = [c for c in result if c["correction_confidence"] <= threshold]
    if filters.get("min_net_value") is not None:
        threshold = float(filters["min_net_value"])
        result = [c for c in result if c["net_value"] >= threshold]
    if filters.get("max_net_value") is not None:
        threshold = float(filters["max_net_value"])
        result = [c for c in result if c["net_value"] <= threshold]
    return result


# --- Route 4: POST /chat ---
# Called when the analyst sends a message in the sidebar.
#
# Expects JSON body:
# {
#   message:  "show me the easy wins",
#   history:  [{role: "user", content: "..."}, {role: "assistant", content: "..."}],
#   weights:  {financial_value, confidence, effort, risk},
#   top_n:    25 | "all",
#   filtered: true | false,
#   visible_claims: [...]
# }
#
# Returns JSON:
# {
#   text:     "Claude's response",
#   sliders:  {financial_value, confidence, effort, risk} or null,
#   profile:  "easy_win" | null,
#   sort:     "recovery_potential" | "net_value" | ... | null,
#   prompts:  ["prompt 1", "prompt 2"]
# }
@app.route("/chat", methods=["POST"])
def chat_route():
    data = request.get_json()

    # Build the message history including the new user message.
    history = data.get("history", [])
    message = data.get("message", "")

    messages = history + [{"role": "user", "content": message}]

    # Build the app state context for Claude.
    app_state = {
        "weights":        data.get("weights", {}),
        "top_n":          data.get("top_n", 25),
        "filtered":       data.get("filtered", True),
        "visible_claims": data.get("visible_claims", []),
        "total_claims":   len(ALL_CLAIMS),
        "all_claims":     ALL_CLAIMS,
    }

    # Call Claude.
    result = chat(messages, app_state)

    # Determine effective filtered state — Claude may have changed it
    new_filtered = app_state["filtered"]
    if result.get("mode") == "unfiltered":
        new_filtered = False
    elif result.get("mode") == "filtered":
        new_filtered = True

    # Get active filters from Claude's response
    new_filters = result.get("filters")

    # Get sort field from Claude's response
    sort_field = result.get("sort")

    # Re-run optimize if Claude changed sliders, mode, filters, or requested a sort
    if result["sliders"] or result.get("mode") or new_filters is not None or sort_field:
        new_weights = result["sliders"] if result["sliders"] else app_state["weights"]

        ranked = rank_claims(ALL_CLAIMS, new_weights)

        # Apply hard filters if Claude sent them
        if new_filters:
            ranked = apply_filters(ranked, new_filters)
            pool   = ranked  # show all matching claims regardless of score
        elif new_filtered:
            pool = [c for c in ranked if c["score"] > 0]
        else:
            pool = ranked

        # Filter out expired claims (days_remaining == 0) in filtered mode
        if new_filtered:
            pool = [c for c in pool if c.get("days_remaining", 0) > 0]

        top_n   = app_state["top_n"]
        visible = pool if top_n == "all" else pool[:int(top_n)] if top_n else pool

        # Apply raw sort if Claude requested it — overrides score-based order
        # Only sort; do NOT touch sliders when a SORT instruction was the trigger
        if sort_field:
            visible = apply_sort(visible, sort_field)

        if visible:
            net_recovery     = sum(c["net_value"] for c in visible)
            min_days_remaining = min([c.get("days_remaining", 0) for c in visible]) if visible else 0
            avg_confidence   = sum(c["correction_confidence"] for c in visible) / len(visible)
            total_effort     = sum(c["effort_hours"] for c in visible)
        else:
            net_recovery = min_days_remaining = avg_confidence = total_effort = 0

        result["claims"]  = visible
        result["metrics"] = {
            "net_recovery":      round(net_recovery, 2),
            "prioritized_count": len(visible),
            "days_remaining":    round(min_days_remaining, 0),
            "avg_confidence":    round(avg_confidence, 3),
            "total_effort":      round(total_effort, 2),
        }
        result["empty"] = len(visible) == 0
    else:
        result["claims"]  = None
        result["metrics"] = None
        result["empty"]   = False

    return jsonify(result)


# --- Start the server ---
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
