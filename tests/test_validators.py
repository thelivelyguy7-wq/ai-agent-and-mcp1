from src.validators import verify_quotes, verify_word_count
from src.models import Review
from datetime import datetime

def test_verify_quotes_success():
    source_reviews = [
        Review(text="The app is amazing and very fast.", rating=5, date=datetime.now()),
        Review(text="I love the new features.", rating=5, date=datetime.now())
    ]
    generated_text = 'Users stated that "the app is amazing" and they "love the new features".'
    assert verify_quotes(generated_text, source_reviews) is True

def test_verify_quotes_hallucination():
    source_reviews = [
        Review(text="The app is okay.", rating=3, date=datetime.now())
    ]
    generated_text = 'Users stated that "the app is amazing" which is great.'
    assert verify_quotes(generated_text, source_reviews) is False

def test_verify_quotes_ignore_short():
    source_reviews = [
        Review(text="The app is okay.", rating=3, date=datetime.now())
    ]
    # "the app" is only 2 words, should be ignored by the >3 word check
    generated_text = 'Users talked about "the app" being okay.'
    assert verify_quotes(generated_text, source_reviews) is True

def test_verify_word_count_success():
    text = "word " * 200
    assert verify_word_count(text, max_words=250) is True

def test_verify_word_count_failure():
    text = "word " * 251
    assert verify_word_count(text, max_words=250) is False
