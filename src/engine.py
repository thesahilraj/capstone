"""Unified Simulation Engine Controller.
Coordinates data ingestion, validation, algorithm execution across all 4 OS modules,
performance analysis, figure plotting, and artifact persistence.
"""

import os
import json
from typing import Dict, Any, Optional, List
from .utils.logger import get_logger
from .utils.exceptions import ValidationError
from .utils.validator import InputValidator
from .modules.cpu_scheduler import CPUScheduler, Process, ScheduleResult
from .modules.memory_manager import (
    ContiguousMemoryManager,
    PageReplacementSimulator,
    ContiguousAllocationResult,
    PageReplacementResult
)
from .modules.deadlock_guard import BankersAlgorithm, SafetyResult, RequestEvaluationResult
from .modules.disk_scheduler import DiskScheduler, DiskScheduleResult
from .analytics.metrics import MetricsFormatter
from .analytics.visualizer import SimulationVisualizer
from .analytics.report_generator import PDFReportGenerator

class SimulationEngine:
    """Master controller managing simulation lifecycles and batch workloads."""

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            self.base_dir = os.path.dirname(os.path.dirname(__file__))
        else:
            self.base_dir = base_dir

        self.logger = get_logger("SimulationEngine")
        self.visualizer = SimulationVisualizer(os.path.join(self.base_dir, "output", "figures"))
        self.traces_dir = os.path.join(self.base_dir, "output", "traces")
        self.tables_dir = os.path.join(self.base_dir, "output", "tables")
        self.reports_dir = os.path.join(self.base_dir, "output", "reports")

        for d in [self.traces_dir, self.tables_dir, self.reports_dir]:
            os.makedirs(d, exist_ok=True)

    def load_workload(self, json_path: str) -> Dict[str, Any]:
        """Load and parse workload configuration from JSON file."""
        if not os.path.isabs(json_path):
            json_path = os.path.join(self.base_dir, json_path)

        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Workload file not found at: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.logger.info(f"Loaded workload configuration from {json_path}")
        return data

    def run_cpu_benchmark(self, cpu_config: Dict[str, Any], generate_plots: bool = True) -> Dict[str, ScheduleResult]:
        """Execute full CPU scheduling benchmark."""
        processes_raw = cpu_config.get("processes", [])
        quantum = cpu_config.get("round_robin_quantum", 2)
        InputValidator.validate_cpu_workload(processes_raw, quantum)

        procs = [
            Process(
                pid=str(p["pid"]),
                arrival_time=int(p["arrival_time"]),
                burst_time=int(p["burst_time"]),
                priority=int(p.get("priority", 0))
            )
            for p in processes_raw
        ]

        self.logger.info(f"Running CPU Scheduling benchmark across {len(procs)} processes (Quantum={quantum})")
        results = CPUScheduler.run_all(procs, quantum=quantum)

        # Trace persistence
        trace_file = os.path.join(self.traces_dir, "cpu_scheduling_trace.json")
        with open(trace_file, "w", encoding="utf-8") as f:
            json.dump({k: v.to_dict() for k, v in results.items()}, f, indent=2)

        # Plot figures
        if generate_plots:
            fcfs_res = results.get("FCFS")
            if fcfs_res:
                self.visualizer.plot_cpu_gantt_chart(fcfs_res, "cpu_gantt_chart.png")
            self.visualizer.plot_cpu_algorithm_comparison(results, "cpu_comparison.png")

        return results

    def run_memory_benchmark(self, memory_config: Dict[str, Any], generate_plots: bool = True) -> Dict[str, Any]:
        """Execute Memory Partitioning and Page Replacement benchmarks."""
        # 1. Contiguous allocation
        part_config = memory_config.get("partitioning", memory_config.get("memory_partitioning", {}))
        paging_config = memory_config.get("paging", memory_config.get("page_replacement", {}))

        part_results = {}
        if part_config:
            partitions = part_config.get("initial_partitions", [100, 500, 200, 300, 600])
            requests = part_config.get("process_requests", [])
            total_size = part_config.get("total_memory_size", sum(partitions))
            InputValidator.validate_memory_partitioning(total_size, partitions, requests)

            mgr = ContiguousMemoryManager(partitions)
            part_results = {
                "First_Fit": mgr.simulate_allocation("FIRST_FIT", requests),
                "Best_Fit": mgr.simulate_allocation("BEST_FIT", requests),
                "Worst_Fit": mgr.simulate_allocation("WORST_FIT", requests)
            }

        # 2. Page replacement
        paging_results = {}
        if paging_config:
            capacity = paging_config.get("frame_capacity", 3)
            ref_string = paging_config.get("reference_string", [7, 0, 1, 2, 0, 3, 0, 4, 2, 3])
            InputValidator.validate_page_replacement(capacity, ref_string)

            self.logger.info(f"Simulating page replacement (Frames={capacity}, References={len(ref_string)})")
            paging_results = PageReplacementSimulator.run_all(capacity, ref_string)

            if generate_plots:
                self.visualizer.plot_page_replacement_comparison(paging_results, "page_replacement_comparison.png")

        # Save traces
        trace_file = os.path.join(self.traces_dir, "memory_trace.json")
        with open(trace_file, "w", encoding="utf-8") as f:
            dump_data = {
                "contiguous": {k: v.to_dict() for k, v in part_results.items()},
                "paging": {k: v.to_dict() for k, v in paging_results.items()}
            }
            json.dump(dump_data, f, indent=2)

        return {"contiguous": part_results, "paging": paging_results}

    def run_deadlock_benchmark(self, deadlock_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Banker's Algorithm safety and request evaluation."""
        res_types = deadlock_config.get("resource_types", ["A", "B", "C"])
        avail = deadlock_config.get("available", [3, 3, 2])
        processes = deadlock_config.get("processes", ["P0", "P1", "P2", "P3", "P4"])
        alloc = deadlock_config.get("allocation", [])
        maximum = deadlock_config.get("maximum", [])

        banker = BankersAlgorithm(res_types, avail, processes, alloc, maximum)
        safety_eval = banker.check_safety()
        self.logger.info(f"Banker's Safety Check: {safety_eval.explanation}")

        # Test sample request if present
        request_eval = None
        sample_req = deadlock_config.get("sample_request")
        if sample_req:
            pid = sample_req.get("process_id", processes[0])
            req_vec = sample_req.get("request", [1, 0, 2])
            request_eval = banker.request_resources(pid, req_vec)

        # Save trace
        trace_file = os.path.join(self.traces_dir, "deadlock_trace.json")
        with open(trace_file, "w", encoding="utf-8") as f:
            json.dump({
                "safety": safety_eval.to_dict(),
                "request": request_eval.to_dict() if request_eval else None
            }, f, indent=2)

        return {"safety": safety_eval, "request": request_eval, "state": banker.get_state_summary()}

    def run_disk_benchmark(self, disk_config: Dict[str, Any], generate_plots: bool = True) -> Dict[str, DiskScheduleResult]:
        """Execute Disk Scheduling algorithms across all 6 policies."""
        head = disk_config.get("initial_head_position", 50)
        cylinders = disk_config.get("disk_cylinders", 200)
        requests = disk_config.get("requests", [98, 183, 37, 122, 14, 124, 65, 67])
        direction = disk_config.get("direction", "RIGHT")

        InputValidator.validate_disk_workload(head, cylinders, requests)
        self.logger.info(f"Simulating disk scheduling from head={head} on {cylinders} cylinders (direction={direction})")

        results = DiskScheduler.run_all(head, cylinders, requests, direction)

        # Save trace
        trace_file = os.path.join(self.traces_dir, "disk_scheduling_trace.json")
        with open(trace_file, "w", encoding="utf-8") as f:
            json.dump({k: v.to_dict() for k, v in results.items()}, f, indent=2)

        if generate_plots:
            self.visualizer.plot_disk_trajectories(results, "disk_trajectories.png")

        return results

    def run_full_suite(self, workload_file: str = "data/sample_workload.json") -> Dict[str, Any]:
        """Run complete suite across all 4 modules and generate comprehensive PDF report."""
        config = self.load_workload(workload_file)

        self.logger.info("==================================================")
        self.logger.info("STARTING FULL OS-SIMSUITE BENCHMARK EXECUTION")
        self.logger.info("==================================================")

        cpu_res = self.run_cpu_benchmark(config.get("cpu_scheduling", {}), generate_plots=True)
        mem_res = self.run_memory_benchmark(config, generate_plots=True)
        deadlock_res = self.run_deadlock_benchmark(config.get("deadlock_bankers", {}))
        disk_res = self.run_disk_benchmark(config.get("disk_scheduling", {}), generate_plots=True)

        # Generate Master PDF Report
        pdf_gen = PDFReportGenerator(os.path.join(self.reports_dir, "Capstone_Final_Report.pdf"))
        portal_img = os.path.join(self.base_dir, "docs", "assets", "capstone_assignment_portal.png")
        cpu_gantt = os.path.join(self.base_dir, "output", "figures", "cpu_gantt_chart.png")
        cpu_comp = os.path.join(self.base_dir, "output", "figures", "cpu_comparison.png")
        disk_traj = os.path.join(self.base_dir, "output", "figures", "disk_trajectories.png")
        page_comp = os.path.join(self.base_dir, "output", "figures", "page_replacement_comparison.png")

        pdf_path = pdf_gen.build_report(
            portal_image_path=portal_img,
            cpu_gantt_path=cpu_gantt,
            cpu_comp_path=cpu_comp,
            disk_chart_path=disk_traj,
            memory_chart_path=page_comp,
            student_name="Sahil Raj",
            roll_number="2401410004"
        )
        self.logger.info(f"Master PDF Report generated at: {pdf_path}")

        return {
            "cpu": cpu_res,
            "memory": mem_res,
            "deadlock": deadlock_res,
            "disk": disk_res,
            "pdf_report": pdf_path
        }
