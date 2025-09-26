import hmac
import hashlib
from github import Github
from typing import List
import logging

logger = logging.getLogger(__name__)

class GitHubService:
    def __init__(self, token: str, webhook_secret: str):
        self.github = Github(token)
        self.webhook_secret = webhook_secret
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        expected_signature = "sha256=" + hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_signature, signature)
    
    def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> List[dict]:
        repo = self.github.get_repo(f"{owner}/{repo}")
        pr = repo.get_pull(pr_number)
        files = pr.get_files()
        
        diffs = []
        for file in files:
            diffs.append({
                "filename": file.filename,
                "additions": file.additions,
                "deletions": file.deletions,
                "patch": file.patch if hasattr(file, 'patch') else "",
                "status": file.status
            })
        return diffs
    
    def post_review_comments(self, owner: str, repo: str, pr_number: int, 
                           comments: List[dict]) -> None:
        repo = self.github.get_repo(f"{owner}/{repo}")
        pr = repo.get_pull(pr_number)
        
        # Get the head commit SHA for review comments
        head_commit = pr.head.sha
        
        for comment in comments:
            pr.create_review_comment(
                body=comment["comment"],
                commit=head_commit,
                path=comment["file_path"],
                line=comment["line_number"]
            )