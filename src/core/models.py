from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from enum import Enum

class TaskType(Enum):
    TRAINING = "training"
    LORA_FINETUNE = "lora_finetune"
    INFERENCE = "inference"

class Task(BaseModel):
    """Represents a computational task (job) to be scheduled."""
    job_id: str
    task_type: TaskType
    arrival_time: float
    duration: float  # Estimated duration in seconds
    memory_requirement_gb: float
    npu_requirement: int = 1 # Number of NPUs needed
    priority: int = 1
    
    # Simulation state
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    allocated_npu_ids: List[str] = []

class NPU(BaseModel):
    """Represents a single Ascend NPU."""
    npu_id: str
    node_id: str
    memory_capacity_gb: float = 32.0 # Standard 32GB or 64GB
    current_memory_usage: float = 0.0
    status: Literal["IDLE", "BUSY"] = "IDLE"

class Cluster(BaseModel):
    """Represents the entire cluster."""
    npus: Dict[str, NPU] = {}
    
    def add_npu(self, npu: NPU):
        self.npus[npu.npu_id] = npu

class SimulationConfig(BaseModel):
    """Configuration for a simulation run."""
    total_npus: int = 8
    memory_per_npu: float = 32.0
    algorithm: str = "FIFO"
    duration_limit: float = 3600.0 # Stop after 1 hour sim time
