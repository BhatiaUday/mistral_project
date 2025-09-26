# Smart Code Review Assistant

An automated code review system that analyzes GitHub pull requests using Mistral AI. When a pull request is created, the system automatically reviews the code changes and posts intelligent feedback comments directly on the PR.

## What It Does

This application connects to GitHub repositories and automatically reviews code changes when pull requests are created. It uses Mistral AI to analyze code diffs and identify potential issues including:

- Security vulnerabilities
- Bug risks and logic errors
- Performance optimization opportunities
- Code quality and best practice violations
- Input validation issues
- Error handling improvements

The AI reviewer posts comments directly on the pull request with specific line-by-line feedback, severity levels, and suggested improvements.

## Demo

See the AI reviewer in action on these example pull requests:
- [Demo PR #1](https://github.com/BhatiaUday/mistral_project/pull/1)
- [Demo PR #2](https://github.com/BhatiaUday/mistral_project/pull/2)
- [Demo PR #3](https://github.com/BhatiaUday/mistral_project/pull/3)

## Requirements

- Python 3.9 or higher
- GitHub account with repository access
- Mistral AI API key from console.mistral.ai
- Azure account for deployment (optional)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/BhatiaUday/mistral_project.git
cd mistral_project
```

2. Create and activate virtual environment:
```bash
python3 -m venv mistral_project_venv
source mistral_project_venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys (see Configuration section)
```

5. Run the application:
```bash
python -m uvicorn app.main:app --reload
```

## Configuration

Create a `.env` file with the following variables:

```bash
# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Mistral AI Configuration  
MISTRAL_API_KEY=your_mistral_api_key
MISTRAL_MODEL=mistral-small

# Application Settings
APP_HOST=0.0.0.0
APP_PORT=8080
LOG_LEVEL=INFO
```

### Getting API Keys

**GitHub Personal Access Token:**
1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate new token with `repo` permissions
3. Copy the token to GITHUB_TOKEN in .env

**Mistral AI API Key:**
1. Sign up at console.mistral.ai
2. Navigate to API Keys section
3. Generate new API key
4. Copy the key to MISTRAL_API_KEY in .env

**Webhook Secret:**
Generate a secure random string for webhook verification:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## API Endpoints

- `GET /health` - Health check endpoint
- `GET /status` - Service status and configuration
- `POST /webhook/github` - GitHub webhook endpoint for automatic PR reviews
- `POST /review/{owner}/{repo}/{pr_number}` - Manual PR review trigger

## Webhook Setup

To enable automatic PR reviews:

1. Go to your GitHub repository settings
2. Navigate to Webhooks > Add webhook
3. Set Payload URL to: `https://your-deployed-app-url/webhook/github`
4. Set Content type to: `application/json`
5. Set Secret to your GITHUB_WEBHOOK_SECRET value
6. Select "Pull requests" event
7. Save the webhook

## Deployment

The application includes Azure Container Apps deployment configuration:

```bash
# Deploy to Azure
cd deployment/azure
./deploy-containerapp.sh
```

See `deployment/azure/AZURE_DEPLOYMENT.md` for detailed deployment instructions.

## Local Development

Run with Docker:
```bash
docker-compose up --build
```

Run for development:
```bash
python -m uvicorn app.main:app --reload --port 8000
```

## How It Works

1. Developer creates a pull request on GitHub
2. GitHub sends webhook notification to the application
3. Application fetches PR diff using GitHub API
4. Code changes are analyzed by Mistral AI
5. AI generates review comments with severity levels and suggestions
6. Comments are posted back to the pull request
7. Developer receives immediate feedback on code changes

## Architecture

```
GitHub PR → Webhook → FastAPI App → Mistral AI → Code Analysis → GitHub Comments
```

The application is built with:
- FastAPI for the web framework and API endpoints
- PyGithub for GitHub API integration
- Mistral AI SDK for code analysis
- Docker for containerization
- Azure Container Apps for cloud deployment

## License

MIT License - feel free to use this project for your own code review automation needs.