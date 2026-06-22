from deep_researcher.utils.parsing import extract_json_object, extract_numbered_items


def test_extract_numbered_items_handles_common_formats():
    text = "1. 背景是什么？\n2) 应用有哪些？\n- 风险是什么？"

    assert extract_numbered_items(text, limit=5) == ["背景是什么？", "应用有哪些？", "风险是什么？"]


def test_extract_json_object_handles_fenced_json():
    text = '```json\n{"score": 8, "strengths": ["结构清晰"]}\n```'

    assert extract_json_object(text)["score"] == 8
