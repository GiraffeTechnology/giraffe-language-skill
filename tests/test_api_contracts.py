"""Contract-level checks that every required endpoint exists and responds."""


def test_healthz_contract(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert set(resp.json()) >= {"ok", "service", "version"}


def test_models_contract(client):
    resp = client.get("/v1/models")
    assert resp.status_code == 200
    assert set(resp.json()) >= {
        "provider",
        "canonical_language",
        "available_language_pairs",
        "models",
    }


def test_normalize_contract(client):
    resp = client.post(
        "/v1/inbound/normalize",
        json={"source_text": "询价 5000 件格子衬衫，45天交东京", "source_language": "auto"},
    )
    assert resp.status_code == 200
    assert set(resp.json()) >= {
        "raw_text",
        "language",
        "canonical_language",
        "canonical_text",
        "field_evidence",
        "translation",
        "warnings",
    }


def test_translate_contract(client):
    resp = client.post(
        "/v1/translate",
        json={
            "source_text": "询价 5000 件格子衬衫，45天交东京",
            "source_language": "zh",
            "target_language": "en",
            "domain_hint": "trade_rfq",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert set(body) >= {
        "source_language",
        "target_language",
        "translated_text",
        "provider",
        "model",
        "warnings",
    }
    assert "Tokyo" in body["translated_text"]


def test_structure_rfq_contract(client):
    resp = client.post("/v1/structure/rfq", json={"raw_text": "询价 5000 件格子衬衫，45天交东京"})
    assert resp.status_code == 200
    assert set(resp.json()) >= {
        "schema",
        "validation_status",
        "structured",
        "missing_fields",
        "confidence_score",
        "field_sources",
    }


def test_structure_apparel_contract(client):
    resp = client.post(
        "/v1/structure/apparel-customization",
        json={"raw_text": "我要定制 200 件白色纯棉衬衣，男款，东京交货"},
    )
    assert resp.status_code == 200
    assert resp.json()["schema"] == "apparel_customization.v1"


def test_outbound_render_contract(client):
    resp = client.post(
        "/v1/outbound/render",
        json={"target_language": "zh", "canonical_text": "RFQ ready for approval."},
    )
    assert resp.status_code == 200
    assert set(resp.json()) >= {
        "target_language",
        "rendered_text",
        "provider",
        "postprocess",
        "approval_required",
    }
