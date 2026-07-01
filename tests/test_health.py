def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["service"] == "giraffe-language-skill"
    assert "version" in body


def test_models(client):
    resp = client.get("/v1/models")
    assert resp.status_code == 200
    body = resp.json()
    assert body["provider"] == "mock"
    assert body["canonical_language"] == "en"
    assert "zh-en" in body["available_language_pairs"]
    assert "en-ja" in body["available_language_pairs"]
    assert body["models"] == []
