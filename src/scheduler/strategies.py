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
    Advanced Strategy: Adapter-Aware / Pipeline Overlap
    For simulation purposes, we improve upon FIFO by prioritizing smaller tasks (Shortest Job First)
    or packing specific task types more efficiently to minimize fragmentation.
    """
    def schedule(self, pending_tasks: List[Task], current_time: float) -> List[tuple[Task, List[str]]]:
        allocations = []
        
        # Sort pending by NPU requirement and duration DESCENDING (Longest / Largest Job First).
        # This reduces fragmentation and minimizes the overall makespan because large workloads 
        # get packed early, and smaller ones comfortably fill the remaining holes.
        sorted_tasks = sorted(pending_tasks, key=lambda t: (t.npu_requirement, t.duration), reverse=True)
        
        for task in sorted_tasks:
            available_npus = self._find_best_fit_npus(task)
            if available_npus:
                allocations.append((task, available_npus))
                for npu_id in available_npus:
                    self.cluster.npus[npu_id].status = "BUSY" 
        
        return allocations

    def _find_best_fit_npus(self, task: Task) -> List[str]:
        # Tries to find NPUs that have the *least* available memory that can still fit the task
        # This helps reduce fragmentation compared to naive FIFO.
        found = []
        count = 0
        
        # Sort NPUs by available memory ascending
        npus_sorted = sorted(
            [npu for npu in self.cluster.npus.values() if npu.status == "IDLE"],
            key=lambda n: n.memory_capacity_gb - n.current_memory_usage
        )
        
        for npu in npus_sorted:
            if npu.current_memory_usage + task.memory_requirement_gb <= npu.memory_capacity_gb:
                found.append(npu.npu_id)
                count += 1
                if count == task.npu_requirement:
                    return found
        return []
