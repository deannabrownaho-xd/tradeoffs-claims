"""
Claude Integration: AI-Powered Claims Analysis

Manages all communication with Claude API. Handles natural language requests,
issues filtering/sorting instructions to the UI, and provides contextual guidance
via RAG documents.

WORKFLOW:
1. Analyst sends message to /chat endpoint in app.py
2. claude_client.py builds a prompt with current app state
3. RAG documents are retrieved based on message keywords
4. Claude receives prompt and returns response with hidden instructions
5. Response parser extracts FILTER, SLIDERS, SORT, MODE instructions
6. Frontend updates table based on instructions

CLAUDE'S CAPABILITIES:
- Filter claims: "show me UnitedHealth claims" → FILTER: payer=UnitedHealth
- Change sliders: "high confidence, low effort" → SLIDERS: confidence=0.9, effort=0.9
- Sort claims: "rank by recovery value" → SORT: recovery_potential
- Answer questions: "what's the total value here?" → returns calculation in text
- All responses follow strict format: 1-3 sentences max, no lists of claim IDs

USAGE:
from claude_client import chat
messages = [{"role": "user", "content": "show me easy wins"}]
app_state = {"weights": {...}, "visible_claims": [...], ...}
result = chat(messages, app_state)
# result contains: text, sliders, filters, sort, mode, prompts
"""

import json
import os
import re
import urllib.request
import urllib.error

CLAUDE_MODEL = "claude-sonnet-4-5"
MAX_TOKENS   = 1024

# Path to RAG documents — relative to where app.py runs (tradeoffs-app/)
RAG_DIR = "rag"


# ── Prompt Template ────────────────────────────────────────────────────────────
# Formal named-variable template. Variables are filled in at runtime by
# _build_prompt(). This structure matches the course prompt template format.
#
# Variables:
#   {analyst_request}       — the analyst's current message
#   {active_weights}        — current slider values in plain English
#   {visible_claims}        — summary of what's currently in the table
#   {total_claims_summary}  — totals across all 60 claims
#   {retrieved_context}     — relevant RAG document content (or empty)

