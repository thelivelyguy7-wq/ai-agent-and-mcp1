import pytest
import json
import csv
from src.ingestion import load_reviews

def test_load_reviews_csv(tmp_path):
    csv_file = tmp_path / "reviews.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "text", "rating", "date", "language"])
        writer.writerow(["1", "This is a great app, I love it so much!", "5", "2023-10-25T14:30:00Z", "en"])
        writer.writerow(["2", "Bad", "1", "2023-10-25T14:30:00Z", "en"]) # Too short (<8 words)
        writer.writerow(["3", "This app is terrible because it crashes all the time 😂", "1", "2023-10-25T14:30:00Z", "en"]) # Emoji
        writer.writerow(["4", "Esta aplicación es muy buena y me gusta mucho.", "5", "2023-10-25T14:30:00Z", "es"]) # Non-English
    
    reviews = load_reviews(csv_file)
    assert len(reviews) == 1
    assert reviews[0].id == "1"

def test_load_reviews_json(tmp_path):
    json_file = tmp_path / "reviews.json"
    data = [
        {"id": "1", "text": "This is a great app, I love it so much!", "rating": 5, "date": "2023-10-25T14:30:00Z", "language": "en"},
        {"id": "2", "text": "This is a great app, contact user@example.com for more information.", "rating": 5, "date": "2023-10-25T14:30:00Z", "language": "en"}
    ]
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
        
    reviews = load_reviews(json_file)
    assert len(reviews) == 2
    assert "user@example.com" not in reviews[1].text
    assert "[EMAIL REDACTED]" in reviews[1].text

def test_load_reviews_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_reviews("nonexistent.csv")

def test_load_reviews_unsupported_format(tmp_path):
    txt_file = tmp_path / "reviews.txt"
    txt_file.write_text("dummy")
    with pytest.raises(ValueError, match="Unsupported file format"):
        load_reviews(txt_file)

def test_load_reviews_empty_dataset(tmp_path):
    json_file = tmp_path / "empty.json"
    json_file.write_text("[]")
    with pytest.raises(ValueError, match="Empty dataset provided"):
        load_reviews(json_file)
