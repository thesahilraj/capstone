"""Strict schema, type, and boundary validator for all simulation parameters."""

from typing import Any, Dict, List
from .exceptions import ValidationError

class InputValidator:
    """Provides validation guards for all OS module configurations and datasets."""

    @staticmethod
    def validate_positive_integer(val: Any, field_name: str) -> int:
        """Ensure value is a positive integer (> 0)."""
        if not isinstance(val, int) or isinstance(val, bool) or val <= 0:
            raise ValidationError(f"Field '{field_name}' must be a positive integer (> 0). Received: {val}")
        return val

    @staticmethod
    def validate_non_negative_integer(val: Any, field_name: str) -> int:
        """Ensure value is a non-negative integer (>= 0)."""
        if not isinstance(val, int) or isinstance(val, bool) or val < 0:
            raise ValidationError(f"Field '{field_name}' must be a non-negative integer (>= 0). Received: {val}")
        return val

    @staticmethod
    def validate_cpu_workload(processes: List[Dict[str, Any]], quantum: int = 2) -> None:
        """Validate process scheduling configuration."""
        if not processes or not isinstance(processes, list):
            raise ValidationError("Process workload must be a non-empty list of process definitions.")

        InputValidator.validate_positive_integer(quantum, "round_robin_quantum")

        pids = set()
        for idx, p in enumerate(processes):
            if not isinstance(p, dict):
                raise ValidationError(f"Process at index {idx} must be a dictionary.")
            pid = str(p.get("pid", "")).strip()
            if not pid:
                raise ValidationError(f"Process at index {idx} missing valid 'pid'.")
            if pid in pids:
                raise ValidationError(f"Duplicate process ID '{pid}' detected.")
            pids.add(pid)

            InputValidator.validate_non_negative_integer(p.get("arrival_time"), f"Process {pid} arrival_time")
            InputValidator.validate_positive_integer(p.get("burst_time"), f"Process {pid} burst_time")
            if "priority" in p:
                InputValidator.validate_non_negative_integer(p.get("priority"), f"Process {pid} priority")

    @staticmethod
    def validate_memory_partitioning(total_size: int, partitions: List[int], requests: List[Dict[str, Any]]) -> None:
        """Validate contiguous memory partition parameters."""
        InputValidator.validate_positive_integer(total_size, "total_memory_size")
        if not partitions or not isinstance(partitions, list):
            raise ValidationError("Memory partitions must be a non-empty list of positive integers.")
        for p in partitions:
            InputValidator.validate_positive_integer(p, "partition_size")
        if sum(partitions) > total_size:
            raise ValidationError(f"Sum of partitions ({sum(partitions)}) exceeds total memory size ({total_size}).")

        if not isinstance(requests, list):
            raise ValidationError("Process memory requests must be a list.")
        for r in requests:
            if not isinstance(r, dict) or "size" not in r:
                raise ValidationError("Each memory request must contain a 'size' attribute.")
            InputValidator.validate_positive_integer(r["size"], f"Process {r.get('pid', 'unknown')} size")

    @staticmethod
    def validate_page_replacement(capacity: int, reference_string: List[int]) -> None:
        """Validate virtual memory page replacement configuration."""
        InputValidator.validate_positive_integer(capacity, "frame_capacity")
        if not reference_string or not isinstance(reference_string, list):
            raise ValidationError("Reference string must be a non-empty list of page numbers.")
        for page in reference_string:
            InputValidator.validate_non_negative_integer(page, "page_number")

    @staticmethod
    def validate_bankers_data(
        resource_types: List[str],
        available: List[int],
        processes: List[str],
        allocation: List[List[int]],
        maximum: List[List[int]]
    ) -> None:
        """Validate Banker's algorithm matrix dimensions and constraints."""
        num_res = len(resource_types)
        num_proc = len(processes)

        if num_res == 0 or num_proc == 0:
            raise ValidationError("Resource types and processes must both be non-empty.")

        if len(available) != num_res:
            raise ValidationError(f"Available vector length ({len(available)}) does not match resource count ({num_res}).")
        for a in available:
            InputValidator.validate_non_negative_integer(a, "available_resource_count")

        if len(allocation) != num_proc or len(maximum) != num_proc:
            raise ValidationError("Allocation and Maximum matrices row count must match process count.")

        for i in range(num_proc):
            if len(allocation[i]) != num_res:
                raise ValidationError(f"Allocation row {i} length != resource count {num_res}.")
            if len(maximum[i]) != num_res:
                raise ValidationError(f"Maximum row {i} length != resource count {num_res}.")
            for j in range(num_res):
                alloc_val = InputValidator.validate_non_negative_integer(allocation[i][j], f"Allocation[{i}][{j}]")
                max_val = InputValidator.validate_non_negative_integer(maximum[i][j], f"Maximum[{i}][{j}]")
                if alloc_val > max_val:
                    raise ValidationError(
                        f"Allocation exceeds Maximum demand for process {processes[i]} on resource {resource_types[j]} "
                        f"({alloc_val} > {max_val})."
                    )

    @staticmethod
    def validate_disk_workload(initial_head: int, cylinders: int, requests: List[int]) -> None:
        """Validate disk scheduling head position and track requests."""
        InputValidator.validate_positive_integer(cylinders, "disk_cylinders")
        InputValidator.validate_non_negative_integer(initial_head, "initial_head_position")
        if initial_head >= cylinders:
            raise ValidationError(f"Initial head position {initial_head} is out of bounds for {cylinders} cylinders (0 to {cylinders-1}).")

        if not requests or not isinstance(requests, list):
            raise ValidationError("Disk request queue must be a non-empty list of cylinder numbers.")

        for req in requests:
            InputValidator.validate_non_negative_integer(req, "disk_cylinder_request")
            if req >= cylinders:
                raise ValidationError(f"Requested cylinder {req} exceeds disk boundary (max {cylinders-1}).")
