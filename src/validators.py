import logging
import re

logger = logging.getLogger(__name__)

def verify_quotes(generated_text: str, source_reviews: list) -> bool:
    """
    Checks if quotes in the generated text actually exist in the source reviews.
    This prevents LLM hallucinations of quotes.
    """
    # Extract strings enclosed in quotes (handling both standard and directional quotes)
    quotes = re.findall(r'["“](.*?)[”"]', generated_text)
    
    source_texts = [r.text for r in source_reviews]
    # Lowercase and remove extra spaces for fuzzy matching
    all_source_text = " ".join(source_texts).lower()
    all_source_text = re.sub(r'\s+', ' ', all_source_text)
    
    all_valid = True
    for q in quotes:
        if len(q.split()) > 3: # Ignore short quoted words like "the app"
            q_clean = re.sub(r'\s+', ' ', q.lower().strip())
            if q_clean not in all_source_text:
                logger.warning(f"Hallucination detected! Quote not found in source: '{q}'")
                all_valid = False
                
    if all_valid and quotes:
        logger.info("All extracted quotes successfully verified against source.")
        
    return all_valid

def verify_word_count(generated_text: str, max_words: int = 250) -> bool:
    """
    Verifies that the generated text adheres to the word count limit.
    """
    words = generated_text.split()
    word_count = len(words)
    
    if word_count > max_words:
        logger.warning(f"Word count constraint violated: {word_count} words (limit: {max_words})")
        return False
        
    logger.info(f"Word count constraint met: {word_count} words.")
    return True
