import json
import os
from datetime import datetime, timedelta
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

HISTORY_FILE = "history.json"
STRATEGIC_GOALS_FILE = "strategic_goals.json"


class ContentManager:
    """
    Intelligent Content Manager that maintains context, analyzes patterns,
    and provides strategic guidance to the AI consultant.
    """
    
    def __init__(self):
        self.history = self._load_history()
        self.strategic_goals = self._load_goals()
    
    def _load_history(self):
        """Loads enhanced history structure."""
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                try:
                    data = json.load(f)
                    # Support both old format (list) and new format (dict with posts)
                    if isinstance(data, list):
                        return {"posts": data, "metadata": self._calculate_metadata(data)}
                    return data
                except json.JSONDecodeError:
                    return {"posts": [], "metadata": {}}
        return {"posts": [], "metadata": {}}
    
    def _load_goals(self):
        """Loads strategic goals configuration."""
        if os.path.exists(STRATEGIC_GOALS_FILE):
            with open(STRATEGIC_GOALS_FILE, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return self._default_goals()
        return self._default_goals()
    
    def _default_goals(self):
        """Returns default strategic goals if file doesn't exist."""
        return {
            "primary_goals": [
                {
                    "goal": "establish_ai_expertise",
                    "priority": "high",
                    "target_topics": ["AI", "Machine Learning", "LLMs", "Generative AI"],
                    "target_engagement": 0.15
                },
                {
                    "goal": "build_consulting_authority",
                    "priority": "medium",
                    "target_topics": ["AI Strategy", "Business Impact", "ROI", "Implementation"],
                    "target_engagement": 0.12
                }
            ],
            "content_themes": [
                "explanation",
                "business_impact",
                "practical_applications",
                "industry_trends"
            ]
        }
    
    def _calculate_metadata(self, posts):
        """Calculates metadata from posts list."""
        if not posts:
            return {
                "total_posts": 0,
                "avg_engagement_rate": 0.0,
                "topic_coverage": {}
            }
        
        topic_counter = Counter()
        total_engagement = 0
        posts_with_engagement = 0
        
        for post in posts:
            # Extract topics
            if "topics" in post:
                for topic in post["topics"]:
                    topic_counter[topic] += 1
            
            # Calculate engagement rate
            if "engagement" in post:
                eng = post["engagement"]
                views = eng.get("views", 0)
                if views > 0:
                    likes = eng.get("likes", 0)
                    comments = eng.get("comments", 0)
                    shares = eng.get("shares", 0)
                    engagement_rate = (likes + comments * 2 + shares * 3) / views
                    total_engagement += engagement_rate
                    posts_with_engagement += 1
        
        avg_engagement = total_engagement / posts_with_engagement if posts_with_engagement > 0 else 0.0
        
        return {
            "total_posts": len(posts),
            "avg_engagement_rate": round(avg_engagement, 3),
            "topic_coverage": dict(topic_counter)
        }
    
    def analyze_context(self):
        """
        Analyzes posting history to understand patterns and context.
        Returns analysis dictionary.
        """
        posts = self.history.get("posts", [])
        metadata = self.history.get("metadata", {})
        
        # Analyze recent posts (last 7 days)
        recent_posts = []
        week_ago = datetime.now() - timedelta(days=7)
        
        for post in posts:
            try:
                posted_at = datetime.strptime(post.get("posted_at", ""), "%Y-%m-%d %H:%M:%S")
                if posted_at >= week_ago:
                    recent_posts.append(post)
            except (ValueError, KeyError):
                continue
        
        # Analyze storytelling frameworks used
        framework_counter = Counter()
        for post in posts:
            framework = post.get("storytelling_framework", "Unknown")
            framework_counter[framework] += 1
        
        # Analyze content themes
        theme_counter = Counter()
        for post in posts:
            themes = post.get("content_themes", [])
            for theme in themes:
                theme_counter[theme] += 1
        
        return {
            "total_posts": len(posts),
            "recent_posts_count": len(recent_posts),
            "topic_coverage": metadata.get("topic_coverage", {}),
            "avg_engagement_rate": metadata.get("avg_engagement_rate", 0.0),
            "storytelling_frameworks": dict(framework_counter),
            "content_themes": dict(theme_counter),
            "recent_topics": self._extract_recent_topics(recent_posts)
        }
    
    def _extract_recent_topics(self, recent_posts):
        """Extracts topics from recent posts."""
        topics = []
        for post in recent_posts:
            topics.extend(post.get("topics", []))
        return list(set(topics))
    
    def identify_topic_gaps(self, article_title):
        """
        Identifies topic coverage gaps based on strategic goals.
        Returns recommendations for topic focus.
        """
        analysis = self.analyze_context()
        topic_coverage = analysis.get("topic_coverage", {})
        recent_topics = analysis.get("recent_topics", [])
        
        # Find high-priority goals with low coverage
        recommendations = []
        
        for goal in self.strategic_goals.get("primary_goals", []):
            if goal.get("priority") == "high":
                target_topics = goal.get("target_topics", [])
                
                for topic in target_topics:
                    coverage_count = topic_coverage.get(topic, 0)
                    if coverage_count < 3:  # Less than 3 posts about this topic
                        recommendations.append({
                            "topic": topic,
                            "reason": f"Low coverage ({coverage_count} posts) for high-priority goal: {goal.get('goal')}",
                            "priority": "high"
                        })
        
        # Check for topic diversity
        if len(recent_topics) > 0:
            # If last 3 posts covered similar topics, recommend diversity
            if len(set(recent_topics)) < 2:
                recommendations.append({
                    "topic": "diversity",
                    "reason": "Recent posts lack topic diversity - consider different angle",
                    "priority": "medium"
                })
        
        return recommendations
    
    def generate_strategic_guidance(self, article):
        """
        Generates comprehensive strategic guidance for the AI consultant.
        Returns guidance dictionary with recommendations.
        """
        analysis = self.analyze_context()
        topic_gaps = self.identify_topic_gaps(article.get("title", ""))
        
        # Determine content angle based on goals
        content_angle = self._recommend_content_angle(analysis)
        
        # Recommend storytelling framework
        storytelling_framework = self._recommend_storytelling_framework(analysis)
        
        # Build strategic context
        strategic_context = self._build_strategic_context(article, analysis, topic_gaps)
        
        # Topic focus recommendation
        topic_focus = self._recommend_topic_focus(article, topic_gaps)
        
        return {
            "topic_focus": topic_focus,
            "content_angle": content_angle,
            "storytelling_framework": storytelling_framework,
            "strategic_context": strategic_context,
            "topic_diversity_note": self._get_diversity_note(analysis),
            "engagement_optimization": self._get_engagement_insights(analysis)
        }
    
    def _recommend_content_angle(self, analysis):
        """Recommends content angle based on goals and history."""
        themes = analysis.get("content_themes", {})
        
        # If business_impact is underrepresented, recommend it
        if themes.get("business_impact", 0) < themes.get("explanation", 0):
            return "business_impact"
        
        # If practical_applications is low, recommend it
        if themes.get("practical_applications", 0) < 2:
            return "practical_applications"
        
        # Default to balanced approach
        return "balanced"  # Will include both technical and business perspectives
    
    def _recommend_storytelling_framework(self, analysis):
        """Recommends storytelling framework based on what works."""
        frameworks = analysis.get("storytelling_frameworks", {})
        
        # If we have engagement data, use best performing framework
        # For now, rotate between frameworks for diversity
        framework_options = [
            "Hook-Story-Lesson",
            "Before/After",
            "Problem-Solution",
            "Hero's Journey"
        ]
        
        # Find least used framework
        least_used = min(framework_options, key=lambda f: frameworks.get(f, 0))
        return least_used
    
    def _build_strategic_context(self, article, analysis, topic_gaps):
        """Builds strategic context explaining why this post matters."""
        context_parts = []
        
        # Check if this addresses a topic gap
        article_title_lower = article.get("title", "").lower()
        for gap in topic_gaps[:2]:  # Top 2 gaps
            topic = gap.get("topic", "").lower()
            if topic in article_title_lower:
                context_parts.append(
                    f"This post addresses a high-priority topic gap: {gap.get('topic')}. "
                    f"Only {analysis.get('topic_coverage', {}).get(gap.get('topic'), 0)} previous posts covered this."
                )
        
        # Add goal alignment
        for goal in self.strategic_goals.get("primary_goals", []):
            if goal.get("priority") == "high":
                target_topics = [t.lower() for t in goal.get("target_topics", [])]
                if any(topic in article_title_lower for topic in target_topics):
                    context_parts.append(
                        f"This aligns with high-priority goal: {goal.get('goal')}"
                    )
        
        if not context_parts:
            context_parts.append(
                "This post contributes to building consistent thought leadership presence."
            )
        
        return " ".join(context_parts)
    
    def _recommend_topic_focus(self, article, topic_gaps):
        """Recommends which topics to emphasize in the post."""
        article_title = article.get("title", "")
        
        # Extract potential topics from title
        focus_topics = []
        
        # Check against strategic goals
        for goal in self.strategic_goals.get("primary_goals", []):
            target_topics = goal.get("target_topics", [])
            for topic in target_topics:
                if topic.lower() in article_title.lower():
                    focus_topics.append(topic)
        
        if focus_topics:
            return f"Emphasize: {', '.join(focus_topics[:2])}"
        
        return "Focus on making complex AI concepts accessible and practical"
    
    def _get_diversity_note(self, analysis):
        """Provides note about topic diversity."""
        recent_topics = analysis.get("recent_topics", [])
        if len(recent_topics) >= 3:
            unique_topics = len(set(recent_topics))
            if unique_topics < 2:
                return "Last few posts covered similar topics - this post adds diversity"
        return "Good topic diversity maintained"
    
    def _get_engagement_insights(self, analysis):
        """Provides insights about engagement optimization."""
        frameworks = analysis.get("storytelling_frameworks", {})
        if len(frameworks) > 0:
            most_used = max(frameworks.items(), key=lambda x: x[1])
            return f"Most used framework: {most_used[0]} ({most_used[1]} times). Consider trying different approaches for variety."
        return "Experiment with different storytelling frameworks to find what resonates"
    
    def get_memory_context(self, count=5):
        """
        Retrieves recent posts with full content for memory context.
        
        Args:
            count: Number of recent posts to retrieve (default: 5)
            
        Returns:
            List of recent posts with content, sorted by most recent first
        """
        posts = self.history.get("posts", [])
        
        if not posts:
            return []
        
        # Get last N posts (most recent first)
        recent_posts = posts[-count:] if len(posts) >= count else posts
        # Reverse to get most recent first
        recent_posts = list(reversed(recent_posts))
        
        # Filter to only include posts that have content
        posts_with_content = [
            post for post in recent_posts 
            if post.get("content") and post.get("content").strip()
        ]
        
        return posts_with_content
    
    def format_posts_for_context(self, posts):
        """
        Formats posts into readable context string for AI consultant.
        
        Args:
            posts: List of post dictionaries with content
            
        Returns:
            Formatted string with recent posts for context
        """
        if not posts:
            return ""
        
        formatted_parts = ["RECENT POSTS (for context and continuity):\n"]
        
        for i, post in enumerate(posts, 1):
            posted_at = post.get("posted_at", "Unknown date")
            topics = ", ".join(post.get("topics", [])) or "General AI"
            content = post.get("content", "").strip()
            
            if content:
                # Calculate days ago
                try:
                    post_date = datetime.strptime(posted_at, "%Y-%m-%d %H:%M:%S")
                    days_ago = (datetime.now() - post_date).days
                    time_label = f"{days_ago} day{'s' if days_ago != 1 else ''} ago" if days_ago > 0 else "Today"
                except ValueError:
                    time_label = posted_at
                
                formatted_parts.append(f"\n[{time_label} - Topic: {topics}]")
                formatted_parts.append(f'"{content}"')
        
        formatted_parts.append("\n\nUse these posts to:")
        formatted_parts.append("- Build on previous discussions")
        formatted_parts.append("- Maintain voice consistency")
        formatted_parts.append("- Reference past insights when relevant")
        formatted_parts.append("- Avoid repeating the same explanations")
        
        return "\n".join(formatted_parts)
    
    def call_ai_consultant(self, article, strategic_guidance, memory_context=None):
        """
        Calls the content editor (AI consultant) with enriched context.
        This method will be used by main.py to generate the post.
        
        Args:
            article: Article dictionary
            strategic_guidance: Strategic guidance dictionary
            memory_context: Optional list of recent posts for context
        """
        # Import here to avoid circular dependencies
        from content_editor import generate_linkedin_post
        
        return generate_linkedin_post(
            article_title=article.get("title", ""),
            article_link=article.get("link", ""),
            article_source=article.get("source", ""),
            strategic_guidance=strategic_guidance,
            memory_context=memory_context
        )
    
    def update_history_with_engagement(self, post_data, post_content=None, engagement_data=None):
        """
        Updates history with a new post, post content, and optional engagement data.
        Called after successful posting.
        
        Args:
            post_data: Dictionary with title, link, storytelling_framework
            post_content: The actual post text content (NEW)
            engagement_data: Optional engagement metrics
        """
        posts = self.history.get("posts", [])
        
        # Extract topics from article title (simple keyword matching)
        topics = self._extract_topics_from_title(post_data.get("title", ""))
        
        # Determine content themes (can be enhanced with AI later)
        content_themes = self._infer_content_themes(post_data.get("title", ""))
        
        # Get strategic guidance that was used (if stored)
        storytelling_framework = post_data.get("storytelling_framework", "Hook-Story-Lesson")
        
        post_record = {
            "title": post_data.get("title", ""),
            "link": post_data.get("link", ""),
            "posted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": post_content or "",  # NEW: Save actual post content
            "topics": topics,
            "content_themes": content_themes,
            "storytelling_framework": storytelling_framework,
            "engagement": engagement_data or {},
            "strategic_goal": self._identify_goal_alignment(topics)
        }
        
        posts.append(post_record)
        self.history["posts"] = posts
        self.history["metadata"] = self._calculate_metadata(posts)
        
        self._save_history()
    
    def _extract_topics_from_title(self, title):
        """Extracts topics from article title using keyword matching."""
        title_lower = title.lower()
        topics = []
        
        # Check against strategic goal topics
        for goal in self.strategic_goals.get("primary_goals", []):
            for topic in goal.get("target_topics", []):
                if topic.lower() in title_lower:
                    topics.append(topic)
        
        # Add common AI topics if found
        ai_keywords = {
            "llm": "LLMs",
            "large language model": "LLMs",
            "generative ai": "Generative AI",
            "machine learning": "Machine Learning",
            "deep learning": "Deep Learning",
            "neural network": "Neural Networks",
            "transformer": "Transformer Architecture",
            "prompt engineering": "Prompt Engineering"
        }
        
        for keyword, topic in ai_keywords.items():
            if keyword in title_lower and topic not in topics:
                topics.append(topic)
        
        return topics if topics else ["AI"]
    
    def _infer_content_themes(self, title):
        """Infers content themes from title."""
        title_lower = title.lower()
        themes = []
        
        if any(word in title_lower for word in ["business", "roi", "impact", "strategy"]):
            themes.append("business_impact")
        
        if any(word in title_lower for word in ["how", "tutorial", "guide", "implement"]):
            themes.append("practical_applications")
        
        if any(word in title_lower for word in ["explain", "understand", "what is", "introduction"]):
            themes.append("explanation")
        
        if any(word in title_lower for word in ["trend", "future", "industry", "market"]):
            themes.append("industry_trends")
        
        return themes if themes else ["explanation"]
    
    def _identify_goal_alignment(self, topics):
        """Identifies which strategic goal this post aligns with."""
        for goal in self.strategic_goals.get("primary_goals", []):
            target_topics = [t.lower() for t in goal.get("target_topics", [])]
            if any(topic.lower() in target_topics for topic in topics):
                return goal.get("goal")
        return "general_thought_leadership"
    
    def _save_history(self):
        """Saves history to file."""
        with open(HISTORY_FILE, "w") as f:
            json.dump(self.history, f, indent=2)
    
    def analyze_patterns(self):
        """
        Analyzes posting patterns to identify insights.
        Returns analysis report.
        """
        analysis = self.analyze_context()
        
        report = {
            "summary": f"Total posts: {analysis['total_posts']}, Recent posts: {analysis['recent_posts_count']}",
            "top_topics": dict(Counter(analysis.get("topic_coverage", {})).most_common(5)),
            "storytelling_preferences": analysis.get("storytelling_frameworks", {}),
            "content_theme_distribution": analysis.get("content_themes", {}),
            "engagement_rate": analysis.get("avg_engagement_rate", 0.0),
            "recommendations": self._generate_recommendations(analysis)
        }
        
        return report
    
    def _generate_recommendations(self, analysis):
        """Generates recommendations based on analysis."""
        recommendations = []
        
        topic_coverage = analysis.get("topic_coverage", {})
        if len(topic_coverage) < 3:
            recommendations.append("Expand topic coverage - focus on diverse AI topics")
        
        if analysis.get("avg_engagement_rate", 0) < 0.10:
            recommendations.append("Consider experimenting with different content angles and storytelling frameworks")
        
        frameworks = analysis.get("storytelling_frameworks", {})
        if len(frameworks) < 2:
            recommendations.append("Try different storytelling frameworks for variety")
        
        return recommendations

if __name__ == "__main__":
    # Test
    manager = ContentManager()
    print("Content Manager initialized")
    print(f"History: {len(manager.history.get('posts', []))} posts")
    print(f"Strategic goals: {len(manager.strategic_goals.get('primary_goals', []))} goals")

