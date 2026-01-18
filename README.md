# nikola
毕设
# Ascend NPU 仿真平台 - 使用指南

## 概览
本平台主要用于模拟 Ascend NPU 集群上的资源调度。它提供了一个交互式仪表板，用于对比不同调度算法（例如 FIFO 与 优化算法）的性能，并对执行时间线进行可视化。

## 安装与运行
1.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **运行应用**:
    ```bash
    streamlit run app.py
    ```

## 功能特性
-   **配置**: 在侧边栏调整 NPU 数量并选择调度算法。
-   **模拟**: 点击 "Start Simulation" 运行离散事件模拟 (DES) 引擎。
-   **可视化**:
    -   **微观甘特图 (Micro-Gantt)**: 精确查看每个 NPU 上任务的运行时间与流水线情况。
    -   **热力图 (Heatmap)**: 集群利用率的空间分布可视化（目前基于模拟数据）。
-   **对比分析**: 
    1. 选择 "FIFO" 算法运行一次。
    2. 切换到 "Optimized" (或自定义算法) 再运行一次。
    3. 界面底部的 "Algorithm Comparison" 区域将自动显示 Makespan（总完工时间）等关键指标的对比图表。

## 代码结构
-   `app.py`: Streamlit 主程序与 UI 逻辑。
-   `src/core/simulator.py`: 核心仿真引擎 (DES)。
-   `src/vis/charts.py`: 基于 ECharts 的图表生成模块。
-   `src/scheduler/`: 调度策略实现目录。