from giraffe_language_skill.language import detect_language


def test_detect_chinese():
    result = detect_language("询价 5000 件格子衬衫，45天交东京")
    assert result.detected == "zh"
    assert result.confidence > 0.5


def test_detect_japanese():
    result = detect_language("5000枚のチェック柄シャツを45日以内に東京へ納品してください")
    assert result.detected == "ja"
    assert result.confidence > 0.5


def test_detect_english():
    result = detect_language("Order 5000 plaid shirts to Osaka within 45 days.")
    assert result.detected == "en"


def test_declared_language_is_trusted():
    result = detect_language("anything", declared="zh")
    assert result.detected == "zh"
    assert result.confidence >= 0.9