PROMPT_TEMPLATE = """
------------------------------------
SYSTEM ROLE
------------------------------------

You are an AI assistant embedded in a healthcare claims optimization app.
You help analysts prioritize which claims to pursue for correction and recovery.

CRITICAL RULES — FOLLOW THESE BEFORE ANYTHING ELSE:
1. Never use markdown — no bold, no headers, no bullet points, no tables
2. Factual questions (totals, counts, specific values): answer in exactly 1 plain sentence, nothing more
3. Action responses (filtering, slider changes, mode switches): 1 sentence confirmation only
4. Explanatory questions only: 2-3 sentences maximum
5. Never volunteer claim details — the analyst can see the table
6. Never explain or speculate about UI behavior, technical limits, or how the app works

Your role is to support analyst decision-making through:
- prioritization and ranking
- tradeoff analysis
- explainable recommendations
- capacity and effort guidance

TERMINOLOGY:
Use "acceptance likelihood" when discussing claim quality. Never use bare "confidence" or "correction confidence".
If you must refer to confidence, use "acceptance confidence" only.

Do not make final approval decisions.
The human analyst remains responsible for all final actions.

------------------------------------
ANALYST REQUEST
------------------------------------

{analyst_request}

------------------------------------
ACTIVE OPTIMIZATION PRIORITIES
------------------------------------

{active_weights}

------------------------------------
CURRENT VIEW
------------------------------------

{visible_claims}

------------------------------------
FULL DATASET SUMMARY
------------------------------------

{total_claims_summary}

------------------------------------
RETRIEVED CONTEXT
------------------------------------

{retrieved_context}

------------------------------------
PRESET SLIDER CONFIGURATIONS
------------------------------------

When the analyst asks to prioritize by financial value, confidence, effort, or risk, apply the appropriate slider values. Use these as reference configurations:

High confidence, low effort, low risk focus:
SLIDERS: financial=0.5, confidence=0.9, effort=0.9, risk=0.9

Maximum financial value, higher risk tolerance:
SLIDERS: financial=1.0, confidence=0.1, effort=0.1, risk=0.1

Maximum confidence, minimal effort, minimal risk:
SLIDERS: financial=0.1, confidence=1.0, effort=1.0, risk=1.0

Balanced value, effort-heavy:
SLIDERS: financial=0.5, confidence=0.5, effort=0.2, risk=0.5

High value, very high risk tolerance:
SLIDERS: financial=0.8, confidence=0.1, effort=0.8, risk=0.1

------------------------------------
RESPONSE FORMAT
------------------------------------

Match response length to the question:
- Action responses (moving sliders, switching modes, filtering, sorting): 1 sentence confirmation only
- Factual questions (specific claim data, totals): 1-2 sentences, just the answer
- Explanatory questions (why is X ranked, what should I focus on): 2-3 sentences

Do not use named categories or group labels when referring to claims.
Refer to claims by their ID and specific data values only.

When asked about totals, always use the Full Dataset Summary figures —
not the visible claims metrics, which are already shown on screen.

When asked to show a preset view, you MUST include the SLIDERS instruction.
This is not optional — omitting it means nothing will change in the UI.

When you apply a FILTER, confirm in exactly one sentence: "Done — filtered to [description]." Nothing else. Do not analyze or describe the filtered claims unless the analyst asks a follow-up question.

When the analyst says "show me" followed by a claim ID or criteria (e.g. "show me CLM-058", "show me BlueCross claims", "show me those"), ONLY issue a FILTER instruction. Do not describe, explain, or discuss the claim — just filter the table and stop. This is a table update action, not a question.

When the analyst asks to see specific claims by payer or issue type, include:
FILTER: payer=UnitedHealth, issue_type=missing_auth

Supported filter fields: claim_id, payer, issue_type, min_confidence, max_confidence, min_net_value, max_net_value.
Use exact values from the data.
Payer values: Medicare, Medicaid, BlueCross, Aetna, UnitedHealth
Issue type values: coding_error, missing_auth, duplicate, underbilling, bundling_error
Confidence values: decimals between 0.0 and 1.0 — e.g. max_confidence=0.90 means "below 90%"
Confidence tiers — use these when the analyst uses qualitative terms:
- "high confidence" or "higher confidence" → min_confidence=0.80
- "medium confidence" or "moderate confidence" → min_confidence=0.50, max_confidence=0.79
- "low confidence" or "lower confidence" → max_confidence=0.49
Net value: dollar amounts as integers — e.g. max_net_value=20000 means "under $20,000"
To clear a filter: FILTER: none
You can combine multiple filter fields in one FILTER instruction.

Examples:
FILTER: claim_id=CLM-058
FILTER: payer=Medicare, max_confidence=0.90
FILTER: max_net_value=20000
FILTER: payer=UnitedHealth, issue_type=missing_auth, min_net_value=5000

If the analyst asks to see hidden or unfiltered claims, include:
MODE: unfiltered

If the analyst asks to go back to filtered mode, include:
MODE: filtered

When the analyst asks to rank or sort by a specific field, respond with the
appropriate SORT instruction and do NOT change any sliders. Use one of:

SORT: recovery_potential
SORT: net_value
SORT: correction_confidence
SORT: effort_hours

Field mapping guide:
- "recovery value", "recovery potential", "expected recovery" → SORT: recovery_potential
- "net value", "dollar value", "value" → SORT: net_value
- "confidence", "correction confidence" → SORT: correction_confidence
- "effort", "hours", "effort hours" → SORT: effort_hours

When a SORT instruction is given, confirm with exactly one sentence:
"Done — sorted by [field name] descending."
Do NOT include a SLIDERS instruction when responding to a sort request.

Always include 1-2 contextual follow-up prompts at the END:
PROMPTS: "What's the total value here?", "How much effort am I signing up for?"

Make PROMPTS the natural next step given what was just discussed:
- After filtering → suggest exploration ("What's the denial risk on these?", "Show all claims instead")
- After showing a view → suggest exploration ("What's the total value here?", "Show highest confidence claims")
- After answering totals → suggest action ("Show me all 60 claims", "What's the best I can recover today?")
- After switching modes → suggest navigation ("Go back to filtered view", "What's the riskiest claim here?")
- After sorting → suggest next step ("Now filter to high confidence only", "What's the total recovery value here?")
Never use named group labels in suggested prompts.

The SLIDERS, MODE, FILTER, SORT, and PROMPTS lines are parsed by the frontend.
They will not be shown to the analyst.

------------------------------------
EXAMPLE CORRECT RESPONSES
------------------------------------

Request: "show me high confidence, low effort claims"
Response:
Done — I've shifted your weights toward high confidence, low effort.
SLIDERS: financial=0.5, confidence=0.9, effort=0.9, risk=0.9
PROMPTS: "What's the total value here?", "Show highest value claims instead"

Request: "show me the UnitedHealth missing auth claims"
Response:
Done — filtered to UnitedHealth missing authorization claims.
FILTER: payer=UnitedHealth, issue_type=missing_auth
PROMPTS: "What's the denial risk on these?", "Show all UnitedHealth claims instead"

Request: "show me all claims"
Response:
Done — showing all claims now.
FILTER: none
MODE: unfiltered
PROMPTS: "Go back to filtered view", "What's the riskiest claim here?"

Request: "show me the hidden claims"
Response:
Done — showing all claims now.
MODE: unfiltered
PROMPTS: "Go back to filtered view", "What's the riskiest claim here?"

Request: "rank those claims by recovery"
Response:
Done — sorted by recovery potential descending.
SORT: recovery_potential
PROMPTS: "What's the total recovery value here?", "Filter to high confidence only"

Request: "rank by recovery value"
Response:
Done — sorted by recovery potential descending.
SORT: recovery_potential
PROMPTS: "Now filter to high confidence only", "What's the total recovery value here?"

Request: "sort by effort hours"
Response:
Done — sorted by effort hours descending.
SORT: effort_hours
PROMPTS: "Filter to low effort claims", "What's the total value of these?"

------------------------------------
RESPONSE STYLE
------------------------------------

- Never volunteer claim details, lists, or summaries — the analyst can see the table. Only mention specific claim IDs when directly asked or when one claim is notably different from the others.
- Never use markdown formatting — no headers, no bold, no tables, no bullet points
- Never reproduce or summarize RAG document content directly — use it only to inform your answer
- Match response length to the question:
  - Action responses (moving sliders, switching modes, filtering, sorting): 1 sentence confirmation only
  - Factual questions (specific claim data, totals, counts): 1 sentence with just the numbers — no context, no comparison, no analysis unless explicitly asked
  - Explanatory questions (why is X ranked, what should I focus on, what's X like): 2-3 sentences maximum
- Never explain what you are about to do — just do it
- Never narrate before and after — confirm only after
- Never ask permission — just act
- Never say "want me to..." — just do it
- Never explain slider weights or scores to the analyst
- Never say "certainly" or "of course"
- When adjusting sliders, end with: "Done — I've shifted your weights toward [3-4 words]."
- When switching modes, end with: "Done — showing all claims now."
- When sorting, end with: "Done — sorted by [field name] descending."
- When asked "show me X" without asking for a list, change the table — never list in chat
- Only provide a list in chat if explicitly asked ("give me a list", "tell me which")
- Use language such as "projected", "estimated", "likely", "historically associated with"
- Do not imply certainty
"""


