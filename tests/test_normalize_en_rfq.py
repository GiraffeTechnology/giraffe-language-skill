EN_RFQ = "Inquiry: Order 5000 plaid shirts, to be shipped to Osaka within 45 days."


def test_normalize_en_rfq_passthrough(client):
    resp = client.post(
        "/v1/inbound/normalize",
        json={
            "source_text": EN_RFQ,
            "source_language": "auto",
            "canonical_language": "en",
            "domain_hint": "trade_rfq",
        },
    )
    assert resp.status_code == 200
    body = resp.json()

    assert body["language"]["detected"] == "en"
    # en -> en requires no translation.
    assert body["translation"]["model"] == "passthrough"
    assert "Osaka" in body["canonical_text"]

    ev = body["field_evidence"]
    assert ev["quantity"]["value"] == 5000
    assert ev["destination"]["value"] == "Osaka"
    assert ev["lead_time_days"]["value"] == 45
    assert "plaid" in ev["product_modifier"]["value"]


def test_normalize_english_shipped_to_singapore_destination(client):
    resp = client.post(
        "/v1/inbound/normalize",
        json={
            "source_text": "Inquiry: Order 5000 plaid shirts, to be shipped to Singapore within 45 days.",
            "source_language": "auto",
            "canonical_language": "en",
            "domain_hint": "trade_rfq",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["field_evidence"]["destination"]["value"] == "Singapore"
