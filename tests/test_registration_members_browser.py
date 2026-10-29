from pathlib import Path

from tests.test_xss_browser import run_browser_page


def test_registration_without_member_controls(user, tmp_path):
    html = user.get('/').get_data(as_text=True)
    modal = html[html.index('<div class="modal-overlay" id="regModal"'):html.index('<!-- 6.')]
    assert 'regAddMember' not in modal
    assert 'Участники команды' not in modal
    source = (Path(__file__).resolve().parents[1] / 'static/js/auth.js').read_text(encoding='utf-8')
    page = '<!doctype html><meta charset="utf-8">' + modal + '<pre id="result">pending</pre><script>' + source + '''</script><script>
(async () => {
  try {
    const check = (value, message) => { if (!value) throw new Error(message); };
    window.currentUser = {id: 1, name: 'Captain'};
    window.alert = () => {};
    let created = 0;
    let registered = 0;
    let fail = false;
    let expectedTeam = '5';
    window.fetch = async (url, options = {}) => {
      if (url === '/api/my/teams') return {json: async () => [{id: 5, name: 'Existing', can_manage: true}]};
      const data = JSON.parse(options.body);
      if (url === '/api/teams') {
        created++;
        return {ok: true, json: async () => ({team: {id: 7, name: data.name}})};
      }
      if (url === '/api/register_team') {
        registered++;
        check(String(data.team_id) === expectedTeam && String(data.player_count) === '4' && data.event_id === 9, 'Wrong registration');
        return {ok: !fail, json: async () => fail ? {message: 'Retry'} : {status: 'success'}};
      }
      throw new Error('Unexpected request ' + url);
    };
    await openRegModal(9, 'Game', 'Date', 'Price');
    check(!document.querySelector('#regAddMemberToggle'), 'Member controls present');
    const select = document.getElementById('regTeamSelect');
    select.value = '5';
    await submitReg();
    check(registered === 1 && created === 0, 'Existing registration failed');
    await openRegModal(9, 'Game', 'Date', 'Price');
    showCreateTeam();
    document.getElementById('regNewTeamName').value = "O'Brien <img src=x>";
    expectedTeam = '7'; fail = true;
    await submitReg();
    check(created === 1 && select.value === '7', 'New team not created');
    check(!document.querySelector('img'), 'Unsafe team name rendering');
    fail = false;
    await submitReg();
    check(created === 1 && registered === 3, 'Retry created duplicate team');
    check(!document.querySelector('#regModal .btn-submit').disabled, 'Button left disabled');
    document.getElementById('result').textContent = 'passed';
  } catch (error) { document.getElementById('result').textContent = 'failed: ' + error.message; }
})();
</script>'''
    output = run_browser_page(tmp_path, page)
    assert '<pre id="result">passed</pre>' in output, output[-3500:]
