
class InvalidPriorityWindowException(Exception):
    def __init__(self):
        self.detail = "Minimum priority must be less than or equal to maximum priority."
        
    
class InvalidDateWindowException(Exception):
    def __init__(self, start, end):
        self.detail = f"Start date {start} must be before or equal to end date {end}."
        
        
class InvalidPriorityPairException(Exception):
    def __init__(self):
        self.detail = f"Min and max priority must be both present or all None."
        
class TaskNotFoundException(Exception):
    def __init__(self, task_id):
        self.detail = f"Task id {task_id} is not found."

