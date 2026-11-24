"""CPU Process Scheduling Module.
Simulates FCFS, SJF (Non-preemptive), SRTF (Preemptive SJF), Priority (Non-preemptive & Preemptive),
and Round Robin scheduling algorithms with comprehensive performance metrics and Gantt charts.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import copy
from ..utils.exceptions import ValidationError
from ..utils.validator import InputValidator

@dataclass
class Process:
    pid: str
    arrival_time: int
    burst_time: int
    priority: int = 0
    # Dynamic Simulation State
    remaining_time: int = field(init=False)
    start_time: Optional[int] = None
    completion_time: Optional[int] = None
    waiting_time: Optional[int] = None
    turnaround_time: Optional[int] = None
    response_time: Optional[int] = None

    def __post_init__(self):
        self.remaining_time = self.burst_time

    def to_dict(self) -> Dict[str, any]:
        return {
            "pid": self.pid,
            "arrival_time": self.arrival_time,
            "burst_time": self.burst_time,
            "priority": self.priority,
            "start_time": self.start_time,
            "completion_time": self.completion_time,
            "waiting_time": self.waiting_time,
            "turnaround_time": self.turnaround_time,
            "response_time": self.response_time
        }

@dataclass
class GanttSlice:
    pid: str
    start_time: int
    end_time: int

@dataclass
class ScheduleResult:
    algorithm_name: str
    gantt_chart: List[GanttSlice]
    processes: List[Process]
    average_waiting_time: float
    average_turnaround_time: float
    average_response_time: float
    cpu_utilization_pct: float
    throughput: float
    total_time: int

    def to_dict(self) -> Dict[str, any]:
        return {
            "algorithm_name": self.algorithm_name,
            "gantt_chart": [{"pid": s.pid, "start": s.start_time, "end": s.end_time} for s in self.gantt_chart],
            "processes": [p.to_dict() for p in self.processes],
            "average_waiting_time": round(self.average_waiting_time, 2),
            "average_turnaround_time": round(self.average_turnaround_time, 2),
            "average_response_time": round(self.average_response_time, 2),
            "cpu_utilization_pct": round(self.cpu_utilization_pct, 2),
            "throughput": round(self.throughput, 4),
            "total_time": self.total_time
        }


class CPUScheduler:
    """Core CPU Process Scheduling Simulation Engine."""

    @staticmethod
    def _clone_processes(processes: List[Process]) -> List[Process]:
        return [copy.deepcopy(p) for p in processes]

    @staticmethod
    def _compute_metrics(
        algorithm_name: str,
        procs: List[Process],
        gantt: List[GanttSlice],
        current_time: int
    ) -> ScheduleResult:
        n = len(procs)
        if n == 0:
            return ScheduleResult(algorithm_name, [], [], 0.0, 0.0, 0.0, 0.0, 0.0, 0)

        # Merge adjacent identical Gantt slices if any
        condensed_gantt: List[GanttSlice] = []
        for slice_item in gantt:
            if condensed_gantt and condensed_gantt[-1].pid == slice_item.pid and condensed_gantt[-1].end_time == slice_item.start_time:
                condensed_gantt[-1].end_time = slice_item.end_time
            else:
                condensed_gantt.append(slice_item)

        total_burst = sum(p.burst_time for p in procs)
        min_arrival = min(p.arrival_time for p in procs)
        total_time = max(current_time, 1)

        total_wt = 0
        total_tat = 0
        total_rt = 0

        for p in procs:
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            p.response_time = (p.start_time - p.arrival_time) if p.start_time is not None else 0

            total_wt += p.waiting_time
            total_tat += p.turnaround_time
            total_rt += p.response_time

        avg_wt = total_wt / n
        avg_tat = total_tat / n
        avg_rt = total_rt / n
        cpu_util = (total_burst / total_time) * 100.0 if total_time > 0 else 0.0
        throughput = n / total_time if total_time > 0 else 0.0

        return ScheduleResult(
            algorithm_name=algorithm_name,
            gantt_chart=condensed_gantt,
            processes=procs,
            average_waiting_time=avg_wt,
            average_turnaround_time=avg_tat,
            average_response_time=avg_rt,
            cpu_utilization_pct=cpu_util,
            throughput=throughput,
            total_time=total_time
        )

    @classmethod
    def schedule_fcfs(cls, processes: List[Process]) -> ScheduleResult:
        """First-Come, First-Served (Non-preemptive)."""
        procs = cls._clone_processes(processes)
        # Sort by arrival time, then PID for deterministic tie-breaking
        procs.sort(key=lambda p: (p.arrival_time, p.pid))

        current_time = 0
        gantt: List[GanttSlice] = []

        for p in procs:
            if current_time < p.arrival_time:
                # CPU Idle
                gantt.append(GanttSlice("IDLE", current_time, p.arrival_time))
                current_time = p.arrival_time

            p.start_time = current_time
            current_time += p.burst_time
            p.completion_time = current_time
            p.remaining_time = 0
            gantt.append(GanttSlice(p.pid, p.start_time, p.completion_time))

        return cls._compute_metrics("First-Come, First-Served (FCFS)", procs, gantt, current_time)

    @classmethod
    def schedule_sjf_non_preemptive(cls, processes: List[Process]) -> ScheduleResult:
        """Shortest Job First (Non-preemptive)."""
        procs = cls._clone_processes(processes)
        current_time = 0
        completed = 0
        n = len(procs)
        gantt: List[GanttSlice] = []
        is_completed = {p.pid: False for p in procs}

        while completed < n:
            available = [p for p in procs if not is_completed[p.pid] and p.arrival_time <= current_time]
            if not available:
                next_arrival = min(p.arrival_time for p in procs if not is_completed[p.pid])
                gantt.append(GanttSlice("IDLE", current_time, next_arrival))
                current_time = next_arrival
                continue

            # Shortest burst time, tie break with arrival time and pid
            available.sort(key=lambda p: (p.burst_time, p.arrival_time, p.pid))
            chosen = available[0]

            chosen.start_time = current_time
            current_time += chosen.burst_time
            chosen.completion_time = current_time
            chosen.remaining_time = 0
            is_completed[chosen.pid] = True
            completed += 1
            gantt.append(GanttSlice(chosen.pid, chosen.start_time, chosen.completion_time))

        return cls._compute_metrics("Shortest Job First (SJF Non-Preemptive)", procs, gantt, current_time)

    @classmethod
    def schedule_srtf(cls, processes: List[Process]) -> ScheduleResult:
        """Shortest Remaining Time First (SRTF / Preemptive SJF)."""
        procs = cls._clone_processes(processes)
        current_time = 0
        completed = 0
        n = len(procs)
        gantt: List[GanttSlice] = []
        proc_map = {p.pid: p for p in procs}

        last_running_pid: Optional[str] = None
        slice_start = 0

        while completed < n:
            available = [p for p in procs if p.remaining_time > 0 and p.arrival_time <= current_time]
            if not available:
                if last_running_pid is not None:
                    gantt.append(GanttSlice(last_running_pid, slice_start, current_time))
                    last_running_pid = None
                next_arrival = min(p.arrival_time for p in procs if p.remaining_time > 0)
                gantt.append(GanttSlice("IDLE", current_time, next_arrival))
                current_time = next_arrival
                continue

            available.sort(key=lambda p: (p.remaining_time, p.arrival_time, p.pid))
            current_proc = available[0]

            if current_proc.start_time is None:
                current_proc.start_time = current_time

            if last_running_pid != current_proc.pid:
                if last_running_pid is not None:
                    gantt.append(GanttSlice(last_running_pid, slice_start, current_time))
                last_running_pid = current_proc.pid
                slice_start = current_time

            # Step simulation by 1 unit
            current_proc.remaining_time -= 1
            current_time += 1

            if current_proc.remaining_time == 0:
                current_proc.completion_time = current_time
                completed += 1

        if last_running_pid is not None:
            gantt.append(GanttSlice(last_running_pid, slice_start, current_time))

        return cls._compute_metrics("Shortest Remaining Time First (SRTF)", procs, gantt, current_time)

    @classmethod
    def schedule_priority_non_preemptive(cls, processes: List[Process]) -> ScheduleResult:
        """Priority Scheduling (Non-preemptive, lower number = higher priority)."""
        procs = cls._clone_processes(processes)
        current_time = 0
        completed = 0
        n = len(procs)
        gantt: List[GanttSlice] = []
        is_completed = {p.pid: False for p in procs}

        while completed < n:
            available = [p for p in procs if not is_completed[p.pid] and p.arrival_time <= current_time]
            if not available:
                next_arrival = min(p.arrival_time for p in procs if not is_completed[p.pid])
                gantt.append(GanttSlice("IDLE", current_time, next_arrival))
                current_time = next_arrival
                continue

            # Prioritize lowest numerical priority value, then arrival time, then pid
            available.sort(key=lambda p: (p.priority, p.arrival_time, p.pid))
            chosen = available[0]

            chosen.start_time = current_time
            current_time += chosen.burst_time
            chosen.completion_time = current_time
            chosen.remaining_time = 0
            is_completed[chosen.pid] = True
            completed += 1
            gantt.append(GanttSlice(chosen.pid, chosen.start_time, chosen.completion_time))

        return cls._compute_metrics("Priority Scheduling (Non-Preemptive)", procs, gantt, current_time)

    @classmethod
    def schedule_priority_preemptive(cls, processes: List[Process]) -> ScheduleResult:
        """Priority Scheduling (Preemptive, lower number = higher priority)."""
        procs = cls._clone_processes(processes)
        current_time = 0
        completed = 0
        n = len(procs)
        gantt: List[GanttSlice] = []

        last_running_pid: Optional[str] = None
        slice_start = 0

        while completed < n:
            available = [p for p in procs if p.remaining_time > 0 and p.arrival_time <= current_time]
            if not available:
                if last_running_pid is not None:
                    gantt.append(GanttSlice(last_running_pid, slice_start, current_time))
                    last_running_pid = None
                next_arrival = min(p.arrival_time for p in procs if p.remaining_time > 0)
                gantt.append(GanttSlice("IDLE", current_time, next_arrival))
                current_time = next_arrival
                continue

            available.sort(key=lambda p: (p.priority, p.arrival_time, p.pid))
            current_proc = available[0]

            if current_proc.start_time is None:
                current_proc.start_time = current_time

            if last_running_pid != current_proc.pid:
                if last_running_pid is not None:
                    gantt.append(GanttSlice(last_running_pid, slice_start, current_time))
                last_running_pid = current_proc.pid
                slice_start = current_time

            current_proc.remaining_time -= 1
            current_time += 1

            if current_proc.remaining_time == 0:
                current_proc.completion_time = current_time
                completed += 1

        if last_running_pid is not None:
            gantt.append(GanttSlice(last_running_pid, slice_start, current_time))

        return cls._compute_metrics("Priority Scheduling (Preemptive)", procs, gantt, current_time)

    @classmethod
    def schedule_round_robin(cls, processes: List[Process], quantum: int) -> ScheduleResult:
        """Round Robin Scheduling with configurable time quantum."""
        InputValidator.validate_positive_integer(quantum, "quantum")
        procs = cls._clone_processes(processes)
        # Order initial processes by arrival time
        procs.sort(key=lambda p: (p.arrival_time, p.pid))

        ready_queue: List[Process] = []
        gantt: List[GanttSlice] = []
        current_time = 0
        completed = 0
        n = len(procs)
        unvisited = list(procs)

        # Enqueue initial arrivals at time 0
        for p in list(unvisited):
            if p.arrival_time <= current_time:
                ready_queue.append(p)
                unvisited.remove(p)

        while completed < n:
            if not ready_queue:
                if unvisited:
                    next_arrival = min(p.arrival_time for p in unvisited)
                    gantt.append(GanttSlice("IDLE", current_time, next_arrival))
                    current_time = next_arrival
                    for p in list(unvisited):
                        if p.arrival_time <= current_time:
                            ready_queue.append(p)
                            unvisited.remove(p)
                    continue

            current_proc = ready_queue.pop(0)

            if current_proc.start_time is None:
                current_proc.start_time = current_time

            run_time = min(quantum, current_proc.remaining_time)
            slice_start = current_time
            current_time += run_time
            current_proc.remaining_time -= run_time
            gantt.append(GanttSlice(current_proc.pid, slice_start, current_time))

            # Check for new arrivals while process was running
            for p in list(unvisited):
                if p.arrival_time <= current_time:
                    ready_queue.append(p)
                    unvisited.remove(p)

            if current_proc.remaining_time > 0:
                ready_queue.append(current_proc)
            else:
                current_proc.completion_time = current_time
                completed += 1

        return cls._compute_metrics(f"Round Robin (Quantum = {quantum})", procs, gantt, current_time)

    @classmethod
    def run_all(cls, processes: List[Process], quantum: int = 2) -> Dict[str, ScheduleResult]:
        """Run all CPU scheduling algorithms on an identical process workload."""
        return {
            "FCFS": cls.schedule_fcfs(processes),
            "SJF": cls.schedule_sjf_non_preemptive(processes),
            "SRTF": cls.schedule_srtf(processes),
            "Priority_NP": cls.schedule_priority_non_preemptive(processes),
            "Priority_Preemptive": cls.schedule_priority_preemptive(processes),
            "Round_Robin": cls.schedule_round_robin(processes, quantum=quantum)
        }
