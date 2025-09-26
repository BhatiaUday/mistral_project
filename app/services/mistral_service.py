from mistralai import Mistral
import json
import logging
import time
import asyncio
from typing import List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MistralService:
    def __init__(self, api_key: str, model: str):
        self.client = Mistral(api_key=api_key)
        self.primary_model = model
        # Fallback models in order of preference
        self.fallback_models = [
            "mistral-small-latest",
            "mistral-tiny-latest", 
            "open-mistral-7b",
            "open-mixtral-8x7b"
        ]
        # Remove primary model from fallbacks if it's there
        if self.primary_model in self.fallback_models:
            self.fallback_models.remove(self.primary_model)
        
        # Rate limiting tracking
        self.rate_limit_retries = {}  # model -> {last_retry: datetime, count: int}
        self.max_retries_per_model = 3
        self.retry_delay = 60  # 1 minute in seconds
    
    def analyze_code_diff(self, diff_content: str, filename: str) -> List[Dict]:
        prompt = self._create_review_prompt(diff_content, filename)
        
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        # Try primary model first, then fallbacks
        models_to_try = [self.primary_model] + self.fallback_models
        
        for model in models_to_try:
            try:
                # Check if we need to wait due to rate limiting
                if self._should_wait_for_rate_limit(model):
                    logger.info(f"Rate limit detected for {model}, waiting {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                
                logger.info(f"Attempting code analysis with model: {model}")
                response = self.client.chat.complete(
                    model=model,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=2000,
                    top_p=0.95
                )
                
                # Reset rate limit tracking on success
                if model in self.rate_limit_retries:
                    del self.rate_limit_retries[model]
                
                logger.info(f"Successfully analyzed code with model: {model}")
                return self._parse_response(response.choices[0].message.content)
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check if it's a rate limit error
                if self._is_rate_limit_error(error_msg):
                    logger.warning(f"Rate limit hit for model {model}: {e}")
                    self._track_rate_limit(model)
                    
                    # Try next model if available
                    if model != models_to_try[-1]:
                        logger.info(f"Trying fallback model due to rate limit...")
                        continue
                else:
                    logger.error(f"Error with model {model}: {e}")
                    # For non-rate-limit errors, try next model immediately
                    if model != models_to_try[-1]:
                        logger.info(f"Trying fallback model due to error...")
                        continue
        
        logger.error("All models failed or hit rate limits")
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
    
    def _is_rate_limit_error(self, error_msg: str) -> bool:
        """Check if the error message indicates a rate limit"""
        rate_limit_indicators = [
            "rate limit",
            "too many requests", 
            "quota exceeded",
            "429",
            "rate_limit_exceeded",
            "throttle"
        ]
        return any(indicator in error_msg for indicator in rate_limit_indicators)
    
    def _track_rate_limit(self, model: str):
        """Track rate limit occurrences for a model"""
        now = datetime.now()
        if model not in self.rate_limit_retries:
            self.rate_limit_retries[model] = {"last_retry": now, "count": 1}
        else:
            self.rate_limit_retries[model]["last_retry"] = now
            self.rate_limit_retries[model]["count"] += 1
    
    def _should_wait_for_rate_limit(self, model: str) -> bool:
        """Check if we should wait before retrying a model due to rate limits"""
        if model not in self.rate_limit_retries:
            return False
        
        last_retry = self.rate_limit_retries[model]["last_retry"]
        time_since_last = datetime.now() - last_retry
        
        # If less than retry_delay seconds have passed since last retry, wait
        return time_since_last.total_seconds() < self.retry_delay
    
    def get_current_model_status(self) -> Dict:
        """Get status of all models for debugging"""
        status = {
            "primary_model": self.primary_model,
            "fallback_models": self.fallback_models,
            "rate_limited_models": {}
        }
        
        for model, data in self.rate_limit_retries.items():
            time_since = datetime.now() - data["last_retry"]
            status["rate_limited_models"][model] = {
                "retry_count": data["count"],
                "last_retry": data["last_retry"].isoformat(),
                "seconds_until_retry": max(0, self.retry_delay - time_since.total_seconds())
            }
        
        return status