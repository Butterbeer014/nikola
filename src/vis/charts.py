from typing import List, Dict, Any
from src.core.models import Task
from streamlit_echarts import JsCode
import plotly.express as px
import pandas as pd

def render_gantt_chart(tasks: List[Task]) -> Any:
    """
    Generates a Plotly Figure for a Gantt chart of scheduled tasks.
    """
    if not tasks:
        return None
    
    data = []
    for task in tasks:
        if not task.allocated_npu_ids:
            continue
        for npu in task.allocated_npu_ids:
            data.append({
                "NPU ID": npu,
                "Start": task.start_time,
                "Duration": task.duration,
                "Job ID": task.job_id,
                "Type": task.task_type.name
            })
            
    if not data:
        return None
        
    df = pd.DataFrame(data)
    # Sort to ensure consistent Y-axis order
    df = df.sort_values(by=["NPU ID", "Start"], ascending=[True, True])
    
    color_map = {
        "TRAINING": "#5470c6",
        "LORA_FINETUNE": "#fac858",
        "INFERENCE": "#91cc75"
    }
    
    fig = px.bar(
        df,
        x="Duration",
        y="NPU ID",
        base="Start",
        color="Type",
        orientation='h',
        hover_name="Job ID",
        hover_data={"Start": True, "Duration": True, "Type": False},
        color_discrete_map=color_map,
        title="Device Schedule (Micro-Gantt)"
    )
    
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        xaxis_title="Time (s)",
        yaxis_title="NPU ID",
        margin=dict(t=40, b=40, l=40, r=40),
        height=400
    )
    
    return fig

def render_utilization_heatmap(tasks: List[Task], npu_list: List[str], max_time: float) -> Dict:
    """
    Generates a heatmap of Cluster memory utilization over time buckets.
    X-axis: Time buckets
    Y-axis: NPU ID
    """
    if not tasks or max_time <= 0:
        return {}
        
    num_buckets = 20
    bucket_size = max_time / num_buckets
    times = [f"{i * bucket_size:.1f}s" for i in range(num_buckets)]
    
    data = []
    
    # Calculate usage per NPU per bucket
    for i, npu in enumerate(npu_list):
        for j in range(num_buckets):
            bucket_start = j * bucket_size
            bucket_end = (j + 1) * bucket_size
            
            # Find tasks that span this bucket on this NPU
            usage = 0.0
            for task in tasks:
                if task.allocated_npu_ids and npu in task.allocated_npu_ids:
                    # Check overlap
                    overlap_start = max(bucket_start, task.start_time)
                    overlap_end = min(bucket_end, task.end_time)
                    if overlap_start < overlap_end:
                        # Normalize usage to roughly 0..1 scale based on memory (max 64GB)
                        usage += task.memory_requirement_gb / 64.0
            
            # Clamp to max 1.0 just for display
            val = min(1.0, usage)
            data.append([j, i, val])
            
    option = {
        "tooltip": {"position": "top", "formatter": JsCode("""function(params){
            return 'NPU ' + params.name + '<br>' + params.value[0] + ' bucket<br>Usage: ' + (params.value[2]*100).toFixed(1) + '%';
        }""").js_code},
        "grid": {"height": "50%", "top": "10%"},
        "xAxis": {"type": "category", "data": times, "splitArea": {"show": True}},
        "yAxis": {"type": "category", "data": npu_list, "splitArea": {"show": True}},
        "visualMap": {
            "min": 0,
            "max": 1,
            "calculable": True,
            "orient": "horizontal",
            "left": "center",
            "bottom": "0%",
            "inRange": {
                "color": ['#f6efa6', '#d88273', '#bf444c'] # Heatmap colors
            }
        },
        "series": [{
            "name": "Utilization",
            "type": "heatmap",
            "data": data,
            "label": {"show": False},
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowColor": "rgba(0, 0, 0, 0.5)"
                }
            }
        }]
    }
    return option
