from fastapi import FastAPI, HTTPException, Header, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import logging
from app.config import get_settings, configure_logging
from app.services.github_service import GitHubService
from app.services.mistral_service import MistralService
from app.services.review_service import ReviewService
from app.models.schemas import WebhookPayload

# Configure logging first
configure_logging()

logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(title="Smart Code Review Assistant")

# Initialize services with error handling
try:
    github_service = GitHubService(settings.github_token, settings.github_webhook_secret)
    mistral_service = MistralService(settings.mistral_api_key, settings.mistral_model)
    review_service = ReviewService(github_service, mistral_service)
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    # Continue anyway for testing purposes

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Code Review Assistant"}

@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str = Header(None)
):
    # Verify webhook signature
    payload = await request.body()
    if not github_service.verify_webhook_signature(payload, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse webhook data
    data = await request.json()
    
    # Check if it's a PR opened or synchronized event
    if data.get("action") in ["opened", "synchronize"]:
        pr = data["pull_request"]
        repo = data["repository"]
        
        # Process in background
        background_tasks.add_task(
            review_service.process_pull_request,
            repo["owner"]["login"],
            repo["name"],
            pr["number"]
        )
        
        return {"status": "accepted", "message": "Review queued"}
    
    return {"status": "ignored", "message": "Not a relevant event"}

@app.post("/review/{owner}/{repo}/{pr_number}")
async def manual_review(
    owner: str,
    repo: str,
    pr_number: int,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(
        review_service.process_pull_request,
        owner,
        repo,
        pr_number
    )
    return {"status": "queued", "pr": f"{owner}/{repo}#{pr_number}"}

@app.get("/status")
async def service_status():
    return {
        "service": "Code Review Assistant",
        "model": settings.mistral_model,
        "version": "1.0.0"
    }