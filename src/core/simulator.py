import heapq
from typing import List, Dict, Any
from src.core.models import Task, Cluster, NPU
from src.scheduler.strategies import BaseScheduler, FIFOScheduler, OptimizedScheduler

class Event:
    def __init__(self, time: float, event_type: str, payload: Any):
        self.time = time
        self.event_type = event_type # 'TASK_ARRIVAL', 'TASK_COMPLETION'
        self.payload = payload

    def __lt__(self, other):
        return self.time < other.time

class Simulator:
    def __init__(self, cluster: Cluster, scheduler: BaseScheduler, tasks: List[Task]):
        self.cluster = cluster
        self.scheduler = scheduler
        self.event_queue = []
        self.current_time = 0.0
        self.completed_tasks = []
        self.pending_tasks = []
        
        # Initialize events
        for task in tasks:
            heapq.heappush(self.event_queue, Event(task.arrival_time, 'TASK_ARRIVAL', task))

    def run(self) -> List[Dict]:
        """
        Runs the simulation until no events occupy the queue.
        Returns a time-series log of events for visualization.
        """
        simulation_log = []

        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time
            
            # Log the step
            simulation_log.append({
                "time": self.current_time,
                "event": event.event_type,
                "task_id": event.payload.job_id if isinstance(event.payload, Task) else "N/A"
            })

            if event.event_type == 'TASK_ARRIVAL':
                task = event.payload
                self.pending_tasks.append(task)
                self._try_schedule()
            
            elif event.event_type == 'TASK_COMPLETION':
                task = event.payload
                self._release_resources(task)
                self.completed_tasks.append(task)
                # Resources freed, try scheduling again
                self._try_schedule()

        return simulation_log

    def _try_schedule(self):
        # Call scheduler
        allocations = self.scheduler.schedule(self.pending_tasks, self.current_time)
        
        for task, npu_ids in allocations:
            # Commit allocation
            task.start_time = self.current_time
            task.end_time = self.current_time + task.duration
            task.allocated_npu_ids = npu_ids
            
            # Update Cluster State
            for npu_id in npu_ids:
                npu = self.cluster.npus[npu_id]
                npu.status = 'BUSY'
                npu.current_memory_usage += task.memory_requirement_gb
            
            # Remove from pending
            if task in self.pending_tasks:
                self.pending_tasks.remove(task)
            
            # Schedule completion event
            heapq.heappush(self.event_queue, Event(task.end_time, 'TASK_COMPLETION', task))

    def _release_resources(self, task: Task):
        for npu_id in task.allocated_npu_ids:
            if npu_id in self.cluster.npus:
                npu = self.cluster.npus[npu_id]
                npu.status = 'IDLE' # Simplified logic (assuming 1 task per NPU for now)
                npu.current_memory_usage -= task.memory_requirement_gb
                if npu.current_memory_usage < 0: npu.current_memory_usage = 0 # Safety
