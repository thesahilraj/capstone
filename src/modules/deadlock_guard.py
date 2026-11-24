"""Deadlock Management Subsystem.
Implements Dijkstra's Banker's Algorithm for deadlock avoidance:
- System Safety Algorithm (Safe State verification & safe sequence derivation).
- Resource-Request Algorithm (Speculative allocation, constraint checks & rollback).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
import copy
from ..utils.exceptions import DeadlockError, ValidationError
from ..utils.validator import InputValidator

@dataclass
class SafetyResult:
    is_safe: bool
    safe_sequence: List[str]
    work_history: List[Dict[str, Any]]
    blocked_processes: List[str]
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_safe": self.is_safe,
            "safe_sequence": self.safe_sequence,
            "work_history": self.work_history,
            "blocked_processes": self.blocked_processes,
            "explanation": self.explanation
        }

@dataclass
class RequestEvaluationResult:
    granted: bool
    process_id: str
    request_vector: List[int]
    is_safe: bool
    safe_sequence: List[str]
    message: str
    available_after: List[int]
    need_after: List[List[int]]
    allocation_after: List[List[int]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "granted": self.granted,
            "process_id": self.process_id,
            "request_vector": self.request_vector,
            "is_safe": self.is_safe,
            "safe_sequence": self.safe_sequence,
            "message": self.message,
            "available_after": self.available_after,
            "need_after": self.need_after,
            "allocation_after": self.allocation_after
        }


class BankersAlgorithm:
    """Encapsulates Dijkstra's Banker's Algorithm for multi-instance resource systems."""

    def __init__(
        self,
        resource_types: List[str],
        available: List[int],
        processes: List[str],
        allocation: List[List[int]],
        maximum: List[List[int]]
    ):
        InputValidator.validate_bankers_data(resource_types, available, processes, allocation, maximum)
        self.resource_types = list(resource_types)
        self.available = list(available)
        self.processes = list(processes)
        self.allocation = [list(row) for row in allocation]
        self.maximum = [list(row) for row in maximum]

        # Compute Need matrix: Need[i][j] = Max[i][j] - Allocation[i][j]
        self.need = [
            [self.maximum[i][j] - self.allocation[i][j] for j in range(len(self.resource_types))]
            for i in range(len(self.processes))
        ]

    def get_state_summary(self) -> Dict[str, Any]:
        """Return a structured summary snapshot of current system state."""
        return {
            "resources": self.resource_types,
            "available": list(self.available),
            "processes": list(self.processes),
            "allocation": [list(r) for r in self.allocation],
            "maximum": [list(r) for r in self.maximum],
            "need": [list(r) for r in self.need]
        }

    def check_safety(
        self,
        custom_available: Optional[List[int]] = None,
        custom_allocation: Optional[List[List[int]]] = None,
        custom_need: Optional[List[List[int]]] = None
    ) -> SafetyResult:
        """Execute Dijkstra's Safety Algorithm."""
        avail = list(custom_available if custom_available is not None else self.available)
        alloc = [list(r) for r in (custom_allocation if custom_allocation is not None else self.allocation)]
        need = [list(r) for r in (custom_need if custom_need is not None else self.need)]

        num_proc = len(self.processes)
        num_res = len(self.resource_types)

        work = list(avail)
        finish = [False] * num_proc
        safe_sequence: List[str] = []
        work_history: List[Dict[str, Any]] = []

        step = 1
        while len(safe_sequence) < num_proc:
            found_candidate = False
            for i in range(num_proc):
                if not finish[i]:
                    # Check if Need[i] <= Work
                    can_allocate = all(need[i][j] <= work[j] for j in range(num_res))
                    if can_allocate:
                        prev_work = list(work)
                        # Process terminates, releases its allocated resources to Work
                        for j in range(num_res):
                            work[j] += alloc[i][j]
                        finish[i] = True
                        safe_sequence.append(self.processes[i])
                        work_history.append({
                            "step": step,
                            "process": self.processes[i],
                            "work_before": prev_work,
                            "need": list(need[i]),
                            "allocation": list(alloc[i]),
                            "work_after": list(work)
                        })
                        step += 1
                        found_candidate = True
                        break  # restart search

            if not found_candidate:
                # System is not in a safe state (Deadlock potential)
                break

        is_safe = all(finish)
        blocked = [self.processes[i] for i in range(num_proc) if not finish[i]]

        if is_safe:
            explanation = f"System is in a SAFE STATE. Complete Safe Execution Sequence: <{' -> '.join(safe_sequence)}>."
        else:
            explanation = (
                f"System is in an UNSAFE STATE! Circular wait / starvation risk detected. "
                f"Blocked processes: {', '.join(blocked)}."
            )

        return SafetyResult(
            is_safe=is_safe,
            safe_sequence=safe_sequence,
            work_history=work_history,
            blocked_processes=blocked,
            explanation=explanation
        )

    def request_resources(self, process_id: str, request_vector: List[int]) -> RequestEvaluationResult:
        """Execute Banker's Resource-Request Algorithm."""
        if process_id not in self.processes:
            raise ValidationError(f"Process '{process_id}' not found in system processes.")

        p_idx = self.processes.index(process_id)
        num_res = len(self.resource_types)

        if len(request_vector) != num_res:
            raise ValidationError(f"Request vector length ({len(request_vector)}) does not match resource count ({num_res}).")

        for r in request_vector:
            InputValidator.validate_non_negative_integer(r, "request_quantity")

        # Step 1: Check if Request <= Need
        for j in range(num_res):
            if request_vector[j] > self.need[p_idx][j]:
                msg = (
                    f"Request DENIED: Process '{process_id}' requested {request_vector[j]} units of "
                    f"resource '{self.resource_types[j]}', which exceeds its declared maximum need "
                    f"({self.need[p_idx][j]})."
                )
                return RequestEvaluationResult(
                    granted=False,
                    process_id=process_id,
                    request_vector=request_vector,
                    is_safe=False,
                    safe_sequence=[],
                    message=msg,
                    available_after=list(self.available),
                    need_after=[list(r) for r in self.need],
                    allocation_after=[list(r) for r in self.allocation]
                )

        # Step 2: Check if Request <= Available
        for j in range(num_res):
            if request_vector[j] > self.available[j]:
                msg = (
                    f"Request SUSPENDED: Process '{process_id}' must wait. Requested {request_vector[j]} units of "
                    f"resource '{self.resource_types[j]}', but only {self.available[j]} units are currently available."
                )
                return RequestEvaluationResult(
                    granted=False,
                    process_id=process_id,
                    request_vector=request_vector,
                    is_safe=False,
                    safe_sequence=[],
                    message=msg,
                    available_after=list(self.available),
                    need_after=[list(r) for r in self.need],
                    allocation_after=[list(r) for r in self.allocation]
                )

        # Step 3: Speculative trial allocation
        trial_available = list(self.available)
        trial_allocation = [list(r) for r in self.allocation]
        trial_need = [list(r) for r in self.need]

        for j in range(num_res):
            trial_available[j] -= request_vector[j]
            trial_allocation[p_idx][j] += request_vector[j]
            trial_need[p_idx][j] -= request_vector[j]

        # Step 4: Evaluate safety on speculative state
        safety_eval = self.check_safety(
            custom_available=trial_available,
            custom_allocation=trial_allocation,
            custom_need=trial_need
        )

        if safety_eval.is_safe:
            # Grant permanently
            self.available = trial_available
            self.allocation = trial_allocation
            self.need = trial_need
            msg = (
                f"Request GRANTED for '{process_id}'. System remains in a SAFE state. "
                f"Resulting Safe Sequence: <{' -> '.join(safety_eval.safe_sequence)}>."
            )
            return RequestEvaluationResult(
                granted=True,
                process_id=process_id,
                request_vector=request_vector,
                is_safe=True,
                safe_sequence=safety_eval.safe_sequence,
                message=msg,
                available_after=list(self.available),
                need_after=[list(r) for r in self.need],
                allocation_after=[list(r) for r in self.allocation]
            )
        else:
            # Rollback speculative allocation
            msg = (
                f"Request DENIED for '{process_id}': Granting request would lead to an UNSAFE STATE (deadlock hazard). "
                f"Rolled back speculative allocation. Process must wait."
            )
            return RequestEvaluationResult(
                granted=False,
                process_id=process_id,
                request_vector=request_vector,
                is_safe=False,
                safe_sequence=[],
                message=msg,
                available_after=list(self.available),
                need_after=[list(r) for r in self.need],
                allocation_after=[list(r) for r in self.allocation]
            )
