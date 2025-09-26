import logging
from typing import List
from app.models.schemas import ReviewComment, CodeDiff, SeverityLevel

logger = logging.getLogger(__name__)

class ReviewService:
    def __init__(self, github_service, mistral_service):
        self.github_service = github_service
        self.mistral_service = mistral_service
    
    async def process_pull_request(self, owner: str, repo: str, pr_number: int):
        try:
            # Get PR diff
            diffs = self.github_service.get_pr_diff(owner, repo, pr_number)
            
            all_comments = []
            for diff in diffs:
                if not diff.get("patch"):
                    continue
                
                # Analyze with Mistral
                analysis = self.mistral_service.analyze_code_diff(
                    diff["patch"], 
                    diff["filename"]
                )
                
                # Convert to review comments
                for item in analysis:
                    # Ensure line_number is an integer, not a list
                    line_num = item.get("line_number", 1)
                    if isinstance(line_num, list) and line_num:
                        line_num = line_num[0]  # Take first element if it's a list
                    if not isinstance(line_num, int):
                        line_num = 1  # Default fallback
                    
                    comment = ReviewComment(
                        file_path=diff["filename"],
                        line_number=line_num,
                        comment=self._format_comment(item),
                        severity=SeverityLevel(item.get("severity", "info")),
                        suggestion=item.get("suggestion")
                    )
                    all_comments.append(comment)
            
            # Post comments to GitHub
            if all_comments:
                self._post_comments_to_github(owner, repo, pr_number, all_comments)
            
            return {
                "status": "success",
                "comments_count": len(all_comments),
                "files_reviewed": len(diffs)
            }
            
        except Exception as e:
            logger.error(f"Error processing PR: {e}")
            raise
    
    def _format_comment(self, analysis_item: dict) -> str:
        severity_emoji = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🔵",
            "info": "ℹ️"
        }
        
        emoji = severity_emoji.get(analysis_item.get("severity", "info"))
        
        # Format as bot comment with clear AI attribution
        comment = f"🤖 **AI Code Reviewer** {emoji}\n\n"
        comment += f"**{analysis_item.get('severity', 'info').upper()}**: {analysis_item['comment']}"
        
        if analysis_item.get("suggestion"):
            comment += f"\n\n💡 **Suggestion:**\n```python\n{analysis_item['suggestion']}\n```"
        
        comment += f"\n\n---\n*Powered by Mistral AI • Smart Code Review Assistant*"
        
        return comment
    
    def _post_comments_to_github(self, owner: str, repo: str, pr_number: int, 
                                comments: List[ReviewComment]):
        for comment in comments:
            self.github_service.post_review_comments(
                owner, repo, pr_number,
                [{
                    "file_path": comment.file_path,
                    "line_number": comment.line_number,
                    "comment": comment.comment
                }]
            )