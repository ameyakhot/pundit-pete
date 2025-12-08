import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Import modules
from news_scout import fetch_news
from content_planner import ContentPlanner
from content_editor import generate_linkedin_post

# Load env vars
load_dotenv()


def main():
    print(f"--- Starting Daily Run: {datetime.now()} ---")

    # 1. Check Env
    if not os.getenv("GROQ_API_KEY"):
        print("[ERROR] GROQ_API_KEY missing.")
        sys.exit(1)

    # 2. Initialize Planner
    planner = ContentPlanner()

    # 3. Scout Phase (Feed the Planner)
    print("[1/3] Scouting for news...")
    articles = fetch_news(hours=168)  # Look back 7 days
    planner.update_backlog(articles)

    # 4. Plan Phase (Decide what to post)
    print("[2/3] Planning content...")
    target_article = planner.select_next_post()

    if not target_article:
        print("[INFO] No content available in backlog to post.")
        # Optional: Here we could trigger a "Generate Evergreen Content" function
        sys.exit(0)

    print(f"[INFO] Selected: {target_article['title']}")

    # 5. Edit Phase (Generate Post)
    print("[3/3] Generating content with Groq...")
    post_text = generate_linkedin_post(
        target_article["title"], target_article["link"], target_article["source"]
    )

    if not post_text:
        print("[ERROR] Failed to generate post content.")
        sys.exit(1)

    print("\n" + "=" * 20 + " FINAL POST " + "=" * 20)
    print(post_text)
    print("=" * 52 + "\n")

    # 6. Commit Phase (Update Memory)
    # Only mark as posted if we actually "posted" (or in this case, generated successfully)
    planner.mark_as_posted(target_article)
    print("[SUCCESS] Article marked as posted in history.")


if __name__ == "__main__":
    main()
