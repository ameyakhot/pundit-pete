# AI Consultant Personal Branding System

An automated LinkedIn posting system that helps AI consultants build their personal brand by posting daily thought leadership content. The system generates engaging posts that explain complex AI concepts in simple terms, establishing expertise through clear, accessible explanations.

## Overview

This system automatically:
1. **Scouts** for AI industry news and trends
2. **Plans** content using an intelligent backlog system
3. **Generates** thought leadership posts using Groq (Llama 3 70B)
4. **Publishes** to your LinkedIn personal profile daily at 6 PM IST

## Features

- **Intelligent Content Planning**: Maintains a backlog of AI news articles and prioritizes breaking news
- **Expert Content Generation**: Uses advanced AI to create posts that combine:
  - Expert consultant knowledge
  - Thought leadership insights
  - Hands-on practitioner experience
- **Simple Explanations**: Breaks down complex AI concepts into accessible, understandable language
- **Flexible Storytelling**: Uses various narrative frameworks (Hook-Story-Lesson, Before/After, Hero's Journey, etc.)
- **Automated Scheduling**: Posts daily at 6 PM IST via GitHub Actions
- **No Duplicates**: Tracks posting history to avoid reposting the same content

## Setup

### Prerequisites

- Python 3.11+
- A LinkedIn Developer App (for OAuth)
- A Groq API key
- GitHub account (for automated scheduling)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd linkedin-ai-qfoundry
   ```

2. **Install dependencies using uv**:
   ```bash
   uv sync
   ```

3. **Configure environment variables**:
   Create a `.env` file with:
   ```env
   LINKEDIN_CLIENT_ID=your_client_id
   LINKEDIN_CLIENT_SECRET=your_client_secret
   LINKEDIN_REDIRECT_URI=http://localhost:8000/callback
   GROQ_API_KEY=your_groq_api_key
   LINKEDIN_ACCESS_TOKEN=your_access_token
   ```

### LinkedIn Authentication

1. **Create a LinkedIn Developer App**:
   - Go to https://www.linkedin.com/developers/apps
   - Create a new app
   - Request access to "Share on LinkedIn" product
   - Add redirect URL: `http://localhost:8000/callback`

2. **Get Access Token**:
   ```bash
   uv run python src/auth_server.py
   ```
   - Open http://localhost:8000 in your browser
   - Click "Login with LinkedIn"
   - Approve permissions
   - Copy the access token to your `.env` file

### GitHub Actions Setup

1. **Add Secrets to GitHub**:
   - Go to your repository Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `LINKEDIN_CLIENT_ID`
     - `LINKEDIN_CLIENT_SECRET`
     - `LINKEDIN_ACCESS_TOKEN`
     - `GROQ_API_KEY`

2. **Enable GitHub Actions**:
   - The workflow is already configured in `.github/workflows/daily_post.yml`
   - It will run automatically at 6 PM IST (12:30 UTC) daily

## Usage

### Manual Run

To test the system manually:

```bash
uv run src/main.py
```

This will:
1. Fetch AI industry news from the last 7 days
2. Select the best article to post about
3. Generate a thought leadership post
4. Publish to your LinkedIn profile

### Automated Daily Posts

The system runs automatically via GitHub Actions at 6 PM IST every day. No manual intervention needed.

## How It Works

1. **News Scouting** (`src/news_scout.py`):
   - Fetches AI industry news from Google News RSS
   - Filters articles from the last 7 days
   - Adds new articles to the content backlog

2. **Content Planning** (`src/content_planner.py`):
   - Maintains a backlog of potential posts
   - Prioritizes breaking news (< 24 hours old)
   - Tracks posting history to avoid duplicates

3. **Content Generation** (`src/content_editor.py`):
   - Uses Groq (Llama 3 70B) to generate posts
   - Applies expert consultant + thought leader + practitioner persona
   - Explains complex concepts simply
   - Uses flexible storytelling frameworks

4. **Publishing** (`src/linkedin_api.py`):
   - Posts to your LinkedIn personal profile
   - Attaches article link if available
   - Updates history to track posted content

## Content Strategy

The system generates posts that:
- **Establish Expertise**: Show deep knowledge of AI concepts
- **Simplify Complexity**: Explain technical topics in accessible language
- **Provide Insights**: Offer unique perspectives, not just summaries
- **Engage Audience**: Use storytelling and thought-provoking questions
- **Build Brand**: Consistently reinforce your position as a go-to AI expert

## Project Structure

```
linkedin-ai-qfoundry/
├── src/
│   ├── news_scout.py          # Fetches AI industry news
│   ├── content_planner.py     # Manages content backlog and selection
│   ├── content_editor.py      # Generates thought leadership posts
│   ├── linkedin_api.py        # Handles LinkedIn posting
│   ├── auth_server.py         # OAuth authentication server
│   └── main.py                # Main orchestration script
├── .github/
│   └── workflows/
│       └── daily_post.yml     # Automated daily posting schedule
├── history.json                # Tracks posted articles
├── content_backlog.json       # Queue of potential posts
└── README.md                  # This file
```

## Customization

### Change Posting Time

Edit `.github/workflows/daily_post.yml` and update the cron schedule:
```yaml
- cron: '30 12 * * *'  # 6 PM IST (12:30 UTC)
```

### Adjust Content Style

Modify the system prompt in `src/content_editor.py` to change:
- Writing tone
- Storytelling frameworks
- Hashtags
- Post length

### Change News Sources

Update the RSS URL in `src/news_scout.py` to fetch different topics or sources.

## Troubleshooting

### "Token MISSING w_organization_social scope"
- This error only appears if posting to company pages
- For personal profile posting, this is not required
- Current setup posts to personal profile, so this shouldn't occur

### "No content available in backlog"
- The system looks back 7 days for news
- If no relevant AI news is found, it will exit gracefully
- You can manually add articles to `content_backlog.json` if needed

### Posts not appearing on LinkedIn
- Verify your `LINKEDIN_ACCESS_TOKEN` is valid
- Check that you approved "Share on LinkedIn" permission
- Ensure the token hasn't expired (tokens last 60 days)

## License

[Add your license here]

## Contributing

[Add contribution guidelines if applicable]
