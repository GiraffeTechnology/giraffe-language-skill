ZH_APPAREL = "我要定制 200 件白色纯棉衬衣，男款，东京交货"


def test_structure_apparel_customization(client):
    resp = client.post(
        "/v1/structure/apparel-customization",
        json={"raw_text": ZH_APPAREL, "schema_version": "apparel_customization.v1"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["schema"] == "apparel_customization.v1"
    assert body["validation_status"] == "valid"

    s = body["structured"]
    assert s["garment_type"] == "shirt"
    assert s["fabric"] == "cotton"
    assert s["color"] == "white"
    assert s["gender"] == "men"
    assert s["quantity"] == 200
    assert s["delivery_destination"] == "Tokyo"
    assert s["delivery_deadline"] is None
    assert body["missing_fields"] == []
