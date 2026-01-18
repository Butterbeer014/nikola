from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.models import Task, Cluster, NPU

class BaseScheduler(ABC):
    def __init__(self, cluster: Cluster):
        self.cluster = cluster

    @abstractmethod
    def schedule(self, pending_tasks: List[Task], current_time: float) -> List[tuple[Task, List[str]]]:
        """
        Decides which tasks to schedule on which NPUs.
        Returns a list of tuples: (Task, List[npu_ids_to_allocate])
        """
        pass

class FIFOScheduler(BaseScheduler):
    def schedule(self, pending_tasks: List[Task], current_time: float) -> List[tuple[Task, List[str]]]:
        allocations = []
        
        # Simple Logic: Try to schedule tasks in order of arrival,
        # Sort pending by arrival time (should already be sorted, but ensure safety)
        sorted_tasks = sorted(pending_tasks, key=lambda t: t.arrival_time)
        
        for task in sorted_tasks:
            available_npus = self._find_available_npus(task)
            if available_npus:
                allocations.append((task, available_npus))
                # Temporarily mark as busy in local logic to prevent double booking in same tick
                # (Real booking happens in Simulator)
                for npu_id in available_npus:
                    self.cluster.npus[npu_id].status = "BUSY" 
        
        return allocations

    def _find_available_npus(self, task: Task) -> List[str]:
        found = []
        count = 0
        for npu_id, npu in self.cluster.npus.items():
            if npu.status == "IDLE" and npu.current_memory_usage + task.memory_requirement_gb <= npu.memory_capacity_gb:
                found.append(npu_id)
                count += 1
                if count == task.npu_requirement:
                    return found
        return []

class OptimizedScheduler(BaseScheduler):
    """
    Placeholder for the advanced strategy (Adapter-Aware / Pipeline Overlap).
    Currently behaves like FIFO but can be expanded.
    """
    def schedule(self, pending_tasks: List[Task], current_time: float) -> List[tuple[Task, List[str]]]:
        # TODO: Implement fragmentation-aware logic here
        return []
