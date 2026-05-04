"""
Phase 1 Setup Script — Claims Optimization App
Run this once to create all your project files:

    python3 setup_phase1.py

It will create:
  - app.py
  - claims.json
  - templates/index.html
"""

import os
import json

# ── Create folders ─────────────────────────────────────────
os.makedirs("templates", exist_ok=True)
print("✓ Created templates/ folder")


# ── Write app.py ───────────────────────────────────────────
APP_PY = '''# app.py
# Flask backend for the Claims Optimization app
# Phase 1: Two routes only - serve the page and return claims data

import json
from flask import Flask, render_template, jsonify

# Create the Flask app
# Flask looks for HTML files in a folder called "templates"
app = Flask(__name__)


# Route 1: When someone visits localhost:5000/
# Flask sends back the index.html file
@app.route("/")
def index():
    return render_template("index.html")


# Route 2: When the page loads and asks for claims data
# Flask reads claims.json and sends it back as JSON
@app.route("/claims")
def claims():
    with open("claims.json") as f:
        data = json.load(f)
    return jsonify(data)


# Start the app when you run: python3 app.py
# debug=True means the app auto-reloads when you save changes
if __name__ == "__main__":
    app.run(debug=True)
'''

with open("app.py", "w") as f:
    f.write(APP_PY)
print("✓ Created app.py")


# ── Write claims.json ──────────────────────────────────────
CLAIMS = [
  {"id":"CLM-0041","payer":"Medicare","issue_type":"Coding Error","recovery_potential":8100,"operational_cost":1200,"net_value":6900,"confidence":0.94,"denial_risk":0.08,"effort_hours":3,"status":"Recommended"},
  {"id":"CLM-0042","payer":"BlueCross","issue_type":"Underbilling","recovery_potential":5400,"operational_cost":900,"net_value":4500,"confidence":0.91,"denial_risk":0.11,"effort_hours":4,"status":"Recommended"},
  {"id":"CLM-0043","payer":"Aetna","issue_type":"Missing Auth","recovery_potential":3200,"operational_cost":2800,"net_value":400,"confidence":0.61,"denial_risk":0.44,"effort_hours":18,"status":"Review"},
  {"id":"CLM-0044","payer":"Medicare","issue_type":"Bundling Error","recovery_potential":11200,"operational_cost":1800,"net_value":9400,"confidence":0.88,"denial_risk":0.14,"effort_hours":6,"status":"Recommended"},
  {"id":"CLM-0045","payer":"UnitedHealth","issue_type":"Duplicate","recovery_potential":2100,"operational_cost":3600,"net_value":-1500,"confidence":0.52,"denial_risk":0.61,"effort_hours":22,"status":"Excluded"},
  {"id":"CLM-0046","payer":"Medicaid","issue_type":"Coding Error","recovery_potential":6700,"operational_cost":1100,"net_value":5600,"confidence":0.89,"denial_risk":0.12,"effort_hours":5,"status":"Recommended"},
  {"id":"CLM-0047","payer":"BlueCross","issue_type":"Missing Auth","recovery_potential":4100,"operational_cost":5200,"net_value":-1100,"confidence":0.48,"denial_risk":0.67,"effort_hours":31,"status":"Excluded"},
  {"id":"CLM-0048","payer":"Aetna","issue_type":"Underbilling","recovery_potential":7800,"operational_cost":1400,"net_value":6400,"confidence":0.92,"denial_risk":0.09,"effort_hours":4,"status":"Recommended"},
  {"id":"CLM-0049","payer":"Medicare","issue_type":"Bundling Error","recovery_potential":3900,"operational_cost":2100,"net_value":1800,"confidence":0.73,"denial_risk":0.29,"effort_hours":11,"status":"Review"},
  {"id":"CLM-0050","payer":"UnitedHealth","issue_type":"Coding Error","recovery_potential":9500,"operational_cost":1600,"net_value":7900,"confidence":0.96,"denial_risk":0.06,"effort_hours":3,"status":"Recommended"},
  {"id":"CLM-0051","payer":"Medicaid","issue_type":"Duplicate","recovery_potential":1800,"operational_cost":4100,"net_value":-2300,"confidence":0.44,"denial_risk":0.72,"effort_hours":28,"status":"Excluded"},
  {"id":"CLM-0052","payer":"BlueCross","issue_type":"Coding Error","recovery_potential":5100,"operational_cost":2200,"net_value":2900,"confidence":0.78,"denial_risk":0.24,"effort_hours":9,"status":"Review"},
  {"id":"CLM-0053","payer":"Aetna","issue_type":"Bundling Error","recovery_potential":12400,"operational_cost":2000,"net_value":10400,"confidence":0.87,"denial_risk":0.16,"effort_hours":7,"status":"Recommended"},
  {"id":"CLM-0054","payer":"Medicare","issue_type":"Missing Auth","recovery_potential":2600,"operational_cost":5800,"net_value":-3200,"confidence":0.39,"denial_risk":0.78,"effort_hours":36,"status":"Excluded"},
  {"id":"CLM-0055","payer":"UnitedHealth","issue_type":"Underbilling","recovery_potential":4800,"operational_cost":1300,"net_value":3500,"confidence":0.83,"denial_risk":0.19,"effort_hours":6,"status":"Recommended"}
]

