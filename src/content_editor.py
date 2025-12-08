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

def generate_linkedin_post(article_title, article_link, article_source=""):
    """
    Generates a LinkedIn post based on the article title and link using Groq (Llama 3 70B).
    """
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY is not set in environment variables.")

    system_prompt = """
    You are an expert Science Communicator and Tech Influencer specializing in Quantum Technology.
    Your goal is to write a professional, engaging LinkedIn post about the latest news regarding India's National Quantum Mission.
    
    Guidelines:
    1. Hook the reader immediately.
    2. Summarize the news update clearly.
    3. Explain the impact on India's tech ecosystem.
    4. Keep it under 200 words.
    5. Use a professional tone. 
    6. Do NOT use emojis (strict requirement).
    7. Include relevant hashtags like #NationalQuantumMission #QuantumIndia #IndiaTech #QFoundry.
    8. End with a question to encourage engagement.
    """

    user_prompt = f"""
    News Title: {article_title}
    Source: {article_source}
    Link: {article_link}

    Write the LinkedIn post. Do not include the link in the text body (it will be attached separately), but refer to "the latest update".
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
    title = "India announces new Quantum Computing Hub in Pune"
    link = "https://example.com/quantum-pune"
    print(generate_linkedin_post(title, link))

