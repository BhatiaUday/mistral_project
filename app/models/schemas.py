from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class SeverityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class WebhookPayload(BaseModel):
    action: str
    pull_request: Dict[str, Any]
    repository: Dict[str, Any]
    sender: Dict[str, Any]

class PullRequestInfo(BaseModel):
    repo_owner: str
    repo_name: str
    pr_number: int
    pr_title: str
    pr_description: Optional[str]
    base_branch: str
    head_branch: str

class CodeDiff(BaseModel):
    filename: str
    additions: int
    deletions: int
    patch: str
    status: str

class ReviewComment(BaseModel):
    file_path: str
    line_number: int
    comment: str
    severity: SeverityLevel
    suggestion: Optional[str]

class ReviewResponse(BaseModel):
    pr_number: int
    total_comments: int
    comments: List[ReviewComment]
    review_summary: str