JA_FUKUOKA_RFQ = "お問い合わせ：チェック柄シャツ5000枚を注文し、45日以内に福岡へ発送してください。"


def test_normalize_ja_fukuoka_destination(client):
    resp = client.post(
        "/v1/inbound/normalize",
        json={
            "source_text": JA_FUKUOKA_RFQ,
            "source_language": "auto",
            "canonical_language": "en",
            "domain_hint": "trade_rfq",
            "source_channel": "wechat",
        },
    )
    assert resp.status_code == 200
    body = resp.json()

    assert body["language"]["detected"] == "ja"
    ev = body["field_evidence"]
    assert ev["destination"]["value"] == "Fukuoka"
    assert ev["destination"]["source"] == "raw_rule+glossary"
    assert ev["quantity"]["value"] == 5000
    assert ev["lead_time_days"]["value"] == 45
    assert "plaid" in ev["product_modifier"]["value"]

    canonical = body["canonical_text"]
    assert "Fukuoka" in canonical
    assert "plaid" in canonical
    assert "shirt" in canonical
