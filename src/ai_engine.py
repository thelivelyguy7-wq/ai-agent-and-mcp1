import os
import time
import logging
from groq import Groq
from src.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.validators import verify_quotes, verify_word_count

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        # Ensure API key is available
        api_key = os.getenv("LLM_API_KEY")
        if not api_key:
            logger.warning("LLM_API_KEY is not set. API calls will fail.")
            
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        
    def generate_pulse(self, reviews: list, max_retries=3) -> str:
        """
        Generates the pulse document using the Groq API.
        Implements exponential backoff for rate limits.
        """
        # Because of strict Groq free tier limits (e.g. 1k-6k TPM), 
        # we intelligently sample the reviews to fit within ~700 words of context.
        sampled_reviews = self._sample_reviews(reviews, max_words=700)
        
        reviews_text = "\n".join([f"- [Rating: {r.rating}/5] {r.text}" for r in sampled_reviews])
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(reviews_text=reviews_text)}
        ]
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Invoking LLM (Attempt {attempt + 1})...")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.3, # Low temperature for analytical consistency
                    max_tokens=400   # Limit output to save tokens and enforce brevity
                )
                
                output = response.choices[0].message.content
                
                # Validate output constraints
                verify_word_count(output)
                verify_quotes(output, sampled_reviews)
                
                return output
                
            except Exception as e:
                # Exponential backoff
                wait_time = 2 ** attempt * 5
                logger.error(f"Groq API Error: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                
        raise Exception("Failed to generate pulse document after multiple retries.")

    def _sample_reviews(self, reviews: list, max_words: int) -> list:
        """
        Takes a subset of reviews to fit into the token limit.
        Prioritizes the worst ratings (1 and 2 stars) first to find actionable issues,
        then pads with some 5 star reviews for balance if space permits.
        """
        # Sort by rating ascending
        sorted_reviews = sorted(reviews, key=lambda x: x.rating)
        
        sampled = []
        word_count = 0
        
        for r in sorted_reviews:
            r_words = len(r.text.split())
            if word_count + r_words <= max_words:
                sampled.append(r)
                word_count += r_words
            else:
                break
                
        logger.info(f"Sampled {len(sampled)} reviews ({word_count} words) for the prompt context to respect API limits.")
        return sampled
