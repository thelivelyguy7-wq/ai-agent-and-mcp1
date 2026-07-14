import sys
import os

# Ensure we can import the src module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion import load_reviews

def main():
    csv_path = 'data/playstore_reviews.csv'
    
    # Get the raw starting count
    import csv
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        total_raw = sum(1 for row in reader) - 1 # subtract header
        
    print(f"Total raw reviews in CSV: {total_raw}")
    print("Running ingestion and applying Data Quality Filters (>= 8 words, no emojis, english only)...")
    
    try:
        valid_reviews = load_reviews(csv_path)
        print(f"Total valid reviews after filtering: {len(valid_reviews)}")
        print(f"Filtered out: {total_raw - len(valid_reviews)} reviews.")
        
        # Print a sample valid review
        if valid_reviews:
            print("\n--- Sample Valid Review ---")
            print(f"Rating: {valid_reviews[0].rating}/5")
            print(f"Date: {valid_reviews[0].date}")
            print(f"Text: {valid_reviews[0].text}")
            print("---------------------------")
            
    except Exception as e:
        print(f"Error during ingestion: {e}")

if __name__ == "__main__":
    main()
