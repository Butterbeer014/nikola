from src.core.models import Cluster, NPU, Task, TaskType
from src.core.simulator import Simulator
from src.scheduler.strategies import FIFOScheduler

def test_engine():
    print("Initializing Cluster...")
    cluster = Cluster()
    for i in range(4):
        cluster.add_npu(NPU(npu_id=f"npu_{i}", node_id="node_0"))
        
    print("Generating Tasks...")
    tasks = []
    for i in range(5):
        tasks.append(Task(
            job_id=f"job_{i}",
            task_type=TaskType.TRAINING,
            arrival_time=i, # Arrive 1 second apart
            duration=5.0,
            memory_requirement_gb=10.0,
            npu_requirement=1
        ))
        
    print("Initializing Scheduler (FIFO)...")
    scheduler = FIFOScheduler(cluster)
    
    print("Running Simulation...")
    sim = Simulator(cluster, scheduler, tasks)
    log = sim.run()
    
    print(f"Simulation Complete. Processed {len(log)} events.")
    print(f"Makespan: {sim.current_time}")
    
    # Assertions
    assert len(sim.completed_tasks) == 5
    print("TEST PASSED: All tasks completed.")

if __name__ == "__main__":
    test_engine()
