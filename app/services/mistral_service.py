from mistralai import Mistral
import json
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class MistralService:
    def __init__(self, api_key: str, model: str):
        self.client = Mistral(api_key=api_key)
        self.model = model
    
    def analyze_code_diff(self, diff_content: str, filename: str) -> List[Dict]:
        prompt = self._create_review_prompt(diff_content, filename)
        
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=2000,
                top_p=0.95
            )
            
            return self._parse_response(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error analyzing code: {e}")
            return []
    
    def _get_system_prompt(self) -> str:
        return """You are an expert code reviewer. Your task is to analyze:
        1. Potential bugs or logical errors
        2. Security vulnerabilities (e.g., SQL injection, XSS)
        3. Performance problems
        4. Violations of coding best practices
        5. Code that could be simplified or improved
        
        Provide feedback as a JSON array:
        [
            {
                "line_number": <int>,
                "severity": "high|medium|low|info",
                "comment": "<issue description>",
                "suggestion": "<optional code suggestion>"
            }
        ]
        
        Be specific and actionable. Focus on actual problems, not style preferences."""
    
    def _create_review_prompt(self, diff_content: str, filename: str) -> str:
        return f"""Review the code changes in {filename}:
        
        ```diff
        {diff_content}
        ```
        
        Provide feedback in the specified JSON format."""
    
    def _parse_response(self, response: str) -> List[Dict]:
        try:
            # Extract JSON from response
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to parse Mistral response: {e}")
        return []