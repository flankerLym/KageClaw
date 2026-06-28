from shibaclaw.thinkers.base import Thinker


def test_sanitize_empty_content_early_return():
    msg = {"role": "user", "content": "hello"}
    messages = [msg]
    sanitized = Thinker._sanitize_empty_content(messages)
    assert sanitized[0] is msg


def test_sanitize_empty_content_empty_string():
    messages = [
        {"role": "user", "content": ""},
        {"role": "assistant", "content": "", "tool_calls": [{"id": "tc1"}]},
        {"role": "assistant", "content": ""},
    ]
    sanitized = Thinker._sanitize_empty_content(messages)

    assert sanitized[0]["content"] == "(empty)"
    assert sanitized[1]["content"] is None
    assert sanitized[2]["content"] == "(empty)"


def test_sanitize_empty_content_list():
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "hello"},
                {"type": "text", "text": ""},
                {"type": "image_url", "image_url": {"url": "data:image/png"}, "_meta": {"path": "test"}},
            ],
        }
    ]
    sanitized = Thinker._sanitize_empty_content(messages)

    content = sanitized[0]["content"]
    assert len(content) == 2
    assert content[0] == {"type": "text", "text": "hello"}
    assert content[1] == {"type": "image_url", "image_url": {"url": "data:image/png"}}
