MISSING_DEST = "询价5000件格子衬衫，45天交货"


def test_missing_destination_needs_confirmation(client):
    resp = client.post("/v1/structure/rfq", json={"raw_text": MISSING_DEST})
    assert resp.status_code == 200
    body = resp.json()
    assert body["validation_status"] == "needs_confirmation"
    assert "destination" in body["missing_fields"]
    # Never hallucinate a destination.
    assert body["structured"]["destination"] is None


def test_missing_quantity_and_destination(client):
    resp = client.post("/v1/structure/rfq", json={"raw_text": "询价格子衬衫，请报价"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["validation_status"] == "needs_confirmation"
    assert "destination" in body["missing_fields"]
    assert "quantity" in body["missing_fields"]


def test_recipient_is_not_treated_as_destination(client):
    # "to <recipient> within <n>" with no shipping/delivery wording must not be
    # mistaken for a destination, or the missing-destination check is silently
    # satisfied by the recipient name.
    text = "Please quote to Buyer within 3 days for 500 plaid shirts."
    resp = client.post("/v1/structure/rfq", json={"raw_text": text, "canonical_text": text})
    assert resp.status_code == 200
    body = resp.json()
    assert body["structured"]["destination"] is None
    assert "destination" in body["missing_fields"]
    assert body["validation_status"] == "needs_confirmation"
