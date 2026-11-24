"""Core OS modules package exports."""
from .cpu_scheduler import CPUScheduler, Process, GanttSlice, ScheduleResult
from .memory_manager import (
    ContiguousMemoryManager,
    PageReplacementSimulator,
    MemoryPartition,
    ContiguousAllocationResult,
    PageReplacementResult,
    PageTraceStep
)
from .deadlock_guard import BankersAlgorithm, SafetyResult, RequestEvaluationResult
from .disk_scheduler import DiskScheduler, DiskScheduleResult

__all__ = [
    "CPUScheduler",
    "Process",
    "GanttSlice",
    "ScheduleResult",
    "ContiguousMemoryManager",
    "PageReplacementSimulator",
    "MemoryPartition",
    "ContiguousAllocationResult",
    "PageReplacementResult",
    "PageTraceStep",
    "BankersAlgorithm",
    "SafetyResult",
    "RequestEvaluationResult",
    "DiskScheduler",
    "DiskScheduleResult"
]
