def test_admin_page_has_poster_block(admin_client):
    html = admin_client.get("/admin").get_data(as_text=True)
    assert "Афиша <span>месяца</span>" in html
    assert 'id="posterFileInput"' in html
    assert 'id="posterUploadBtn"' in html
    assert 'id="posterRemoveBtn"' in html
    assert "js/admin.js" in html
