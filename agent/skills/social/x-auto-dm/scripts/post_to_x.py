import os
from dotenv import load_dotenv
import tweepy
import datetime
import time

TODAY = datetime.date.today().strftime('%Y-%m-%d')

# ============================================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================================
load_dotenv()

# Use the exact names from your .env file
X_CONSUMER_KEY        = os.getenv('X_SWRLD_CONSUMER_KEY')
X_CONSUMER_SECRET     = os.getenv('X_SWRLD_CONSUMER_SECRET_KEY')      
X_ACCESS_TOKEN        = os.getenv('X_SWRLD_ACCESS_TOKEN')
X_ACCESS_TOKEN_SECRET = os.getenv('X_SWRLD_ACCESS_TOKEN_SECRET')

# ============================================================================
# AUTH CHECK + POST FUNCTION
# ============================================================================
def verify_x_auth():
    """Quick check if authentication works (read-only call)"""
    if not all([X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET]):
        print("ERROR: Missing one or more X API credentials in .env")
        return False

    client = tweepy.Client(
        consumer_key=X_CONSUMER_KEY,
        consumer_secret=X_CONSUMER_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET,
    )

    try:
        me = client.get_me(user_auth=True)
        print("AUTH CHECK SUCCESSFUL!")
        print(f"→ Account:   @{me.data.username}")
        print(f"→ Name:      {me.data.name}")
        print(f"→ User ID:   {me.data.id}")
        print(f"→ Verified:  {me.data.verified}")
        return True
    except tweepy.TweepyException as e:
        print("AUTH CHECK FAILED")
        print(f"→ {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"→ HTTP {e.response.status_code}")
            print("→ Response:", e.response.text)
        return False
    except Exception as e:
        print(f"Unexpected error during auth check: {type(e).__name__} - {e}")
        return False


def post_to_x(contents, sleep_seconds=1.5):
    """
    Post a single tweet or thread to X.
    
    Args:
        contents: str or list[str] — tweet text or list of texts for a thread
        sleep_seconds: float — delay between tweets in thread (avoid rate limits)
    Returns:
        last_tweet_id or None on failure
    """
    if isinstance(contents, str):
        contents = [contents]  # make single string work like a 1-item thread

    if not verify_x_auth():
        print("Cannot post — authentication failed. Fix credentials / tier first.")
        return None

    client = tweepy.Client(
        consumer_key=X_CONSUMER_KEY,
        consumer_secret=X_CONSUMER_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET,
    )

    try:
        previous_tweet_id = None
        last_tweet_id = None

        for i, text in enumerate(contents, 1):
            print(f"\nPosting tweet {i}/{len(contents)} ...")
            print(f"→ Text ({len(text)} chars): {text[:80]}{'...' if len(text)>80 else ''}")

            kwargs = {"text": text}
            if previous_tweet_id is not None:
                kwargs["in_reply_to_tweet_id"] = previous_tweet_id

            response = client.create_tweet(**kwargs)
            tweet_id = response.data["id"]

            print(f"→ SUCCESS → Tweet ID: {tweet_id}")
            last_tweet_id = tweet_id
            previous_tweet_id = tweet_id

            if i < len(contents):
                print(f"Waiting {sleep_seconds}s before next tweet...")
                time.sleep(sleep_seconds)

        print(f"\nThread posted successfully! Final tweet ID: {last_tweet_id}")
        return last_tweet_id

    except tweepy.TweepyException as e:
        print("\nERROR posting to X:")
        print(f"→ {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"→ HTTP {e.response.status_code}")
            print("→ Response body:", e.response.text)
        return None
    except Exception as e:
        print(f"\nUnexpected error: {type(e).__name__} - {e}")
        return None
    
if __name__ == "__main__":
    post_contents = input("Enter tweet text (or multiple lines for a thread, separated by '\\n'): ")
    post_lines = post_contents.split('\\n')

    print(f"Number of tweets: {len(post_lines)}")
    print("Content:")
    for post in post_lines:
        print(f"Post {post_lines.index(post) + 1}: {post}")
    post_to_x(post_lines)
  
 