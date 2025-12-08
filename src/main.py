import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Import modules
from news_scout import fetch_news
from content_planner import ContentPlanner
from content_manager import ContentManager
from linkedin_api import post_to_linkedin

# Load env vars
load_dotenv()


def main():
    print(f"--- Starting Daily AI Consultant Post: {datetime.now()} ---")

    # 1. Check Env
    if not os.getenv("GROQ_API_KEY"):
        print("[ERROR] GROQ_API_KEY missing.")
        sys.exit(1)

    # 2. Initialize Components
    planner = ContentPlanner()
    content_manager = ContentManager()

    # 3. Scout Phase (Feed the Planner)
    print("[1/4] Scouting for AI industry insights...")
    articles = fetch_news(hours=168)  # Look back 7 days
    planner.update_backlog(articles)

    # 4. Plan Phase (Decide what to post)
    print("[2/4] Planning thought leadership content...")
    target_article = planner.select_next_post()

    if not target_article:
        print("[INFO] No content available in backlog to post.")
        # Optional: Here we could trigger a "Generate Evergreen Content" function
        sys.exit(0)

    print(f"[INFO] Selected topic: {target_article['title']}")

    # 5. Content Manager Phase (Analyze context and generate strategic guidance)
    print(
        "[3/5] Content Manager analyzing context and generating strategic guidance..."
    )
    strategic_guidance = content_manager.generate_strategic_guidance(target_article)

    print(
        f"[CONTENT MANAGER] Topic Focus: {strategic_guidance.get('topic_focus', 'N/A')}"
    )
    print(
        f"[CONTENT MANAGER] Content Angle: {strategic_guidance.get('content_angle', 'N/A')}"
    )
    print(
        f"[CONTENT MANAGER] Storytelling Framework: {strategic_guidance.get('storytelling_framework', 'N/A')}"
    )

    # 5.5. Memory Phase (Retrieve recent posts for context)
    print("[4/5] Retrieving memory context from recent posts...")
    memory_context = content_manager.get_memory_context(count=5)
    if memory_context:
        print(f"[MEMORY] Retrieved {len(memory_context)} recent posts for context")
    else:
        print("[MEMORY] No previous posts found - this will be the first post")

    # 6. Edit Phase (Content Manager calls AI Consultant with guidance and memory)
    print(
        "[5/5] Content Manager calling AI Consultant with strategic guidance and memory..."
    )
    post_text = content_manager.call_ai_consultant(
        target_article, strategic_guidance, memory_context=memory_context
    )

    if not post_text:
        print("[ERROR] Failed to generate post content.")
        sys.exit(1)

    print("\n" + "=" * 20 + " FINAL POST " + "=" * 20)
    print(post_text)
    print("=" * 52 + "\n")

    # 7. Publish Phase
    print("[5/5] Publishing to LinkedIn personal profile...")
    success = post_to_linkedin(
        text=post_text,
        article_url=target_article["link"],
        article_title=target_article["title"],
        use_company_page=False,  # Post to personal profile
    )

    # 8. Commit Phase (Update Memory)
    if success:
        # Update planner's simple history
        planner.mark_as_posted(target_article)

        # Update content manager's enriched history with post content
        post_data = {
            "title": target_article["title"],
            "link": target_article["link"],
            "storytelling_framework": strategic_guidance.get(
                "storytelling_framework", "Hook-Story-Lesson"
            ),
        }
        content_manager.update_history_with_engagement(
            post_data,
            post_content=post_text,  # NEW: Save actual post content
            engagement_data=None,
        )

        print("[SUCCESS] Thought leadership post published and marked in history.")
    else:
        print("[ERROR] Failed to post to LinkedIn. History not updated.")
        sys.exit(1)


if __name__ == "__main__":
    main()
