"""
Data processing utilities for the Code Review Assistant.
"""
import json
import time
from typing import List, Dict, Any


def process_user_data(data):
    """Process user data with various transformations."""
    # TODO: Add proper type hints
    result = []
    
    # Inefficient nested loop - O(n²) complexity
    for item in data:
        for other_item in data:
            if item['id'] != other_item['id'] and item['category'] == other_item['category']:
                result.append({
                    'match': True,
                    'item1': item,
                    'item2': other_item
                })
    
    return result


def calculate_metrics(user_stats, threshold=100):
    """Calculate user metrics with potential issues."""
    # Missing error handling
    total_score = 0
    user_count = len(user_stats)
    
    # Hardcoded magic numbers
    for user in user_stats:
        score = user['points'] * 1.5 + user['bonus'] * 2.3
        if score > 500:  # Magic number
            score = score * 0.8
        total_score += score
    
    # Potential division by zero
    average = total_score / user_count
    
    # Unclear variable naming
    x = []
    for u in user_stats:
        if u['active']:
            x.append(u)
    
    return {
        'average': average,
        'total': total_score,
        'active_users': x,
        'processed_at': time.time()
    }


class DatabaseHelper:
    """Helper class for database operations with security issues."""
    
    def __init__(self, connection_string):
        self.conn_str = connection_string
        self.cache = {}
    
    def execute_query(self, query, params=None):
        """Execute database query - potential SQL injection risk."""
        # This is a security risk - string formatting in SQL queries
        if params:
            query = query.format(**params)
        
        # Simulated database execution
        print(f"Executing: {query}")
        return {"status": "success", "rows": []}
    
    def get_user_data(self, user_id):
        """Get user data with caching but no validation."""
        # No input validation
        cache_key = f"user_{user_id}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Vulnerable query construction
        query = f"SELECT * FROM users WHERE id = {user_id}"
        result = self.execute_query(query)
        
        # Store in cache without expiration
        self.cache[cache_key] = result
        return result