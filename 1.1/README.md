# Claims Optimization App

AI-assisted healthcare claims prioritization tool. Analysts interact with a chat interface to filter, sort, and prioritize claims for correction using natural language.

---

## What it does

- Ranks claims by weighted score across financial value, confidence, effort, and risk
- Chat interface powered by Claude — filter, sort, and ask questions in plain English
- Filter pills show active filters with individual clear buttons
- Sortable column headers — click to sort, click again to toggle direction
- RAG documents provide payer and issue type context to Claude
- Summary metrics update in real time as filters and weights change

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, vanilla JS |
| AI | Claude API (claude-sonnet-4-5) |
| Data | claims.json (60 claims) |
| Context | Keyword-based RAG (4 documents) |
| Prompts | Named-variable prompt template |

---

## Setup

**Requirements:** Python 3, pip

```bash
# Clone or copy the project folder
cd tradeoffs-app

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install flask anthropic

# Set your API key (add to ~/.zshrc for persistence)
export ANTHROPIC_API_KEY="your-key-here"

# Run
python3 app.py
```

Open `http://127.0.0.1:5000` in your browser.

---

## File structure

```
tradeoffs-app/
├── app.py              # Flask server — routes, filtering, scoring orchestration
├── claude_client.py    # Prompt template, RAG retrieval, response parser
├── scoring.py          # Weighted scoring algorithm
├── claims.json         # Dataset — 60 healthcare claims
├── templates/
│   └── index.html      # Single-file frontend
└── rag/
    ├── rag_payer_patterns.txt
    ├── rag_issue_types.txt
    ├── rag_risk_guidance.txt
    ├── rag_effort_guidance.txt
    └── rag_registry.txt
```

---

## How it works

1. Analyst types a message in the chat panel
2. `app.py` packages the message with current app state (weights, visible claims)
3. `claude_client.py` builds a prompt, retrieves relevant RAG documents, calls Claude
4. Claude returns a response with optional instructions — `SLIDERS`, `FILTER`, `SORT`
5. `app.py` parses instructions, re-ranks claims, returns updated data
6. Frontend updates table, metrics, and filter pills

---

## Chat capabilities

| What you type | What happens |
|---|---|
| "show me easy wins" | Shifts sliders toward high confidence, low effort |
| "show me highest value, higher risk claims" | Shifts sliders toward financial value |
| "show me UnitedHealth claims" | Hard filters table to that payer |
| "with confidence below 80%" | Stacks a confidence filter |
| "show claims under $20k" | Filters by net value |
| "rank by recovery value" | Sorts table by raw field |
| "what's the total effort here?" | Claude answers from visible claims |
| "is UnitedHealth worth the effort?" | Claude draws on RAG payer context |

---

## Filter fields

`payer` · `issue_type` · `min_confidence` · `max_confidence` · `min_net_value` · `max_net_value`

**Confidence tiers:** High = 80%+ · Medium = 50–79% · Low = below 50%

---

## Project context

Built as a UX-led prototype to explore AI-assisted decision support in healthcare claims processing. Developed iteratively across phases:

- **Phase 1–2** — Data, scoring algorithm, basic UI
- **Phase 3** — Claude chat integration, RAG
- **Phase 3a** — Extended RAG, keyword retrieval
- **Phase 3b** — Sorting, filter pills, extended filters, stability fixes
- **Phase 4** *(planned)* — File split, per-claim detail panel, tradeoff simulation

**Author:** Deanna Aho
