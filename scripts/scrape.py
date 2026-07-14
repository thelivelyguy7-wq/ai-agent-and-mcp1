import pandas as pd
from google_play_scraper import reviews, Sort
import os
import sys
from datetime import datetime, timedelta

def fetch_reviews_last_12_weeks(app_id="com.revolut.revolut"):
    print(f"Fetching reviews for {app_id} from the last 12 weeks...")
    
    # 12 weeks = 84 days
    cutoff_date = datetime.now() - timedelta(weeks=12)
    print(f"Cutoff Date: {cutoff_date.date()}")
    
    all_reviews = []
    continuation_token = None
    
    # We will fetch in batches of 200
    while True:
        try:
            result, continuation_token = reviews(
                app_id,
                lang='en',
                country='us',
                sort=Sort.NEWEST,
                count=200,
                continuation_token=continuation_token
            )
            
            if not result:
                break
                
            older_than_cutoff = False
            for rev in result:
                # review date is in 'at' field
                review_date = rev.get('at')
                if review_date and review_date < cutoff_date:
                    older_than_cutoff = True
                    break
                all_reviews.append(rev)
                
            print(f"Fetched {len(all_reviews)} reviews so far...")
            
            if older_than_cutoff or continuation_token is None:
                break
                
        except Exception as e:
            print(f"Error fetching batch: {e}")
            break

    if not all_reviews:
        print("No reviews found in the last 12 weeks.")
        return

    df = pd.DataFrame(all_reviews)
    
    # Rename columns to match what our ingestion script expects
    df = df.rename(columns={
        "reviewId": "id",
        "content": "text",
        "score": "rating",
        "at": "date"
    })
    
    # Keep relevant columns
    cols_to_keep = ['id', 'text', 'rating', 'date', 'userName']
    df = df[[col for col in cols_to_keep if col in df.columns]]
    
    df['title'] = ""
    df['language'] = "en"
    
    os.makedirs('data', exist_ok=True)
    csv_path = 'data/playstore_reviews.csv'
    df.to_csv(csv_path, index=False)
    print(f"Successfully saved {len(df)} reviews from the last 12 weeks to {csv_path}")

if __name__ == "__main__":
    fetch_reviews_last_12_weeks()
