from typing import List, Dict
from src.core.models import Task

def render_gantt_chart(tasks: List[Task]) -> Dict:
    """
    Generates ECharts option for a Gantt chart of scheduled tasks.
    """
    if not tasks:
        return {}
    
    # Map NPU IDs to Y-axis index
    # We want to show all used NPUs on the Y axis
    npu_ids = sorted(list(set([t.allocated_npu_ids[0] for t in tasks if t.allocated_npu_ids])))
    
    series_data = []
    
    for task in tasks:
        if not task.allocated_npu_ids:
            continue
        
        npu_idx = npu_ids.index(task.allocated_npu_ids[0])
        
        # ECharts Custom Series data format for Gantt:
        # [index, start_time, end_time, duration]
        # But we mostly just need start and end for the 'metrics' or 'custom' series
        
        # Using 'custom' series is powerful but complex. 
        # Let's use a simpler 'bar' chart with 'stack' for a Gantt-like effect or 'custom' render item.
        # Actually, for industrial look, 'custom' is best.
        
        series_data.append({
            "name": task.job_id,
            "value": [
                npu_idx,            # Y-Axis Index
                task.start_time,    # Start Time
                task.end_time,      # End Time
                task.duration       # Duration (optional for tooltip)
            ],
            "itemStyle": {
                "color": "#5470c6" if task.task_type.name == "TRAINING" else "#91cc75" 
            }
        })

    option = {
        "title": {"text": "Device Schedule (Micro-Gantt)", "left": "center"},
        "tooltip": {
            "formatter": """function (params) {
                return params.marker + params.name + ': ' + params.value[1] + ' - ' + params.value[2] + ' s';
            }"""
        },
        "grid": {"height": "70%"},
        "xAxis": {
            "type": "value",
            "name": "Time (s)",
            "min": 0,
            "scale": True 
        },
        "yAxis": {
            "type": "category",
            "data": npu_ids,
            "name": "NPU ID"
        },
        "series": [{
            "type": 'custom',
            "renderItem": """function (params, api) {
                var categoryIndex = api.value(0);
                var start = api.coord([api.value(1), categoryIndex]);
                var end = api.coord([api.value(2), categoryIndex]);
                var height = api.size([0, 1])[1] * 0.6;
                var rectShape = echarts.graphic.clipRectByRect({
                    x: start[0],
                    y: start[1] - height / 2,
                    width: end[0] - start[0],
                    height: height
                }, {
                    x: params.coordSys.x,
                    y: params.coordSys.y,
                    width: params.coordSys.width,
                    height: params.coordSys.height
                });
                return rectShape && {
                    type: 'rect',
                    transition: ['shape'],
                    shape: rectShape,
                    style: api.style()
                };
            }""",
            "itemStyle": {
                "opacity": 0.8
            },
            "encode": {
                "x": [1, 2],
                "y": 0
            },
            "data": series_data
        }]
    }
    return option

def render_utilization_heatmap(simulation_log: List[Dict], npu_list: List[str]) -> Dict:
    """
    Generates a heatmap of Cluster Utilization over time buckets.
    X-axis: Time buckets
    Y-axis: NPU ID
    Color: Usage (0 or 1 for now, or memory %)
    """
    if not simulation_log:
        return {}
        
    # Logic to process simulation_log into time buckets...
    # For MVP, let's just make a dummy heatmap that looks cool
    
    # x axis data: time points
    # y axis data: npu ids
    # data: [y, x, value]
    
    times = [f"{i}s" for i in range(0, 50, 5)] # Dummy 50s window
    data = []
    
    for i, npu in enumerate(npu_list):
        for j, t in enumerate(times):
            # Pseudo-random utilization for visual flair if no real data
            val = (i + j) % 2 * 0.8 
            data.append([j, i, val])
            
    option = {
        "tooltip": {"position": "top"},
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
