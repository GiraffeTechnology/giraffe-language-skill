ZH_RFQ = "询价 5000 件格子衬衫，45天交东京，高品质，请给我一个初步报价"


def test_normalize_zh_rfq(client):
    resp = client.post(
        "/v1/inbound/normalize",
        json={
            "source_text": ZH_RFQ,
            "source_language": "auto",
            "canonical_language": "en",
            "domain_hint": "trade_rfq",
            "source_channel": "wechat",
        },
    )
    assert resp.status_code == 200
    body = resp.json()

    assert body["language"]["detected"] == "zh"
    assert body["canonical_language"] == "en"

    ev = body["field_evidence"]
    assert ev["quantity"]["value"] == 5000
    assert ev["quantity"]["source"] == "raw_rule"
    assert ev["destination"]["value"] == "Tokyo"
    assert ev["lead_time_days"]["value"] == 45
    assert ev["quality_level"]["value"] == "high"
    assert "plaid" in ev["product_modifier"]["value"]

    # Canonical English text carries the glossary-normalized business terms.
    canonical = body["canonical_text"]
    assert "Tokyo" in canonical
    assert "plaid" in canonical
    assert "shirt" in canonical

    assert body["translation"]["provider"] == "mock"
    assert body["translation"]["glossary_version"] == "2026-07-01"