with open("claims.json", "w") as f:
    json.dump(CLAIMS, f, indent=2)
print("✓ Created claims.json (15 claims)")


# ── Write templates/index.html ─────────────────────────────
INDEX_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Claims Optimization</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg:             #F7F6F2;
      --surface:        #FFFFFF;
      --border:         #E2E0D8;
      --border-mid:     #C8C6BC;
      --text-primary:   #1A1916;
      --text-secondary: #6B6860;
      --text-muted:     #9C9A92;
      --accent:         #1A3A2A;
      --accent-light:   #E8F0EB;
      --amber:          #92600A;
      --amber-light:    #FDF3E0;
      --red:            #8B2020;
      --red-light:      #FDEAEA;
      --green:          #1A5C32;
      --green-light:    #E6F4EC;
      --font-body:      'DM Sans', sans-serif;
      --font-mono:      'DM Mono', monospace;
      --radius-sm:      6px;
      --radius-md:      10px;
      --radius-lg:      14px;
    }

    html, body {
      height: 100%;
      font-family: var(--font-body);
      background: var(--bg);
      color: var(--text-primary);
      font-size: 14px;
      line-height: 1.5;
    }

    .shell {
      display: grid;
      grid-template-columns: 1fr 280px;
      grid-template-rows: auto 1fr;
      height: 100vh;
      overflow: hidden;
    }

    /* Header */
    .header {
      grid-column: 1 / -1;
      padding: 14px 24px;
      border-bottom: 1px solid var(--border);
      background: var(--surface);
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .header-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent); }
    .header-label { font-size: 11px; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-muted); }
    .header-title { font-size: 14px; font-weight: 500; color: var(--text-primary); }

    /* Main */
    .main { padding: 24px; overflow-y: auto; display: flex; flex-direction: column; gap: 24px; }

    /* Metric cards */
    .metrics {
      display: grid;
      grid-template-columns: 1.6fr 1fr 1fr 1fr 1fr;
      gap: 1px;
      background: var(--border);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      overflow: hidden;
    }
    .metric-card { background: var(--surface); padding: 18px 20px; display: flex; flex-direction: column; gap: 6px; }
    .metric-label { font-size: 11px; font-weight: 400; color: var(--text-muted); line-height: 1.3; }
    .metric-value { font-size: 28px; font-weight: 300; color: var(--text-primary); letter-spacing: -0.02em; line-height: 1; }
    .metric-card:first-child .metric-value { color: var(--green); font-size: 32px; }

    /* Sliders */
    .sliders-section { display: flex; flex-direction: column; gap: 4px; }
    .sliders-label { font-size: 11px; font-weight: 500; letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px; }
    .sliders-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
    .slider-item { display: flex; flex-direction: column; gap: 8px; }
    .slider-header { display: flex; justify-content: space-between; align-items: baseline; }
    .slider-name { font-size: 12px; font-weight: 500; color: var(--text-secondary); }
    .slider-value { font-size: 11px; font-family: var(--font-mono); color: var(--text-muted); }

    input[type="range"] {
      -webkit-appearance: none; appearance: none;
      width: 100%; height: 2px;
      background: var(--border-mid); border-radius: 2px; outline: none; cursor: pointer;
    }
    input[type="range"]::-webkit-slider-thumb {
      -webkit-appearance: none; appearance: none;
      width: 14px; height: 14px; border-radius: 50%;
      background: var(--accent); border: 2px solid var(--surface);
      box-shadow: 0 0 0 1px var(--accent); cursor: pointer; transition: transform 0.15s ease;
    }
    input[type="range"]::-webkit-slider-thumb:hover { transform: scale(1.2); }

    /* Table */
    .table-section { flex: 1; }
    .table-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
    .table-title { font-size: 11px; font-weight: 500; letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-muted); }
    .table-count { font-size: 11px; font-family: var(--font-mono); color: var(--text-muted); }
    .table-wrap { border: 1px solid var(--border); border-radius: var(--radius-lg); overflow: hidden; background: var(--surface); }

    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    thead th { background: var(--bg); padding: 10px 14px; text-align: left; font-size: 11px; font-weight: 500; letter-spacing: 0.04em; color: var(--text-muted); border-bottom: 1px solid var(--border); white-space: nowrap; }
    thead th.center { text-align: center; }
    tbody tr { border-bottom: 1px solid var(--border); transition: background 0.1s ease; }
    tbody tr:last-child { border-bottom: none; }
    tbody tr:hover { background: var(--bg); }
    tbody td { padding: 11px 14px; color: var(--text-primary); vertical-align: middle; }
    tbody td.center { text-align: center; }

    .claim-id { font-family: var(--font-mono); font-size: 12px; color: var(--text-secondary); }
    .payer-badge { display: inline-block; font-size: 11px; padding: 2px 8px; border-radius: 4px; background: var(--bg); color: var(--text-secondary); border: 1px solid var(--border); }
    .net-positive { color: var(--green); font-weight: 500; }
    .net-negative { color: var(--red); font-weight: 500; }

    .confidence-bar-wrap { display: flex; align-items: center; gap: 8px; }
    .confidence-bar { flex: 1; height: 3px; background: var(--border); border-radius: 2px; overflow: hidden; min-width: 40px; }
    .confidence-fill { height: 100%; background: var(--accent); border-radius: 2px; }
    .confidence-text { font-size: 12px; font-family: var(--font-mono); color: var(--text-secondary); min-width: 32px; }

    .status-badge { display: inline-flex; align-items: center; gap: 5px; font-size: 11px; font-weight: 500; padding: 3px 9px; border-radius: 20px; white-space: nowrap; }
    .status-badge::before { content: ''; width: 5px; height: 5px; border-radius: 50%; }
    .status-recommended { background: var(--green-light); color: var(--green); }
    .status-recommended::before { background: var(--green); }
    .status-review { background: var(--amber-light); color: var(--amber); }
    .status-review::before { background: var(--amber); }
    .status-excluded { background: var(--red-light); color: var(--red); }
    .status-excluded::before { background: var(--red); }

    .cb-wrap { display: flex; flex-direction: column; align-items: center; gap: 3px; }
    .cb-wrap label { font-size: 9px; letter-spacing: 0.04em; text-transform: uppercase; color: var(--text-muted); }
    input[type="checkbox"] { width: 14px; height: 14px; border: 1px solid var(--border-mid); border-radius: 3px; accent-color: var(--accent); cursor: pointer; }

    /* Sidebar */
    .sidebar { border-left: 1px solid var(--border); background: var(--surface); display: flex; flex-direction: column; padding: 20px 16px; gap: 10px; overflow-y: auto; }
    .sidebar-label { font-size: 11px; font-weight: 500; letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-muted); margin-bottom: 4px; }

    .chip { width: 100%; text-align: left; background: var(--bg); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 12px 14px; font-family: var(--font-body); font-size: 13px; color: var(--text-primary); cursor: pointer; line-height: 1.4; transition: background 0.15s ease, border-color 0.15s ease; }
    .chip:hover { background: var(--accent-light); border-color: var(--accent); color: var(--accent); }

    .sidebar-spacer { flex: 1; }

    .chat-messages { display: flex; flex-direction: column; gap: 6px; min-height: 0; }
    .chat-bubble { background: var(--bg); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 8px 12px; font-size: 12px; color: var(--text-secondary); line-height: 1.4; }

    .chat-input-row { display: flex; gap: 6px; align-items: center; border: 1px solid var(--border); border-radius: var(--radius-md); background: var(--bg); padding: 8px 10px; transition: border-color 0.15s ease; }
    .chat-input-row:focus-within { border-color: var(--accent); background: var(--surface); }
    .chat-input { flex: 1; background: none; border: none; outline: none; font-family: var(--font-body); font-size: 13px; color: var(--text-primary); }
    .chat-input::placeholder { color: var(--text-muted); }
    .chat-send { background: none; border: none; cursor: pointer; color: var(--text-muted); padding: 2px 4px; border-radius: 4px; transition: color 0.15s ease; font-size: 16px; line-height: 1; }
    .chat-send:hover { color: var(--accent); }

    .loading-row td { text-align: center; padding: 32px; color: var(--text-muted); font-size: 13px; }
  </style>
