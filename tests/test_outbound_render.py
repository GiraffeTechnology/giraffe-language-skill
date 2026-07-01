CANONICAL = (
    "RFQ ready for approval: 5000 pcs high-quality plaid shirts to Tokyo "
    "within 45 days. Two supplier inquiry drafts are pending approval."
)


def test_outbound_render_chinese(client):
    resp = client.post(
        "/v1/outbound/render",
        json={
            "target_language": "zh",
            "target_channel": "wechat",
            "message_type": "rfq_status_update",
            "canonical_text": CANONICAL,
            "tone": "operator_control",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    rendered = body["rendered_text"]

    for expected in [
        "RFQ 已准备好审批",
        "5000 件",
        "高品质格子衬衫",
        "45 天内交东京",
        "供应商询价草稿",
        "等待审批",
    ]:
        assert expected in rendered, f"missing {expected!r} in {rendered!r}"

    assert body["target_language"] == "zh"
    assert body["approval_required"] is True
    assert "glossary" in body["postprocess"]
    assert "channel_formatting" in body["postprocess"]


def test_outbound_render_english_passthrough(client):
    resp = client.post(
        "/v1/outbound/render",
        json={"target_language": "en", "canonical_text": "RFQ ready for approval."},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["rendered_text"] == "RFQ ready for approval."
    assert body["approval_required"] is True
