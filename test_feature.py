"""
Test feature for demonstrating the Smart Code Review Assistant.

This file contains a simple function that can be reviewed by our AI assistant.
"""

def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number using recursion."""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)


def process_user_data(data):
    """Process user data with some potential issues for the AI to catch."""
    # Potential issue: No input validation
    result = []
    
    for item in data:
        # Potential issue: Accessing dict without checking if key exists
        processed_item = {
            'id': item['id'],
            'name': item['name'].upper(),
            'score': item['score'] * 2
        }
        result.append(processed_item)
    
    return result


class UserManager:
    """A simple user management class."""
    
    def __init__(self):
        self.users = []
    
    def add_user(self, user):
        # Potential issue: No duplicate checking
        self.users.append(user)
    
    def find_user(self, user_id):
        # Potential issue: Inefficient linear search
        for user in self.users:
            if user.get('id') == user_id:
                return user
        return None
    
    def delete_user(self, user_id):
        # Potential issue: Modifying list while iterating
        for i, user in enumerate(self.users):
            if user.get('id') == user_id:
                del self.users[i]
                return True
        return False