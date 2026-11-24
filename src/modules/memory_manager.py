"""Memory Management Subsystem.
Models dynamic contiguous memory allocation (First-Fit, Best-Fit, Worst-Fit with coalescing & compaction)
and Virtual Memory Page Replacement algorithms (FIFO, LRU, Optimal) with full state tracing.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
import copy
from ..utils.exceptions import AllocationError, ValidationError
from ..utils.validator import InputValidator

# --------------------------------------------------------------------------
# Part A: Contiguous Partition Allocation
# --------------------------------------------------------------------------

@dataclass
class MemoryPartition:
    partition_id: int
    start_address: int
    size: int
    is_allocated: bool = False
    process_id: Optional[str] = None
    process_size: int = 0
    internal_fragmentation: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "partition_id": self.partition_id,
            "start_address": self.start_address,
            "size": self.size,
            "is_allocated": self.is_allocated,
            "process_id": self.process_id,
            "process_size": self.process_size,
            "internal_fragmentation": self.internal_fragmentation
        }

@dataclass
class AllocationStepTrace:
    process_id: str
    requested_size: int
    allocated: bool
    target_partition_id: Optional[int] = None
    message: str = ""

@dataclass
class ContiguousAllocationResult:
    strategy_name: str
    total_memory: int
    partitions: List[MemoryPartition]
    allocation_traces: List[AllocationStepTrace]
    allocated_processes: int
    failed_processes: int
    total_internal_fragmentation: int
    external_fragmentation: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_name": self.strategy_name,
            "total_memory": self.total_memory,
            "partitions": [p.to_dict() for p in self.partitions],
            "allocation_traces": [
                {
                    "process_id": t.process_id,
                    "requested_size": t.requested_size,
                    "allocated": t.allocated,
                    "target_partition_id": t.target_partition_id,
                    "message": t.message
                }
                for t in self.allocation_traces
            ],
            "allocated_processes": self.allocated_processes,
            "failed_processes": self.failed_processes,
            "total_internal_fragmentation": self.total_internal_fragmentation,
            "external_fragmentation": self.external_fragmentation
        }


class ContiguousMemoryManager:
    """Simulates First-Fit, Best-Fit, and Worst-Fit allocation strategies."""

    def __init__(self, partition_sizes: List[int]):
        self.original_sizes = list(partition_sizes)

    def _initialize_partitions(self) -> List[MemoryPartition]:
        partitions = []
        current_addr = 0
        for idx, sz in enumerate(self.original_sizes):
            partitions.append(
                MemoryPartition(
                    partition_id=idx + 1,
                    start_address=current_addr,
                    size=sz,
                    is_allocated=False
                )
            )
            current_addr += sz
        return partitions

    def simulate_allocation(
        self,
        strategy: str,
        requests: List[Dict[str, Any]]
    ) -> ContiguousAllocationResult:
        """Run allocation simulation for First-Fit, Best-Fit, or Worst-Fit."""
        strategy = strategy.upper().replace("-", "_").replace(" ", "_")
        partitions = self._initialize_partitions()
        traces: List[AllocationStepTrace] = []
        allocated_count = 0
        failed_count = 0

        for req in requests:
            pid = str(req.get("pid", f"P_{len(traces)+1}"))
            req_size = int(req["size"])

            # Find candidates: free partitions with size >= req_size
            candidates = [p for p in partitions if not p.is_allocated and p.size >= req_size]

            target: Optional[MemoryPartition] = None
            if strategy in ["FIRST_FIT", "FIRST"]:
                if candidates:
                    target = candidates[0]
            elif strategy in ["BEST_FIT", "BEST"]:
                if candidates:
                    # Smallest partition that fits
                    target = min(candidates, key=lambda p: (p.size, p.partition_id))
            elif strategy in ["WORST_FIT", "WORST"]:
                if candidates:
                    # Largest partition available
                    target = max(candidates, key=lambda p: (p.size, -p.partition_id))
            else:
                raise ValidationError(f"Unknown allocation strategy: {strategy}")

            if target is not None:
                target.is_allocated = True
                target.process_id = pid
                target.process_size = req_size
                target.internal_fragmentation = target.size - req_size
                allocated_count += 1
                traces.append(
                    AllocationStepTrace(
                        process_id=pid,
                        requested_size=req_size,
                        allocated=True,
                        target_partition_id=target.partition_id,
                        message=f"Allocated to Partition {target.partition_id} (Internal Frag: {target.internal_fragmentation} KB)"
                    )
                )
            else:
                failed_count += 1
                free_space = sum(p.size for p in partitions if not p.is_allocated)
                traces.append(
                    AllocationStepTrace(
                        process_id=pid,
                        requested_size=req_size,
                        allocated=False,
                        message=f"Allocation Failed. Total Free Space: {free_space} KB (External Frag: {free_space} KB)"
                    )
                )

        total_int_frag = sum(p.internal_fragmentation for p in partitions if p.is_allocated)
        external_frag = sum(p.size for p in partitions if not p.is_allocated) if failed_count > 0 else 0
        total_mem = sum(self.original_sizes)

        return ContiguousAllocationResult(
            strategy_name=strategy,
            total_memory=total_mem,
            partitions=partitions,
            allocation_traces=traces,
            allocated_processes=allocated_count,
            failed_processes=failed_count,
            total_internal_fragmentation=total_int_frag,
            external_fragmentation=external_frag
        )

    def deallocate(self, partitions: List[MemoryPartition], process_id: str) -> bool:
        """Deallocate partition occupied by process_id."""
        for p in partitions:
            if p.is_allocated and p.process_id == process_id:
                p.is_allocated = False
                p.process_id = None
                p.process_size = 0
                p.internal_fragmentation = 0
                return True
        return False

    def compact_memory(self, partitions: List[MemoryPartition]) -> List[MemoryPartition]:
        """Perform memory compaction by sliding allocated partitions together."""
        compacted: List[MemoryPartition] = []
        current_addr = 0
        allocated = [p for p in partitions if p.is_allocated]
        total_free = sum(p.size for p in partitions if not p.is_allocated)

        for idx, p in enumerate(allocated):
            new_p = MemoryPartition(
                partition_id=idx + 1,
                start_address=current_addr,
                size=p.size,
                is_allocated=True,
                process_id=p.process_id,
                process_size=p.process_size,
                internal_fragmentation=p.internal_fragmentation
            )
            compacted.append(new_p)
            current_addr += p.size

        if total_free > 0:
            compacted.append(
                MemoryPartition(
                    partition_id=len(compacted) + 1,
                    start_address=current_addr,
                    size=total_free,
                    is_allocated=False
                )
            )
        return compacted


# --------------------------------------------------------------------------
# Part B: Virtual Memory Page Replacement
# --------------------------------------------------------------------------

@dataclass
class PageTraceStep:
    step: int
    referenced_page: int
    frames_snapshot: List[Optional[int]]
    is_fault: bool
    evicted_page: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "referenced_page": self.referenced_page,
            "frames": [f for f in self.frames_snapshot],
            "is_fault": self.is_fault,
            "evicted_page": self.evicted_page
        }

@dataclass
class PageReplacementResult:
    algorithm_name: str
    frame_capacity: int
    total_references: int
    page_faults: int
    page_hits: int
    hit_ratio: float
    fault_ratio: float
    trace_steps: List[PageTraceStep]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "algorithm_name": self.algorithm_name,
            "frame_capacity": self.frame_capacity,
            "total_references": self.total_references,
            "page_faults": self.page_faults,
            "page_hits": self.page_hits,
            "hit_ratio": round(self.hit_ratio, 4),
            "fault_ratio": round(self.fault_ratio, 4),
            "trace_steps": [t.to_dict() for t in self.trace_steps]
        }


class PageReplacementSimulator:
    """Simulates FIFO, LRU, and Optimal Page Replacement Policies."""

    @classmethod
    def simulate_fifo(cls, frame_capacity: int, reference_string: List[int]) -> PageReplacementResult:
        """First-In, First-Out (FIFO) Page Replacement."""
        InputValidator.validate_page_replacement(frame_capacity, reference_string)
        frames: List[Optional[int]] = [None] * frame_capacity
        fifo_queue: List[int] = []
        faults = 0
        hits = 0
        traces: List[PageTraceStep] = []

        for step, page in enumerate(reference_string, start=1):
            if page in frames:
                hits += 1
                traces.append(PageTraceStep(step, page, list(frames), is_fault=False, evicted_page=None))
            else:
                faults += 1
                evicted = None
                if None in frames:
                    empty_idx = frames.index(None)
                    frames[empty_idx] = page
                    fifo_queue.append(page)
                else:
                    evicted = fifo_queue.pop(0)
                    evict_idx = frames.index(evicted)
                    frames[evict_idx] = page
                    fifo_queue.append(page)

                traces.append(PageTraceStep(step, page, list(frames), is_fault=True, evicted_page=evicted))

        total = len(reference_string)
        return PageReplacementResult(
            algorithm_name="FIFO (First-In, First-Out)",
            frame_capacity=frame_capacity,
            total_references=total,
            page_faults=faults,
            page_hits=hits,
            hit_ratio=hits / total if total > 0 else 0.0,
            fault_ratio=faults / total if total > 0 else 0.0,
            trace_steps=traces
        )

    @classmethod
    def simulate_lru(cls, frame_capacity: int, reference_string: List[int]) -> PageReplacementResult:
        """Least Recently Used (LRU) Page Replacement."""
        InputValidator.validate_page_replacement(frame_capacity, reference_string)
        frames: List[Optional[int]] = [None] * frame_capacity
        last_used: Dict[int, int] = {}
        faults = 0
        hits = 0
        traces: List[PageTraceStep] = []

        for step, page in enumerate(reference_string, start=1):
            if page in frames:
                hits += 1
                last_used[page] = step
                traces.append(PageTraceStep(step, page, list(frames), is_fault=False, evicted_page=None))
            else:
                faults += 1
                evicted = None
                if None in frames:
                    empty_idx = frames.index(None)
                    frames[empty_idx] = page
                else:
                    # Evict the page with the minimum last_used timestamp
                    evicted = min(frames, key=lambda p: last_used.get(p, -1))
                    evict_idx = frames.index(evicted)
                    frames[evict_idx] = page

                last_used[page] = step
                traces.append(PageTraceStep(step, page, list(frames), is_fault=True, evicted_page=evicted))

        total = len(reference_string)
        return PageReplacementResult(
            algorithm_name="LRU (Least Recently Used)",
            frame_capacity=frame_capacity,
            total_references=total,
            page_faults=faults,
            page_hits=hits,
            hit_ratio=hits / total if total > 0 else 0.0,
            fault_ratio=faults / total if total > 0 else 0.0,
            trace_steps=traces
        )

    @classmethod
    def simulate_optimal(cls, frame_capacity: int, reference_string: List[int]) -> PageReplacementResult:
        """Optimal (OPT / MIN) Page Replacement."""
        InputValidator.validate_page_replacement(frame_capacity, reference_string)
        frames: List[Optional[int]] = [None] * frame_capacity
        faults = 0
        hits = 0
        traces: List[PageTraceStep] = []
        n = len(reference_string)

        for step, page in enumerate(reference_string, start=1):
            if page in frames:
                hits += 1
                traces.append(PageTraceStep(step, page, list(frames), is_fault=False, evicted_page=None))
            else:
                faults += 1
                evicted = None
                if None in frames:
                    empty_idx = frames.index(None)
                    frames[empty_idx] = page
                else:
                    # Look ahead in the remaining reference string
                    future_refs = reference_string[step:]
                    candidate_page = None
                    max_distance = -1

                    for f in frames:
                        if f not in future_refs:
                            candidate_page = f
                            break
                        else:
                            dist = future_refs.index(f)
                            if dist > max_distance:
                                max_distance = dist
                                candidate_page = f

                    evicted = candidate_page
                    evict_idx = frames.index(evicted)
                    frames[evict_idx] = page

                traces.append(PageTraceStep(step, page, list(frames), is_fault=True, evicted_page=evicted))

        total = len(reference_string)
        return PageReplacementResult(
            algorithm_name="Optimal (OPT)",
            frame_capacity=frame_capacity,
            total_references=total,
            page_faults=faults,
            page_hits=hits,
            hit_ratio=hits / total if total > 0 else 0.0,
            fault_ratio=faults / total if total > 0 else 0.0,
            trace_steps=traces
        )

    @classmethod
    def run_all(cls, frame_capacity: int, reference_string: List[int]) -> Dict[str, PageReplacementResult]:
        """Run all page replacement algorithms on the identical reference stream."""
        return {
            "FIFO": cls.simulate_fifo(frame_capacity, reference_string),
            "LRU": cls.simulate_lru(frame_capacity, reference_string),
            "Optimal": cls.simulate_optimal(frame_capacity, reference_string)
        }
