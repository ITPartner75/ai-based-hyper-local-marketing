# task_manager.py
from uuid import uuid4
from threading import Lock
import time

class TaskManager:
    def __init__(self):
        self.tasks = {}
        self.lock = Lock()

    def create_task(self):
        task_id = str(uuid4())
        now = time.time()
        with self.lock:
            self.tasks[task_id] = {
                "status": "pending",
                "progress": 0,
                "result": None,
                "error": None,
                "created_at": now,
                "updated_at": now
            }
        return task_id

    def update(self, task_id, **kwargs):
        with self.lock:
            if task_id in self.tasks:
                kwargs["updated_at"] = time.time()
                self.tasks[task_id].update(kwargs)

    def get(self, task_id):
        with self.lock:
            return self.tasks.get(task_id)

    def cleanup(self, older_than_seconds=3600):
        """Remove old completed/failed tasks from memory."""
        cutoff = time.time() - older_than_seconds
        with self.lock:
            self.tasks = {
                tid: task for tid, task in self.tasks.items()
                if task["status"] == "pending" or task["updated_at"] > cutoff
            }
    
    def delete_task(self, task_id: str):
        with self.lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                return True
            return False

# Singleton
task_manager = TaskManager()
