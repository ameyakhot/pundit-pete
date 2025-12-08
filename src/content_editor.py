import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq Client
try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception as e:
    # Handle initialization errors if needed
    client = None

def generate_linkedin_post(article_title, article_link, article_source="", strategic_guidance=None, memory_context=None):
    """
    Generates a LinkedIn post based on AI industry news using Groq (Llama 3 70B).
    Establishes the author as an expert AI consultant, thought leader, and hands-on practitioner.
    
    Args:
        article_title: Title of the news article
        article_link: URL of the article
        article_source: Source of the article
        strategic_guidance: Optional dictionary with strategic guidance from Content Manager
        memory_context: Optional list of recent posts for context and continuity
    """
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY is not set in environment variables.")

    # Build strategic guidance section if provided
    guidance_section = ""
    if strategic_guidance:
        guidance_section = f"""
    
    STRATEGIC GUIDANCE FROM CONTENT MANAGER:
    - Topic Focus: {strategic_guidance.get('topic_focus', 'General AI concepts')}
    - Content Angle: {strategic_guidance.get('content_angle', 'balanced')}
    - Recommended Storytelling Framework: {strategic_guidance.get('storytelling_framework', 'Hook-Story-Lesson')}
    - Strategic Context: {strategic_guidance.get('strategic_context', 'Build thought leadership')}
    - Topic Diversity Note: {strategic_guidance.get('topic_diversity_note', 'Maintain diversity')}
    - Engagement Optimization: {strategic_guidance.get('engagement_optimization', 'Use engaging storytelling')}
    
    IMPORTANT: Incorporate this strategic guidance into your post. Use the recommended storytelling framework and focus on the specified topics and content angle.
    """
    
    # Build memory context section if provided
    memory_section = ""
    if memory_context:
        formatted_parts = ["RECENT POSTS (for context and continuity):\n"]
        
        for i, post in enumerate(memory_context, 1):
            posted_at = post.get("posted_at", "Unknown date")
            topics = ", ".join(post.get("topics", [])) or "General AI"
            content = post.get("content", "").strip()
            
            if content:
                # Calculate days ago
                try:
                    from datetime import datetime
                    post_date = datetime.strptime(posted_at, "%Y-%m-%d %H:%M:%S")
                    days_ago = (datetime.now() - post_date).days
                    time_label = f"{days_ago} day{'s' if days_ago != 1 else ''} ago" if days_ago > 0 else "Today"
                except ValueError:
                    time_label = posted_at
                
                formatted_parts.append(f"\n[{time_label} - Topic: {topics}]")
                formatted_parts.append(f'"{content}"')
        
        if len(formatted_parts) > 1:  # More than just the header
            formatted_parts.append("\n\nUse these posts to:")
            formatted_parts.append("- Build on previous discussions")
            formatted_parts.append("- Maintain voice consistency")
            formatted_parts.append("- Reference past insights when relevant")
            formatted_parts.append("- Avoid repeating the same explanations")
            
            # Join outside f-string to avoid backslash issue
            formatted_memory = "\n".join(formatted_parts)
            memory_section = f"""
    
    {formatted_memory}
    """

    system_prompt = f"""
    You are an expert AI consultant, thoughtful leader, and hands-on practitioner who explains complex AI concepts in the simplest way possible.
    
    Your goal is to write a professional, engaging LinkedIn post that establishes your expertise while making complex AI topics accessible to everyone.
    
    Content Strategy:
    1. Use flexible storytelling frameworks (Hook-Story-Lesson, Before/After, Hero's Journey, or problem-solution narratives)
    2. Explain complex AI concepts in the simplest terms possible - imagine explaining to a smart non-technical person
    3. Generate unique insights and perspectives, not just summaries of the news
    4. Combine three personas:
       - Expert Consultant: Show deep knowledge and authority
       - Thought Leader: Provide forward-thinking insights and implications
       - Hands-on Practitioner: Share practical, real-world applications
    {guidance_section}
    {memory_section}
    Writing Guidelines:
    1. Hook the reader immediately with a compelling opening
    2. Use storytelling to make technical concepts relatable and memorable
    3. Break down complex ideas into simple, digestible explanations
    4. Provide unique insights or perspectives on the topic
    5. Connect the news to broader implications for business, technology, or society
    6. Keep it under 250 words
    7. Use a professional yet approachable tone
    8. Do NOT use emojis or unicode characters (strict requirement)
    9. Include relevant hashtags like #AI #MachineLearning #ArtificialIntelligence #TechLeadership #AIConsulting #Innovation
    10. End with a thought-provoking question or call-to-action to encourage engagement
    
    Remember: Your goal is to build your personal brand as the go-to expert who makes AI accessible. Every post should reinforce that you understand complex concepts deeply enough to explain them simply.
    """

    memory_instruction = ""
    if memory_context:
        memory_instruction = """
    8. Reference or build on previous posts when relevant (see recent posts above)
    9. Maintain consistency with your established voice and style
    10. Avoid repeating explanations you've already covered in recent posts
    """
    
    user_prompt = f"""
    News Article:
    Title: {article_title}
    Source: {article_source}
    Link: {article_link}

    Write a LinkedIn post that:
    1. Uses this news as inspiration (not just a summary)
    2. Explains the underlying AI concepts in simple terms
    3. Provides unique insights or perspectives
    4. Establishes expertise through clear, accessible explanations
    5. Uses the recommended storytelling framework from strategic guidance
    {f"6. Focus on: {strategic_guidance.get('topic_focus', '')}" if strategic_guidance and strategic_guidance.get('topic_focus') else ""}
    {f"7. Content angle: {strategic_guidance.get('content_angle', '')}" if strategic_guidance and strategic_guidance.get('content_angle') else ""}
    {memory_instruction}
    
    Do not include the link in the text body (it will be attached separately), but you can reference "this development" or "the latest update".
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # High performance model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        post_content = response.choices[0].message.content.strip()
        return post_content
    except Exception as e:
        print(f"[ERROR] Failed to generate content: {e}")
        return None

if __name__ == "__main__":
    # Test
    title = "OpenAI releases new GPT model with improved reasoning capabilities"
    link = "https://example.com/gpt-update"
    print(generate_linkedin_post(title, link))
