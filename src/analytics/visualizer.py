"""Matplotlib Visualizer generating publication-quality figures:
Gantt charts, Disk seek trajectory lines, and comparative performance bar graphs.
"""

import os
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless rendering
import matplotlib.pyplot as plt
from typing import Dict, List, Optional
from ..modules.cpu_scheduler import ScheduleResult
from ..modules.memory_manager import PageReplacementResult
from ..modules.disk_scheduler import DiskScheduleResult

class SimulationVisualizer:
    """Renders and saves PNG figures for simulation outcomes."""

    def __init__(self, output_dir: Optional[str] = None):
        if output_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.output_dir = os.path.join(base_dir, "output", "figures")
        else:
            self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def plot_cpu_gantt_chart(self, res: ScheduleResult, filename: str = "cpu_gantt_chart.png") -> str:
        """Plot a horizontal Gantt chart showing process execution timeline."""
        filepath = os.path.join(self.output_dir, filename)
        fig, ax = plt.subplots(figsize=(10, 3.5), dpi=300)

        color_palette = [
            "#4C72B0", "#55A868", "#C44E52", "#8172B2", "#CCB974",
            "#64B5CD", "#8C8C8C", "#E377C2", "#17BECF", "#BCBD22"
        ]
        unique_pids = sorted(list({s.pid for s in res.gantt_chart if s.pid != "IDLE"}))
        pid_colors = {pid: color_palette[idx % len(color_palette)] for idx, pid in enumerate(unique_pids)}
        pid_colors["IDLE"] = "#D3D3D3"

        for s in res.gantt_chart:
            duration = s.end_time - s.start_time
            color = pid_colors.get(s.pid, "#A0A0A0")
            hatch = "//" if s.pid == "IDLE" else ""
            ax.barh(y=0, width=duration, left=s.start_time, height=0.6, align="center",
                    color=color, edgecolor="black", linewidth=1.2, hatch=hatch)
            # Label
            mid = s.start_time + duration / 2
            ax.text(mid, 0, s.pid, ha="center", va="center", color="white" if s.pid != "IDLE" else "black",
                    fontweight="bold", fontsize=10)

        max_time = res.total_time
        ax.set_xlim(0, max_time + 1)
        ax.set_ylim(-0.8, 0.8)
        ax.set_yticks([])
        ax.set_xlabel("Simulation Time Units (Timeline)", fontweight="bold", fontsize=11)
        ax.set_title(f"CPU Scheduling Gantt Chart: {res.algorithm_name}", fontweight="bold", fontsize=13, pad=12)
        ax.grid(axis="x", linestyle="--", alpha=0.7)

        # X ticks at every Gantt boundary
        ticks = sorted(list({s.start_time for s in res.gantt_chart} | {s.end_time for s in res.gantt_chart}))
        ax.set_xticks(ticks)

        plt.tight_layout()
        plt.savefig(filepath, bbox_inches="tight")
        plt.close(fig)
        return filepath

    def plot_cpu_algorithm_comparison(self, results: Dict[str, ScheduleResult], filename: str = "cpu_comparison.png") -> str:
        """Plot comparative bar chart of Waiting Time and Turnaround Time across algorithms."""
        filepath = os.path.join(self.output_dir, filename)
        fig, ax = plt.subplots(figsize=(9, 5), dpi=300)

        algos = list(results.keys())
        avg_wt = [results[k].average_waiting_time for k in algos]
        avg_tat = [results[k].average_turnaround_time for k in algos]

        x = range(len(algos))
        width = 0.35

        rects1 = ax.bar([i - width/2 for i in x], avg_wt, width, label="Avg Waiting Time", color="#4C72B0", edgecolor="black")
        rects2 = ax.bar([i + width/2 for i in x], avg_tat, width, label="Avg Turnaround Time", color="#55A868", edgecolor="black")

        ax.set_ylabel("Time Units", fontweight="bold", fontsize=11)
        ax.set_title("CPU Scheduling Performance Metrics Comparison", fontweight="bold", fontsize=13, pad=12)
        ax.set_xticks(list(x))
        ax.set_xticklabels(algos, fontweight="bold", fontsize=10)
        ax.legend(frameon=True)
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        # Value annotations
        for rect in rects1:
            h = rect.get_height()
            ax.annotate(f"{h:.1f}", xy=(rect.get_x() + rect.get_width()/2, h),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8)
        for rect in rects2:
            h = rect.get_height()
            ax.annotate(f"{h:.1f}", xy=(rect.get_x() + rect.get_width()/2, h),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8)

        plt.tight_layout()
        plt.savefig(filepath, bbox_inches="tight")
        plt.close(fig)
        return filepath

    def plot_disk_trajectories(self, results: Dict[str, DiskScheduleResult], filename: str = "disk_trajectories.png") -> str:
        """Plot disk head movement paths across cylinder tracks."""
        filepath = os.path.join(self.output_dir, filename)
        fig, ax = plt.subplots(figsize=(9, 6), dpi=300)

        colors = ["#4C72B0", "#55A868", "#C44E52", "#8172B2", "#CCB974", "#64B5CD"]
        for idx, (algo_key, res) in enumerate(results.items()):
            color = colors[idx % len(colors)]
            steps = range(len(res.seek_sequence))
            ax.plot(res.seek_sequence, steps, marker="o", markersize=4, label=f"{algo_key} (Move: {res.total_head_movement})",
                    color=color, linewidth=1.8, alpha=0.85)

        first_res = next(iter(results.values()))
        ax.set_xlim(-5, first_res.disk_cylinders + 5)
        ax.set_xlabel("Disk Cylinder / Track Number", fontweight="bold", fontsize=11)
        ax.set_ylabel("Step / Sequence Order (Top to Bottom)", fontweight="bold", fontsize=11)
        ax.invert_yaxis()
        ax.set_title("Disk Head Scheduling Trajectory Comparison", fontweight="bold", fontsize=13, pad=12)
        ax.legend(loc="upper right", frameon=True)
        ax.grid(True, linestyle="--", alpha=0.6)

        plt.tight_layout()
        plt.savefig(filepath, bbox_inches="tight")
        plt.close(fig)
        return filepath

    def plot_page_replacement_comparison(self, results: Dict[str, PageReplacementResult], filename: str = "page_replacement_comparison.png") -> str:
        """Plot page faults and hit ratios across FIFO, LRU, and Optimal algorithms."""
        filepath = os.path.join(self.output_dir, filename)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), dpi=300)

        algos = list(results.keys())
        faults = [results[k].page_faults for k in algos]
        hits = [results[k].page_hits for k in algos]
        hit_pcts = [results[k].hit_ratio * 100 for k in algos]

        # Subplot 1: Faults vs Hits stacked bar
        ax1.bar(algos, faults, label="Page Faults", color="#C44E52", edgecolor="black", width=0.5)
        ax1.bar(algos, hits, bottom=faults, label="Page Hits", color="#55A868", edgecolor="black", width=0.5)
        ax1.set_ylabel("Count of References", fontweight="bold")
        ax1.set_title("Total Faults vs. Hits", fontweight="bold")
        ax1.legend()
        ax1.grid(axis="y", linestyle="--", alpha=0.6)

        # Subplot 2: Hit Ratio percentage
        bars = ax2.bar(algos, hit_pcts, color="#4C72B0", edgecolor="black", width=0.5)
        ax2.set_ylabel("Hit Ratio (%)", fontweight="bold")
        ax2.set_ylim(0, 100)
        ax2.set_title("Cache Hit Ratio Comparison", fontweight="bold")
        ax2.grid(axis="y", linestyle="--", alpha=0.6)

        for bar in bars:
            h = bar.get_height()
            ax2.annotate(f"{h:.1f}%", xy=(bar.get_x() + bar.get_width()/2, h),
                         xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontweight="bold")

        plt.suptitle("Virtual Memory Page Replacement Analysis", fontweight="bold", fontsize=13, y=1.02)
        plt.tight_layout()
        plt.savefig(filepath, bbox_inches="tight")
        plt.close(fig)
        return filepath