</head>
<body>

<div class="shell">

  <header class="header">
    <div class="header-dot"></div>
    <span class="header-label">Scenario</span>
    <span class="header-title">Claim Prioritization</span>
  </header>

  <main class="main">

    <div class="metrics">
      <div class="metric-card">
        <div class="metric-label">Projected<br>Net Recovery</div>
        <div class="metric-value">+$37k</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Prioritized<br>Claims</div>
        <div class="metric-value">240</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">High-Value<br>Corrections</div>
        <div class="metric-value">43</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Avg Correction<br>Confidence</div>
        <div class="metric-value">89%</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Estimated<br>Review Effort</div>
        <div class="metric-value">18h</div>
      </div>
    </div>

    <div class="sliders-section">
      <div class="sliders-label">Optimization weights</div>
      <div class="sliders-grid">
        <div class="slider-item">
          <div class="slider-header">
            <span class="slider-name">Financial Value</span>
            <span class="slider-value" id="val-financial">50%</span>
          </div>
          <input type="range" min="0" max="100" value="50" oninput="document.getElementById('val-financial').textContent = this.value + '%'" />
        </div>
        <div class="slider-item">
          <div class="slider-header">
            <span class="slider-name">Manual Review Effort</span>
            <span class="slider-value" id="val-effort">50%</span>
          </div>
          <input type="range" min="0" max="100" value="50" oninput="document.getElementById('val-effort').textContent = this.value + '%'" />
        </div>
        <div class="slider-item">
          <div class="slider-header">
            <span class="slider-name">Correction Confidence</span>
            <span class="slider-value" id="val-confidence">50%</span>
          </div>
          <input type="range" min="0" max="100" value="50" oninput="document.getElementById('val-confidence').textContent = this.value + '%'" />
        </div>
        <div class="slider-item">
          <div class="slider-header">
            <span class="slider-name">Risk Tolerance</span>
            <span class="slider-value" id="val-risk">50%</span>
          </div>
          <input type="range" min="0" max="100" value="50" oninput="document.getElementById('val-risk').textContent = this.value + '%'" />
        </div>
      </div>
    </div>

    <div class="table-section">
      <div class="table-header">
        <span class="table-title">Claims</span>
        <span class="table-count" id="claim-count">— claims</span>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Claim ID</th>
              <th>Payer</th>
              <th>Issue Type</th>
              <th>Recovery</th>
              <th>Net Value</th>
              <th>Confidence</th>
              <th>Effort</th>
              <th>Status</th>
              <th class="center">Incl.</th>
              <th class="center">Excl.</th>
            </tr>
          </thead>
          <tbody id="claims-body">
            <tr class="loading-row"><td colspan="10">Loading claims…</td></tr>
          </tbody>
        </table>
      </div>
    </div>

  </main>

  <aside class="sidebar">
    <div class="sidebar-label">Suggested prompts</div>
    <button class="chip" onclick="sendPrompt('Show only claims with auto-correction confidence of >80%')">Show only claims with auto-correction confidence of &gt;80%</button>
    <button class="chip" onclick="sendPrompt('Show the safest high-value corrections')">Show the safest high-value corrections</button>
    <button class="chip" onclick="sendPrompt('Exclude claims that decrease net revenue')">Exclude claims that decrease net revenue</button>
    <div class="sidebar-spacer"></div>
    <div class="chat-messages" id="chat-messages"></div>
    <div class="chat-area">
      <div class="chat-input-row">
        <input class="chat-input" type="text" id="chat-input" placeholder="Ask…" onkeydown="if(event.key==='Enter') sendChat()" />
        <button class="chat-send" onclick="sendChat()" title="Send">&#8593;</button>
      </div>
    </div>
  </aside>

