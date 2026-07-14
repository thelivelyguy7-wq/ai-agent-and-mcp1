from src.sanitization import sanitize_text, truncate_review

def test_sanitize_text_email():
    text = "Contact me at user@example.com for info."
    result = sanitize_text(text)
    assert result == "Contact me at [EMAIL REDACTED] for info."

def test_sanitize_text_phone():
    text = "Call 555-123-4567 or +1 (800) 555-0199."
    result = sanitize_text(text)
    # The regex might redact multiple parts or the whole thing depending on matches, 
    # but let's check that the phone numbers are gone and REDACTED is present.
    assert "555-123-4567" not in result
    assert "+1 (800) 555-0199" not in result
    assert "[PHONE REDACTED]" in result

def test_sanitize_text_ip():
    text = "Server IP is 192.168.1.1."
    result = sanitize_text(text)
    assert result == "Server IP is [IP REDACTED]."

def test_sanitize_text_no_pii():
    text = "This is a great app!"
    result = sanitize_text(text)
    assert result == text

def test_truncate_review():
    text = "a" * 1005
    result = truncate_review(text, max_length=1000)
    assert len(result) == 1000 + len("... [TRUNCATED]")
    assert result.endswith("... [TRUNCATED]")

def test_truncate_review_short():
    text = "short text"
    result = truncate_review(text, max_length=1000)
    assert result == "short text"
