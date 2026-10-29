"""Exercise the real renderers and click handlers in an isolated browser document."""
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]


def run_browser_page(tmp_path, page):
    browser = shutil.which("chromium") or shutil.which("google-chrome")
    if not browser:
        for base in (os.environ.get("PROGRAMFILES(X86)", ""), os.environ.get("PROGRAMFILES", "")):
            candidate = Path(base) / "Microsoft/Edge/Application/msedge.exe"
            if candidate.is_file():
                browser = str(candidate)
                break
    if not browser:
        pytest.skip("Chromium or Edge is required for the DOM security test")
    document = tmp_path / "xss.html"
    document.write_text(page, encoding="utf-8")
    completed = subprocess.run([
        browser, "--headless", "--disable-gpu", "--no-first-run", "--disable-extensions",
        f"--user-data-dir={tmp_path / 'browser-profile'}", "--virtual-time-budget=2000",
        "--dump-dom", document.as_uri(),
    ], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
    assert completed.returncode == 0, completed.stderr
    return completed.stdout


def test_untrusted_strings_stay_data_on_click(tmp_path):
    sources = "\n".join((ROOT / "static/js" / name).read_text(encoding="utf-8") for name in ("admin.js", "events.js"))
    payloads = ["O'Brien", "');window.__xss=1;//", '\"><img src=x onerror="window.__xss=1">']
    page = '''<!doctype html><meta charset="utf-8">
<div id="adminsList"></div><div id="historyList"></div>
<div id="participantsModal"></div><div id="participantsModalTitle"></div><div id="participantsCount"></div>
<table><tbody id="participants-tbody"></tbody></table><div id="eventsGrid"></div>
<pre id="result">pending</pre>
<script>
const realAddListener = document.addEventListener.bind(document);
document.addEventListener = (type, ...args) => { if (type !== 'DOMContentLoaded') realAddListener(type, ...args); };
</script><script>''' + sources.replace("</script>", "<\\/script>") + '''</script><script>
(async () => {
  try {
    for (const payload of PAYLOADS) {
      const confirmations = [];
      const registrations = [];
      window.confirm = text => { confirmations.push(text); return false; };
      window.alert = text => { throw new Error(text); };
      window.openRegModal = (...args) => registrations.push(args);
      window.fetch = async url => ({status: 200, json: async () => {
        if (url === '/api/admin/users/admins') return [{name: payload, email: payload}];
        if (url === '/api/admin/history') return [{id: 1, title: payload, date: '', time: '', location: payload, total_teams: 1, total_players: 1}];
        if (url === '/api/admin/events/1/registrations') return {registrations: [{id: 1, team_name: payload, player_count: 1, members: [], comment: payload}], waitlist: []};
        throw new Error('Unexpected request: ' + url);
      }});
      loadAdmins(); loadHistory(); openParticipantsModal(1);
      eventsData = [{id: 1, title: payload, description: payload, place: payload, tag: payload, total: 10, booked: 0, date: '', time: '', price: 100}];
      renderEvents('all');
      await new Promise(resolve => setTimeout(resolve, 50));
      // Use the visual button selectors so this also detects the original vulnerable renderers.
      for (const selector of ['#adminsList .btn-delete', '#historyList .btn-delete', '#participants-tbody .btn-delete', '#eventsGrid .btn-register']) {
        const button = document.querySelector(selector);
        if (!button) throw new Error('Missing button ' + selector);
        button.click();
      }
      if (window.__xss || document.querySelector('img')) throw new Error('User text executed as HTML/JavaScript');
      if (confirmations.length !== 3 || confirmations.some(text => !text.includes(payload))) throw new Error('Confirmation lost original string');
      if (registrations.length !== 1 || registrations[0][1] !== payload) throw new Error('Registration lost original string');
    }
    document.getElementById('result').textContent = 'passed';
  } catch (error) { document.getElementById('result').textContent = 'failed: ' + error.message; }
})();
</script>'''.replace('PAYLOADS', json.dumps(payloads))
    assert '<pre id="result">passed</pre>' in run_browser_page(tmp_path, page)