</div>

<script>
  fetch('/claims')
    .then(response => response.json())
    .then(data => renderTable(data))
    .catch(() => {
      document.getElementById('claims-body').innerHTML =
        '<tr class="loading-row"><td colspan="10">Could not load claims.</td></tr>';
    });

  function renderTable(claims) {
    document.getElementById('claim-count').textContent = claims.length + ' claims';
    const tbody = document.getElementById('claims-body');
    tbody.innerHTML = '';
    claims.forEach(c => {
      const netClass   = c.net_value >= 0 ? 'net-positive' : 'net-negative';
      const netDisplay = (c.net_value >= 0 ? '+' : '') + '$' + Math.abs(c.net_value).toLocaleString();
      const confidencePct = Math.round(c.confidence * 100);
      const statusClass   = 'status-' + c.status.toLowerCase();
      const row = document.createElement('tr');
      row.innerHTML = `
        <td class="claim-id">${c.id}</td>
        <td><span class="payer-badge">${c.payer}</span></td>
        <td>${c.issue_type}</td>
        <td>$${c.recovery_potential.toLocaleString()}</td>
        <td class="${netClass}">${netDisplay}</td>
        <td>
          <div class="confidence-bar-wrap">
            <div class="confidence-bar"><div class="confidence-fill" style="width:${confidencePct}%"></div></div>
            <span class="confidence-text">${confidencePct}%</span>
          </div>
        </td>
        <td>${c.effort_hours}h</td>
        <td><span class="status-badge ${statusClass}">${c.status}</span></td>
        <td class="center"><div class="cb-wrap"><input type="checkbox" /><label>Incl</label></div></td>
        <td class="center"><div class="cb-wrap"><input type="checkbox" /><label>Excl</label></div></td>
      `;
      tbody.appendChild(row);
    });
  }

  function sendPrompt(text) {
    document.getElementById('chat-input').value = text;
    sendChat();
  }

  function sendChat() {
    const input = document.getElementById('chat-input');
    const text  = input.value.trim();
    if (!text) return;
    addBubble(text);
    input.value = '';
    setTimeout(() => {
      addBubble('AI response coming in Phase 3 — prompt received: "' + text + '"');
    }, 400);
  }

  function addBubble(text) {
    const messages = document.getElementById('chat-messages');
    const bubble   = document.createElement('div');
    bubble.className = 'chat-bubble';
    bubble.textContent = text;
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
  }
</script>
</body>
</html>"""

with open("templates/index.html", "w") as f:
    f.write(INDEX_HTML)
print("✓ Created templates/index.html")


# ── Done ───────────────────────────────────────────────────
print()
print("All files created. Now run:")
print()
print("    python3 app.py")
print()
print("Then open your browser to: http://localhost:5000")
