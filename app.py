import streamlit as st
import pandas as pd
import time
from streamlit_echarts import st_echarts
from src.core.models import Cluster, NPU, Task, TaskType
from src.core.simulator import Simulator
from src.scheduler.strategies import FIFOScheduler, OptimizedScheduler
from src.vis.charts import render_gantt_chart, render_utilization_heatmap
import os
import signal

# Page Config
st.set_page_config(
    page_title="Ascend NPU Scheduler Sim",
    page_icon="🧊",
    layout="wide",
)

# Title
st.title("🚀 Ascend NPU Resource Scheduling Simulation Platform")
st.markdown("### Industrial-grade simulation for large-scale heterogeneous clusters")

# Sidebar - Configuration
st.sidebar.header("Simulation Config")
npu_count = st.sidebar.slider("Number of NPUs", 4, 64, 8, step=4)
algorithm = st.sidebar.selectbox("Scheduling Algorithm", ["FIFO", "Optimized (Adapter-Aware)"])
uploaded_file = st.sidebar.file_uploader("Upload Workload Trace (CSV)", type=["csv"])

if st.sidebar.button("🛑 Exit App"):
    st.warning("Shutting down Application...")
    time.sleep(1)
    # Gracefully kill the process
    os.kill(os.getpid(), signal.SIGTERM)

# Helper: Mock Data Generator
def generate_mock_tasks(n=10):
    tasks = []
    for i in range(n):
        tasks.append(Task(
            job_id=f"job_{i}",
            task_type=TaskType.TRAINING,
            arrival_time=i * 2.0,
            duration=10.0,
            memory_requirement_gb=16.0,
            npu_requirement=1
        ))
    return tasks

# Helper: Initialize Cluster
def init_cluster(n_npus):
    cluster = Cluster()
    node_id = "node_0"
    for i in range(n_npus):
        if i % 8 == 0: node_id = f"node_{i//8}"
        cluster.add_npu(NPU(npu_id=f"npu_{i}", node_id=node_id))
    return cluster

# Main Logic
if st.button("Start Simulation"):
    with st.spinner("Initializing Simulation Cluster..."):
        cluster = init_cluster(npu_count)
        
        # Load tasks
        if uploaded_file:
            # TODO: Parse CSV
            st.warning("CSV parsing not implemented yet, using mock data.")
            tasks = generate_mock_tasks(20)
        else:
            tasks = generate_mock_tasks(20)
            
        # Select Scheduler
        if algorithm == "FIFO":
            scheduler = FIFOScheduler(cluster)
        else:
            scheduler = OptimizedScheduler(cluster)
            
        sim = Simulator(cluster, scheduler, tasks)
    
    st.success("Simulation Started!")
    
    # Run Simulation
    start_time = time.time()
    log = sim.run()
    duration = time.time() - start_time
    
    st.metric("Simulation Time (Real)", f"{duration:.4f} s")
    st.metric("Total Events Processed", len(log))

    # Visualization using ECharts
    st.markdown("### 📊 Visualization")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Micro-Gantt (Device Schedule)")
        # Filter only completed or started tasks
        visible_tasks = [t for t in sim.completed_tasks] + [t for t in sim.pending_tasks if t.allocated_npu_ids]
        gantt_option = render_gantt_chart(visible_tasks)
        if gantt_option:
            st_echarts(options=gantt_option, height="400px")
        else:
            st.info("No schedule to display")

    with col2:
        st.markdown("#### Cluster Heatmap")
        # Extract NPU list
        npu_list = sorted(list(cluster.npus.keys()))
        heatmap_option = render_utilization_heatmap(log, npu_list) # Using dummy logic inside for now
        if heatmap_option:
            st_echarts(options=heatmap_option, height="400px")
        
    
    # Comparison Logic (Session State)
    if "results" not in st.session_state:
        st.session_state.results = {}
    
    # Save current run
    run_key = f"{algorithm} ({len(tasks)} tasks)"
    st.session_state.results[run_key] = {
        "duration": duration,
        "makespan": sim.current_time
    }
    
    st.markdown("---")
    st.markdown("### 📈 Algorithm Comparison")
    
    if len(st.session_state.results) > 0:
        comp_df = pd.DataFrame(st.session_state.results).T
        st.dataframe(comp_df)
        
        # Simple Bar Chart for comparison
        st.bar_chart(comp_df["makespan"])
    else:
        st.info("Run multiple simulations with different algorithms to see comparison here.")

else:
    st.info("Configure settings and click 'Start Simulation'")
