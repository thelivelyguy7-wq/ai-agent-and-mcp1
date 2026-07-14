import csv
import json
import logging
import emoji
from pathlib import Path
from typing import List, Dict, Any, Union
from pydantic import ValidationError

from src.models import Review
from src.sanitization import sanitize_text, truncate_review

logger = logging.getLogger(__name__)

def load_reviews(file_path: Union[str, Path]) -> List[Review]:
    """
    Loads, sanitizes, and validates reviews from a CSV or JSON file.
    
    Args:
        file_path: Path to the CSV or JSON export file.
        
    Returns:
        List[Review]: A list of validated Review objects.
        
    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the dataset is empty or unsupported format.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    raw_data: List[Dict[str, Any]] = []
    
    # Parse file based on extension
    if path.suffix.lower() == '.csv':
        with open(path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            raw_data = list(reader)
    elif path.suffix.lower() == '.json':
        with open(path, mode='r', encoding='utf-8') as f:
            raw_data = json.load(f)
    else:
        raise ValueError(f"Unsupported file format '{path.suffix}'. Only .csv and .json are supported.")
        
    if not raw_data:
        raise ValueError("Empty dataset provided.")
        
    valid_reviews = []
    
    for row in raw_data:
        # Normalize keys to handle different export schemas (e.g. 'review_text' vs 'text')
        # Also handles None row in case of malformed list
        if not isinstance(row, dict):
            continue
            
        normalized_row = {str(k).lower().strip(): v for k, v in row.items()}
        
        try:
            # Map raw fields to expected schema
            raw_text = normalized_row.get('text', normalized_row.get('content', normalized_row.get('review', '')))
            
            # Step 1: Sanitize PII
            clean_text = sanitize_text(str(raw_text))
            
            # Step 2: Truncate excessively long reviews
            clean_text = truncate_review(clean_text)
            
            # Rule 1: Reviews which have less than 8 words are not required
            if len(clean_text.split()) < 8:
                continue
                
            # Rule 2: Reviews which have emoji are not required
            if emoji.emoji_count(clean_text) > 0:
                continue
            
            raw_rating = normalized_row.get('rating', normalized_row.get('score', normalized_row.get('star', 0)))
            raw_date = normalized_row.get('date', normalized_row.get('at', normalized_row.get('created_at')))
            raw_title = normalized_row.get('title', '')
            
            review_data = {
                'id': normalized_row.get('id', normalized_row.get('review_id', normalized_row.get('reviewid'))),
                'text': clean_text,
                'rating': int(raw_rating) if raw_rating else 0,
                'date': raw_date,
                'title': sanitize_text(str(raw_title)) if raw_title else None,
                'language': normalized_row.get('language', 'en')
            }
            
            # Step 3: Schema Validation
            review = Review(**review_data)
            
            # MVP specific: Filter out non-English reviews
            # (Based on open question in implementation plan, filtering out is safer for MVP)
            if review.language and review.language.lower() != 'en':
                continue
                
            valid_reviews.append(review)
            
        except (ValidationError, ValueError) as e:
            # Log the malformed row and skip
            logger.warning(f"Skipping malformed row: {e}")
            continue
            
    if not valid_reviews:
        raise ValueError("No valid English reviews found in the dataset after validation and filtering.")
        
    return valid_reviews
