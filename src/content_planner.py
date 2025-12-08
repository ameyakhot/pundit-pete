import json
import os
from datetime import datetime, timedelta
import random

BACKLOG_FILE = "content_backlog.json"
HISTORY_FILE = "history.json"


class ContentPlanner:
    def __init__(self):
        self.backlog = self._load_json(BACKLOG_FILE, [])
        self.history = self._load_json(HISTORY_FILE, [])

    def _load_json(self, filepath, default):
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                try:
                    data = json.load(f)
                    # Handle new history format (dict with posts) vs old format (list)
                    if (
                        filepath == HISTORY_FILE
                        and isinstance(data, dict)
                        and "posts" in data
                    ):
                        # Extract posts list from new format for backward compatibility
                        return data.get("posts", [])
                    return data
                except json.JSONDecodeError:
                    return default
        return default

    def _save_json(self, filepath, data):
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def update_backlog(self, new_articles):
        """
        Adds new articles to the backlog if they haven't been seen before.
        """
        existing_links = {item["link"] for item in self.backlog}
        # Handle both list format (old) and dict format (new) for history
        if isinstance(self.history, list):
            posted_links = {item["link"] for item in self.history if "link" in item}
        else:
            # New format: history is a dict with 'posts' key
            posts = (
                self.history.get("posts", []) if isinstance(self.history, dict) else []
            )
            posted_links = {item["link"] for item in posts if "link" in item}

        added_count = 0
        for article in new_articles:
            if (
                article["link"] not in existing_links
                and article["link"] not in posted_links
            ):
                self.backlog.append(article)
                added_count += 1

        if added_count > 0:
            self._save_json(BACKLOG_FILE, self.backlog)
            print(f"[PLANNER] Added {added_count} new items to backlog.")

    def select_next_post(self):
        """
        Decides what to post based on strategy.
        Strategy:
        1. If there's 'Breaking News' (< 24h old), post that immediately.
        2. Else, pick the oldest item from the backlog (FIFO) to ensure coverage.
        """
        if not self.backlog:
            return None

        # Sort backlog by date (newest first for checking breaking news)
        # Note: Depending on format, string sort might suffice or need parsing
        # Simple heuristic: Just iterate.

        current_time = datetime.now()
        breaking_news = None

        for item in self.backlog:
            try:
                pub_date = datetime.strptime(item["published"], "%Y-%m-%d %H:%M:%S")
                age = current_time - pub_date
                if age < timedelta(hours=24):
                    breaking_news = item
                    break
            except ValueError:
                continue

        if breaking_news:
            print(f"[PLANNER] Strategy: BREAKING NEWS found ({breaking_news['title']})")
            return breaking_news

        # Fallback: Pick a random item or the latest one from backlog if no breaking news
        # Let's pick the latest one to keep it relatively fresh
        selected = self.backlog[0]
        print(f"[PLANNER] Strategy: BACKLOG item selected ({selected['title']})")
        return selected

    def mark_as_posted(self, article):
        """
        Moves an item from backlog to history.
        Note: Content Manager handles enriched history. This maintains simple format for backward compatibility.
        """
        # Remove from backlog
        self.backlog = [
            item for item in self.backlog if item["link"] != article["link"]
        ]
        self._save_json(BACKLOG_FILE, self.backlog)

        # Add to history (simple format for backward compatibility)
        # Content Manager will add enriched data separately
        record = {
            "title": article["title"],
            "link": article["link"],
            "posted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Handle both old format (list) and new format (dict)
        if isinstance(self.history, list):
            self.history.append(record)
            self._save_json(HISTORY_FILE, self.history)
        else:
            # New format: update posts list
            if not isinstance(self.history, dict):
                self.history = {"posts": [], "metadata": {}}
            posts = self.history.get("posts", [])
            posts.append(record)
            self.history["posts"] = posts
            self._save_json(HISTORY_FILE, self.history)


if __name__ == "__main__":
    # Test
    planner = ContentPlanner()
    print(f"Backlog size: {len(planner.backlog)}")
