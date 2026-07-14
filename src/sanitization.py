import re

# Regex patterns for common PII
# Email regex
EMAIL_REGEX = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
# Phone regex (basic US/International formatting)
PHONE_REGEX = re.compile(r"\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\b")
# IP Address regex
IP_REGEX = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

def sanitize_text(text: str) -> str:
    """
    Removes PII like emails, phone numbers, and IP addresses from the text.
    """
    if not text:
        return ""
    
    # Redact emails
    text = EMAIL_REGEX.sub("[EMAIL REDACTED]", text)
    
    # Redact phone numbers (can be aggressive, but favors privacy)
    text = PHONE_REGEX.sub("[PHONE REDACTED]", text)
    
    # Redact IP addresses
    text = IP_REGEX.sub("[IP REDACTED]", text)
    
    return text

def truncate_review(text: str, max_length: int = 1000) -> str:
    """
    Truncates the review to avoid LLM context overflow.
    Preserves the start of the review which usually contains the main intent.
    """
    if not text:
        return ""
    if len(text) > max_length:
        return text[:max_length] + "... [TRUNCATED]"
    return text