# ── RAG Retrieval ──────────────────────────────────────────────────────────────

def retrieve_context(query):
    """
    Simple keyword-based RAG retrieval.
    Scans all .txt files in RAG_DIR and returns content from matching files.
    """
    if not os.path.isdir(RAG_DIR):
        return "No additional context retrieved for this query."

    query_lower = query.lower()
    matched = []

    for filename in os.listdir(RAG_DIR):
        if not filename.endswith(".txt"):
            continue
        filepath = os.path.join(RAG_DIR, filename)
        try:
            with open(filepath) as f:
                content = f.read()
            # Match on filename keywords or content keywords
            name_keywords = filename.replace(".txt", "").replace("_", " ").lower()
            if any(word in query_lower for word in name_keywords.split()):
                matched.append(content.strip())
            elif any(word in content.lower() for word in query_lower.split() if len(word) > 4):
                matched.append(content.strip())
        except Exception:
            continue

    if matched:
        return "\n\n---\n\n".join(matched[:2])  # cap at 2 docs to stay within token budget
    return "No additional context retrieved for this query."


# ── Prompt Builder ─────────────────────────────────────────────────────────────

def _build_prompt(message, app_state):
    """
    Fills in the prompt template variables at runtime.
    Returns the fully populated prompt string.
    """
    weights  = app_state.get("weights", {})
    filtered = app_state.get("filtered", True)
    top_n    = app_state.get("top_n", 25)
    visible  = app_state.get("visible_claims", [])
    total    = app_state.get("total_claims", 60)
    all_claims = app_state.get("all_claims", [])

    mode    = "Filtered" if filtered else "Unfiltered"
    showing = f"top {top_n}" if top_n != "all" else "all"

    # {active_weights}
    active_weights = (
        f"Financial Value: {weights.get('financial_value', 0):.0%} | "
        f"Correction Confidence: {weights.get('confidence', 0):.0%} | "
        f"Manual Review Effort: {weights.get('effort', 0):.0%} | "
        f"Risk Tolerance: {weights.get('risk', 0):.0%}"
    )

    # {visible_claims}
    net_recovery = sum(c.get("net_value", 0) for c in visible)
    avg_conf     = (
        sum(c.get("correction_confidence", 0) for c in visible) / len(visible)
        if visible else 0
    )
    total_effort = sum(c.get("effort_hours", 0) for c in visible)

    top5 = visible[:5]
    top5_text = ", ".join(
        f"{c['id']} (net ${c['net_value']:,}, conf {int(c['correction_confidence']*100)}%, "
        f"risk {int(c['denial_risk']*100)}%, {c['effort_hours']}h, {c['payer']}, {c['issue_type']})"
        for c in top5
    )

    visible_claims = (
        f"Mode: {mode} | Showing: {showing} of {total} claims\n"
        f"Visible count: {len(visible)} | Net Recovery: ${net_recovery:,} | "
        f"Avg Confidence: {int(avg_conf*100)}% | Total Effort: {round(total_effort, 2)}h\n"
        f"Top 5: {top5_text}"
    )

    # {total_claims_summary} — full dataset totals
    all_net    = sum(c.get("net_value", 0) for c in all_claims)
    all_effort = sum(c.get("effort_hours", 0) for c in all_claims)

    # Full claim lookup — all 60 claims for individual claim questions
    all_text = " | ".join(
        f"{c['id']}(net=${c['net_value']:,}, conf={int(c['correction_confidence']*100)}%, "
        f"risk={int(c['denial_risk']*100)}%, effort={c['effort_hours']}h, "
        f"payer={c['payer']}, type={c['issue_type']})"
        for c in all_claims
    )

    total_claims_summary = (
        f"All {total} claims: Net Recovery=${all_net:,} | Total Effort={round(all_effort, 2)}h\n"
        f"All claims data: {all_text}"
    )

    # {retrieved_context} — RAG lookup based on analyst message
    retrieved_context = retrieve_context(message)

    # {analyst_request}
    analyst_request = message

    return PROMPT_TEMPLATE.format(
        analyst_request      = analyst_request,
        active_weights       = active_weights,
        visible_claims       = visible_claims,
        total_claims_summary = total_claims_summary,
        retrieved_context    = retrieved_context,
    )


