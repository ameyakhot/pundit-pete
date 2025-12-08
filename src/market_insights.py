"""
Market Insights Module
Analyzes trending topics and industry insights from news feed.
Can be extended with additional data sources in the future.
"""

from collections import Counter
from datetime import datetime, timedelta


class MarketInsights:
    """
    Analyzes market trends and industry insights from available data sources.
    """
    
    def __init__(self):
        pass
    
    def analyze_trending_topics(self, articles):
        """
        Analyzes articles to identify trending topics.
        
        Args:
            articles: List of article dictionaries with 'title' and 'published' fields
            
        Returns:
            Dictionary with trending topics and insights
        """
        if not articles:
            return {
                "trending_topics": [],
                "insights": "No articles available for analysis"
            }
        
        # Extract keywords from titles
        topic_keywords = {
            "LLMs": ["llm", "large language model", "gpt", "claude", "gemini"],
            "Generative AI": ["generative ai", "genai", "text generation", "image generation"],
            "Machine Learning": ["machine learning", "ml", "deep learning", "neural network"],
            "AI Ethics": ["ai ethics", "bias", "fairness", "responsible ai"],
            "AI Business": ["ai strategy", "ai adoption", "digital transformation", "roi"],
            "Computer Vision": ["computer vision", "image recognition", "cv"],
            "NLP": ["nlp", "natural language processing", "text analysis"],
            "AI Infrastructure": ["ai infrastructure", "gpu", "compute", "training"],
            "AI Regulation": ["regulation", "governance", "compliance", "policy"]
        }
        
        topic_counts = Counter()
        recent_articles = []
        week_ago = datetime.now() - timedelta(days=7)
        
        for article in articles:
            title_lower = article.get("title", "").lower()
            
            # Check publication date
            try:
                pub_date = datetime.strptime(article.get("published", ""), "%Y-%m-%d %H:%M:%S")
                if pub_date >= week_ago:
                    recent_articles.append(article)
            except (ValueError, KeyError):
                recent_articles.append(article)  # Include if date parsing fails
            
            # Count topics
            for topic, keywords in topic_keywords.items():
                if any(keyword in title_lower for keyword in keywords):
                    topic_counts[topic] += 1
        
        # Get top trending topics
        trending_topics = [topic for topic, count in topic_counts.most_common(5)]
        
        # Generate insights
        insights = self._generate_insights(topic_counts, len(recent_articles))
        
        return {
            "trending_topics": trending_topics,
            "topic_counts": dict(topic_counts),
            "recent_articles_count": len(recent_articles),
            "insights": insights
        }
    
    def _generate_insights(self, topic_counts, recent_count):
        """Generates insights based on topic analysis."""
        insights = []
        
        if recent_count > 10:
            insights.append(f"High activity in AI space: {recent_count} recent articles")
        
        if topic_counts:
            top_topic = topic_counts.most_common(1)[0]
            insights.append(f"Most discussed topic: {top_topic[0]} ({top_topic[1]} mentions)")
        
        # Check for emerging topics (appearing frequently but not in top 3)
        if len(topic_counts) > 3:
            insights.append("Diverse topic coverage indicates broad industry interest")
        
        return ". ".join(insights) if insights else "Standard industry activity"
    
    def get_market_context(self, articles):
        """
        Provides market context for content strategy.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Market context string for use in strategic guidance
        """
        analysis = self.analyze_trending_topics(articles)
        
        context_parts = []
        
        if analysis["trending_topics"]:
            context_parts.append(
                f"Current trending topics: {', '.join(analysis['trending_topics'][:3])}"
            )
        
        if analysis["insights"]:
            context_parts.append(analysis["insights"])
        
        return ". ".join(context_parts) if context_parts else "Standard market conditions"

if __name__ == "__main__":
    # Test
    insights = MarketInsights()
    test_articles = [
        {"title": "OpenAI releases new GPT model", "published": "2025-12-08 10:00:00"},
        {"title": "Machine Learning transforms healthcare", "published": "2025-12-07 15:00:00"}
    ]
    result = insights.analyze_trending_topics(test_articles)
    print(result)

