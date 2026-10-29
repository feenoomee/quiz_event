from pathlib import Path

from tests.test_xss_browser import run_browser_page


def test_add_member_form_in_browser(tmp_path):
    source = "\n".join((Path(__file__).resolve().parents[1] / "static/js" / name).read_text(encoding="utf-8") for name in ("profile.js", "auth.js"))
    page = '''<!doctype html><meta charset="utf-8"><div id="teamsList"></div><div id="regList"></div><select id="regTeamSelect"></select><pre id="result">pending</pre>
<script>
const realAddListener = document.addEventListener.bind(document);
document.addEventListener = (type, ...args) => { if (type !== 'DOMContentLoaded') realAddListener(type, ...args); };
</script><script>''' + source.replace('</script>', '<\\/script>') + '''</script><script>
(async () => {
  try {
    const check = (value, message) => { if (!value) throw new Error(message); };
    const teams = [{id: 7, name: "O'Brien <img src=x>", is_captain: true, can_manage: true, members: [{id: 1, name: 'Captain'}]},
      {id: 8, name: 'Member team', is_captain: false, can_manage: false, members: [{id: 1, name: 'Captain'}]}];
    renderTeams(teams);
    check(document.querySelectorAll('.team-add-toggle').length === 1, 'Only captain can add');
    check(!document.querySelector('img'), 'Team name became HTML');
    const card = document.querySelector('.team-card');
    const toggle = card.querySelector('.team-add-toggle');
    const form = card.querySelector('form');
    check(form.hidden, 'Form starts closed');
    toggle.click();
    check(!form.hidden && document.activeElement === form.elements.email, 'Open form and focus');
    check(toggle.getAttribute('aria-expanded') === 'true', 'Expanded state');
    const status = form.querySelector('[role="status"]');
    const submit = form.querySelector('[type="submit"]');
    let calls = 0;
    let mode = 'error';
    window.fetch = async (url, options) => {
      calls++;
      check(url === '/api/teams/7/join', 'Wrong team');
      check(options.method === 'POST' && JSON.parse(options.body).email === 'player@example.com', 'Wrong payload');
      await new Promise(resolve => setTimeout(resolve, 20));
      if (mode === 'network') throw new Error('offline');
      return {ok: mode === 'success', json: async () => mode === 'success'
        ? {member: {id: 2, name: '<img src=x onerror="window.__xss=1">'}}
        : {message: 'Пользователь уже в команде'}};
    };
    form.elements.email.value = 'player@example.com';
    form.requestSubmit();
    check(submit.disabled, 'Submit not locked');
    form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
    await new Promise(resolve => setTimeout(resolve, 50));
    check(calls === 1 && !submit.disabled, 'Duplicate request or stuck button');
    check(status.textContent === 'Пользователь уже в команде' && status.dataset.error === 'true', 'Missing server error');
    check(form.elements.email.value === 'player@example.com', 'Failed email lost');
    mode = 'network'; form.requestSubmit();
    await new Promise(resolve => setTimeout(resolve, 50));
    check(status.textContent.includes('Ошибка сети') && !submit.disabled, 'Network retry broken');
    mode = 'success'; form.requestSubmit();
    await new Promise(resolve => setTimeout(resolve, 50));
    check(card.querySelectorAll('.team-member-badge').length === 2, 'Member not displayed');
    check(card.querySelector('.team-members-title').textContent === 'Участники (2)', 'Count not updated');
    check(form.elements.email.value === '' && !submit.disabled, 'Form not reset');
    check(!document.querySelector('img') && !window.__xss, 'Member name became HTML');
    renderRegistrations([{id: 1, event_name: 'Game', event_date: '', status: 'pending', can_manage: false}], 'active');
    check(!document.querySelector('#regList .btn-cancel') && !document.querySelector('#regList .btn-main'), 'Member sees captain controls');
    window.fetch = async () => ({json: async () => teams});
    await loadUserTeams();
    const options = document.querySelectorAll('#regTeamSelect option');
    check(options.length === 2 && options[1].value === '7', 'Registration offers a team the user cannot manage');
    document.getElementById('result').textContent = 'passed';
  } catch (error) { document.getElementById('result').textContent = 'failed: ' + error.message; }
})();
</script>'''
    output = run_browser_page(tmp_path, page)
    assert '<pre id="result">passed</pre>' in output, output[-3000:]
