"""Task status management with filesystem-backed persistence."""

import json
import os
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from ..config import Config


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"          # 等待中
    PROCESSING = "processing"    # 处理中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"            # 失败


@dataclass
class Task:
    """任务数据类"""
    task_id: str
    task_type: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    progress: int = 0              # 总进度百分比 0-100
    message: str = ""              # 状态消息
    result: Optional[Dict] = None  # 任务结果
    error: Optional[str] = None    # 错误信息
    metadata: Dict = field(default_factory=dict)  # 额外元数据
    progress_detail: Dict = field(default_factory=dict)  # 详细进度信息
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "progress": self.progress,
            "message": self.message,
            "progress_detail": self.progress_detail,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Rebuild a Task instance from persisted JSON data."""
        status = data.get("status", TaskStatus.PENDING)
        if isinstance(status, str):
            status = TaskStatus(status)

        return cls(
            task_id=data["task_id"],
            task_type=data.get("task_type", "unknown"),
            status=status,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            progress=data.get("progress", 0),
            message=data.get("message", ""),
            result=data.get("result"),
            error=data.get("error"),
            metadata=data.get("metadata") or {},
            progress_detail=data.get("progress_detail") or {},
        )


class TaskManager:
    """
    任务管理器
    线程安全的任务状态管理
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._tasks: Dict[str, Task] = {}
                    cls._instance._task_lock = threading.Lock()
                    cls._instance._tasks_dir = os.path.join(Config.UPLOAD_FOLDER, 'tasks')
                    os.makedirs(cls._instance._tasks_dir, exist_ok=True)
        return cls._instance

    def _get_task_path(self, task_id: str) -> str:
        """Return the filesystem path for a task JSON document."""
        return os.path.join(self._tasks_dir, f"{task_id}.json")

    def _save_task(self, task: Task) -> None:
        """Persist task state atomically so all workers can read it."""
        path = self._get_task_path(task.task_id)
        temp_path = f"{path}.tmp"
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(task.to_dict(), f, ensure_ascii=False, indent=2)
        os.replace(temp_path, path)

    def _load_task_from_disk(self, task_id: str) -> Optional[Task]:
        """Load a task from disk if it exists."""
        path = self._get_task_path(task_id)
        if not os.path.exists(path):
            return None

        with open(path, 'r', encoding='utf-8') as f:
            task = Task.from_dict(json.load(f))

        self._tasks[task_id] = task
        return task
    
    def create_task(self, task_type: str, metadata: Optional[Dict] = None) -> str:
        """
        创建新任务
        
        Args:
            task_type: 任务类型
            metadata: 额外元数据
            
        Returns:
            任务ID
        """
        task_id = str(uuid.uuid4())
        now = datetime.now()
        
        task = Task(
            task_id=task_id,
            task_type=task_type,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
            metadata=metadata or {}
        )
        
        with self._task_lock:
            self._tasks[task_id] = task
            self._save_task(task)

        return task_id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        with self._task_lock:
            task = self._tasks.get(task_id)
            if task:
                return task
            return self._load_task_from_disk(task_id)
    
    def update_task(
        self,
        task_id: str,
        status: Optional[TaskStatus] = None,
        progress: Optional[int] = None,
        message: Optional[str] = None,
        result: Optional[Dict] = None,
        error: Optional[str] = None,
        progress_detail: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ):
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            status: 新状态
            progress: 进度
            message: 消息
            result: 结果
            error: 错误信息
            progress_detail: 详细进度信息
            metadata: 额外元数据
        """
        with self._task_lock:
            task = self._tasks.get(task_id) or self._load_task_from_disk(task_id)
            if task:
                task.updated_at = datetime.now()
                if status is not None:
                    task.status = status
                if progress is not None:
                    task.progress = progress
                if message is not None:
                    task.message = message
                if result is not None:
                    task.result = result
                if error is not None:
                    task.error = error
                if progress_detail is not None:
                    task.progress_detail = progress_detail
                if metadata is not None:
                    task.metadata = metadata
                self._save_task(task)
    
    def complete_task(self, task_id: str, result: Dict):
        """标记Task completed"""
        self.update_task(
            task_id,
            status=TaskStatus.COMPLETED,
            progress=100,
            message="Task completed",
            result=result
        )
    
    def fail_task(self, task_id: str, error: str):
        """标记Task failed"""
        self.update_task(
            task_id,
            status=TaskStatus.FAILED,
            message="Task failed",
            error=error
        )
    
    def list_tasks(self, task_type: Optional[str] = None) -> list:
        """列出任务"""
        with self._task_lock:
            tasks: Dict[str, Task] = dict(self._tasks)
            if os.path.exists(self._tasks_dir):
                for filename in os.listdir(self._tasks_dir):
                    if not filename.endswith('.json'):
                        continue
                    task_id = filename[:-5]
                    if task_id not in tasks:
                        task = self._load_task_from_disk(task_id)
                        if task:
                            tasks[task_id] = task
            task_list = list(tasks.values())
            if task_type:
                task_list = [t for t in task_list if t.task_type == task_type]
            return sorted(task_list, key=lambda x: x.created_at, reverse=True)
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """清理旧任务"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        with self._task_lock:
            old_ids = [
                tid for tid, task in self._tasks.items()
                if task.created_at < cutoff and task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
            ]
            for tid in old_ids:
                del self._tasks[tid]
                path = self._get_task_path(tid)
                if os.path.exists(path):
                    os.remove(path)
