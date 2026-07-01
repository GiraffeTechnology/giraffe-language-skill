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