# ── Chat Function ──────────────────────────────────────────────────────────────

def chat(messages, app_state):
    """
    Send a conversation to Claude and return its response.

    messages   — list of {role: "user"|"assistant", content: "..."}
                 Full conversation history including the latest user message.

    app_state  — dict with current app context.

    Returns a dict:
    {
      text:     "Claude's response text (instructions stripped out)",
      sliders:  {financial_value, confidence, effort, risk} or None,
      mode:     "filtered" | "unfiltered" | None,
      filters:  {payer, issue_type} or None,
      sort:     "recovery_potential" | "net_value" | "correction_confidence" | "effort_hours" | None,
      prompts:  ["prompt 1", "prompt 2"] or []
    }
    """

    # Build the fully populated prompt for the latest user message
    latest_message = messages[-1]["content"] if messages else ""
    populated_prompt = _build_prompt(latest_message, app_state)

    # Replace the latest user message content with the populated prompt
    messages_with_context = list(messages)
    if messages_with_context:
        messages_with_context[-1] = {
            "role": "user",
            "content": populated_prompt
        }

    # Truncate history to last 10 messages (5 exchanges) to prevent token limit
    # issues in long sessions. Always keep the last message (the current request).
    MAX_HISTORY = 10
    if len(messages_with_context) > MAX_HISTORY:
        messages_with_context = messages_with_context[-MAX_HISTORY:]

    payload = json.dumps({
        "model":      CLAUDE_MODEL,
        "max_tokens": MAX_TOKENS,
        "messages":   messages_with_context,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type":      "application/json",
            "anthropic-version": "2023-06-01",
            "x-api-key":         os.environ.get("ANTHROPIC_API_KEY", ""),
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data     = json.loads(resp.read())
            raw_text = data["content"][0]["text"]
            return _parse_response(raw_text)

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"Claude API error {e.code}: {error_body}")
        return {
            "text":    "Sorry, I couldn't connect to the AI service. Please try again.",
            "sliders": None,
            "mode":    None,
            "filters": None,
            "sort":    None,
            "prompts": []
        }


# ── Response Parser ────────────────────────────────────────────────────────────

# Valid sort fields — guards against Claude hallucinating a field name
VALID_SORT_FIELDS = {"recovery_potential", "net_value", "correction_confidence", "effort_hours"}

def _parse_response(raw_text):
    """
    Parses Claude's raw response and extracts hidden instructions.
    Returns clean display text plus structured instruction data.
    """
    lines      = raw_text.strip().split("\n")
    text_lines = []
    sliders    = None
    mode       = None
    filters    = None
    sort       = None
    prompts    = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("SLIDERS:"):
            try:
                parts = stripped[len("SLIDERS:"):].strip().split(",")
                sliders = {}
                for part in parts:
                    key, val = part.strip().split("=")
                    sliders[key.strip()] = float(val.strip())
            except Exception as e:
                print(f"Failed to parse SLIDERS: {e}")

        elif stripped.startswith("FILTER:"):
            try:
                filter_raw = stripped[len("FILTER:"):].strip()
                if filter_raw.lower() == "none":
                    filters = {}
                else:
                    filters = {}
                    for part in filter_raw.split(","):
                        key, val = part.strip().split("=")
                        filters[key.strip()] = val.strip()
            except Exception as e:
                print(f"Failed to parse FILTER: {e}")

        elif stripped.startswith("MODE:"):
            mode = stripped[len("MODE:"):].strip().lower()

        elif stripped.startswith("SORT:"):
            field = stripped[len("SORT:"):].strip().lower()
            if field in VALID_SORT_FIELDS:
                sort = field
            else:
                print(f"Ignored unknown SORT field: {field}")

        elif stripped.startswith("PROMPTS:"):
            try:
                prompts_raw = stripped[len("PROMPTS:"):].strip()
                prompts = re.findall(r'"([^"]+)"', prompts_raw)
            except Exception as e:
                print(f"Failed to parse PROMPTS: {e}")

        else:
            text_lines.append(line)

    clean_text = "\n".join(text_lines).strip()

    return {
        "text":    clean_text,
        "sliders": sliders,
        "mode":    mode,
        "filters": filters,
        "sort":    sort,
        "prompts": prompts,
    }
