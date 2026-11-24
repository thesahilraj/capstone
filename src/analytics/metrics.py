"""Metrics aggregation and tabular comparison formatting."""

from typing import Dict, List, Any
import tabulate
from ..modules.cpu_scheduler import ScheduleResult
from ..modules.memory_manager import PageReplacementResult, ContiguousAllocationResult
from ..modules.disk_scheduler import DiskScheduleResult
from ..modules.deadlock_guard import SafetyResult

class MetricsFormatter:
    """Formats simulation metrics into ASCII/Unicode tables for CLI and report generation."""

    @staticmethod
    def format_cpu_comparison(results: Dict[str, ScheduleResult]) -> str:
        headers = ["Algorithm", "Avg Waiting", "Avg Turnaround", "Avg Response", "CPU Util %", "Throughput", "Total Time"]
        rows = []
        for key, res in results.items():
            rows.append([
                res.algorithm_name,
                f"{res.average_waiting_time:.2f}",
                f"{res.average_turnaround_time:.2f}",
                f"{res.average_response_time:.2f}",
                f"{res.cpu_utilization_pct:.1f}%",
                f"{res.throughput:.4f}",
                res.total_time
            ])
        return tabulate.tabulate(rows, headers=headers, tablefmt="grid")

    @staticmethod
    def format_cpu_process_table(res: ScheduleResult) -> str:
        headers = ["PID", "Arrival", "Burst", "Priority", "Start", "Completion", "Turnaround", "Waiting", "Response"]
        rows = []
        for p in res.processes:
            rows.append([
                p.pid,
                p.arrival_time,
                p.burst_time,
                p.priority,
                p.start_time,
                p.completion_time,
                p.turnaround_time,
                p.waiting_time,
                p.response_time
            ])
        return tabulate.tabulate(rows, headers=headers, tablefmt="grid")

    @staticmethod
    def format_page_replacement_comparison(results: Dict[str, PageReplacementResult]) -> str:
        headers = ["Algorithm", "Frames", "References", "Page Faults", "Page Hits", "Fault Ratio", "Hit Ratio"]
        rows = []
        for key, res in results.items():
            rows.append([
                res.algorithm_name,
                res.frame_capacity,
                res.total_references,
                res.page_faults,
                res.page_hits,
                f"{res.fault_ratio * 100:.2f}%",
                f"{res.hit_ratio * 100:.2f}%"
            ])
        return tabulate.tabulate(rows, headers=headers, tablefmt="grid")

    @staticmethod
    def format_disk_comparison(results: Dict[str, DiskScheduleResult]) -> str:
        headers = ["Algorithm", "Initial Head", "Direction", "Total Seek Movement", "Avg Seek Distance", "Seek Path (First 6)"]
        rows = []
        for key, res in results.items():
            path_sample = " -> ".join(map(str, res.seek_sequence[:6]))
            if len(res.seek_sequence) > 6:
                path_sample += "..."
            rows.append([
                res.algorithm_name,
                res.initial_head,
                res.direction,
                res.total_head_movement,
                f"{res.average_seek_distance:.2f}",
                path_sample
            ])
        return tabulate.tabulate(rows, headers=headers, tablefmt="grid")

    @staticmethod
    def format_memory_contiguous_table(res: ContiguousAllocationResult) -> str:
        headers = ["Partition #", "Start Addr", "Size (KB)", "Status", "Process ID", "Internal Frag (KB)"]
        rows = []
        for p in res.partitions:
            rows.append([
                p.partition_id,
                p.start_address,
                p.size,
                "ALLOCATED" if p.is_allocated else "FREE",
                p.process_id if p.process_id else "-",
                p.internal_fragmentation if p.is_allocated else "-"
            ])
        return tabulate.tabulate(rows, headers=headers, tablefmt="grid")
