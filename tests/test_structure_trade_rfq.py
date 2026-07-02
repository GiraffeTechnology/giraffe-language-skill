ZH_RFQ = "询价 5000 件格子衬衫，45天交东京，高品质，请给我一个初步报价"
EN_RFQ = "Inquiry: Order 5000 plaid shirts, to be shipped to Osaka within 45 days."
JA_FUKUOKA_RFQ = "お問い合わせ：チェック柄シャツ5000枚を注文し、45日以内に福岡へ発送してください。"


def test_structure_zh_rfq(client):
    resp = client.post(
        "/v1/structure/rfq",
        json={"raw_text": ZH_RFQ, "schema_version": "trade_rfq.v1"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["schema"] == "trade_rfq.v1"
    assert body["validation_status"] == "valid"

    s = body["structured"]
    assert s["quantity"] == 5000
    assert s["quantity_unit"] == "pcs"
    assert s["product_name"] == "plaid shirt"
    assert s["product_category"] == "apparel"
    assert "plaid" in s["product_modifier"]
    assert s["destination"] == "Tokyo"
    assert s["lead_time_days"] == 45
    assert s["quality_level"] == "high"
    assert s["intent"] == "preliminary_quote"
    assert body["missing_fields"] == []


def test_structure_zh_los_angeles_destination(client):
    resp = client.post(
        "/v1/structure/rfq",
        json={
            "raw_text": "询价5000件格子衬衫，45天交洛杉矶，高品质，请给我一个初步报价",
            "schema_version": "trade_rfq.v1",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["validation_status"] == "valid"

    s = body["structured"]
    assert s["quantity"] == 5000
    assert s["product_name"] == "plaid shirt"
    assert s["destination"] == "Los Angeles"
    assert s["lead_time_days"] == 45
    assert s["quality_level"] == "high"
    assert body["missing_fields"] == []


def test_structure_en_rfq(client):
    resp = client.post(
        "/v1/structure/rfq",
        json={"raw_text": EN_RFQ, "canonical_text": EN_RFQ},
    )
    assert resp.status_code == 200
    s = resp.json()["structured"]
    assert s["quantity"] == 5000
    assert s["quantity_unit"] == "pcs"
    assert s["product_name"] == "plaid shirt"
    assert s["destination"] == "Osaka"
    assert s["lead_time_days"] == 45
    assert resp.json()["validation_status"] == "valid"


def test_structure_ja_fukuoka_destination(client):
    resp = client.post(
        "/v1/structure/rfq",
        json={"raw_text": JA_FUKUOKA_RFQ, "schema_version": "trade_rfq.v1"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["validation_status"] == "valid"

    s = body["structured"]
    assert s["quantity"] == 5000
    assert s["quantity_unit"] == "pcs"
    assert s["product_name"] == "plaid shirt"
    assert s["destination"] == "Fukuoka"
    assert s["lead_time_days"] == 45
    assert body["missing_fields"] == []


def test_structure_english_shipped_to_singapore_destination(client):
    text = "Inquiry: Order 5000 plaid shirts, to be shipped to Singapore within 45 days."
    resp = client.post(
        "/v1/structure/rfq",
        json={"raw_text": text, "canonical_text": text},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["validation_status"] == "valid"
    assert body["structured"]["destination"] == "Singapore"
    assert body["missing_fields"] == []
