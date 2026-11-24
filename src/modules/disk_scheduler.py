"""Storage / Disk Scheduling Subsystem.
Simulates secondary storage cylinder head arbitration algorithms:
FCFS, SSTF, SCAN, C-SCAN, LOOK, and C-LOOK with total seek calculation and trajectory traces.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
import copy
from ..utils.exceptions import ValidationError
from ..utils.validator import InputValidator

@dataclass
class DiskScheduleResult:
    algorithm_name: str
    initial_head: int
    direction: str  # 'RIGHT' (higher cylinders) or 'LEFT' (lower cylinders)
    disk_cylinders: int
    request_queue: List[int]
    seek_sequence: List[int]
    total_head_movement: int
    average_seek_distance: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "algorithm_name": self.algorithm_name,
            "initial_head": self.initial_head,
            "direction": self.direction,
            "disk_cylinders": self.disk_cylinders,
            "request_queue": list(self.request_queue),
            "seek_sequence": list(self.seek_sequence),
            "total_head_movement": self.total_head_movement,
            "average_seek_distance": round(self.average_seek_distance, 2)
        }


class DiskScheduler:
    """Core Disk Head Scheduling Simulation Engine."""

    @staticmethod
    def _compute_total_movement(sequence: List[int]) -> int:
        return sum(abs(sequence[i] - sequence[i - 1]) for i in range(1, len(sequence)))

    @classmethod
    def schedule_fcfs(cls, initial_head: int, cylinders: int, requests: List[int]) -> DiskScheduleResult:
        """First-Come, First-Served Disk Scheduling."""
        InputValidator.validate_disk_workload(initial_head, cylinders, requests)
        seq = [initial_head] + list(requests)
        total_movement = cls._compute_total_movement(seq)
        avg = total_movement / len(requests) if requests else 0.0

        return DiskScheduleResult(
            algorithm_name="FCFS (First-Come, First-Served)",
            initial_head=initial_head,
            direction="N/A",
            disk_cylinders=cylinders,
            request_queue=list(requests),
            seek_sequence=seq,
            total_head_movement=total_movement,
            average_seek_distance=avg
        )

    @classmethod
    def schedule_sstf(cls, initial_head: int, cylinders: int, requests: List[int]) -> DiskScheduleResult:
        """Shortest Seek Time First (SSTF)."""
        InputValidator.validate_disk_workload(initial_head, cylinders, requests)
        pending = list(requests)
        current = initial_head
        seq = [current]

        while pending:
            # Pick pending cylinder with minimum distance to current
            closest = min(pending, key=lambda c: (abs(c - current), c))
            seq.append(closest)
            current = closest
            pending.remove(closest)

        total_movement = cls._compute_total_movement(seq)
        avg = total_movement / len(requests) if requests else 0.0

        return DiskScheduleResult(
            algorithm_name="SSTF (Shortest Seek Time First)",
            initial_head=initial_head,
            direction="Dynamic",
            disk_cylinders=cylinders,
            request_queue=list(requests),
            seek_sequence=seq,
            total_head_movement=total_movement,
            average_seek_distance=avg
        )

    @classmethod
    def schedule_scan(cls, initial_head: int, cylinders: int, requests: List[int], direction: str = "RIGHT") -> DiskScheduleResult:
        """SCAN (Elevator Algorithm). Moves to disk boundary before reversing."""
        InputValidator.validate_disk_workload(initial_head, cylinders, requests)
        direction = direction.upper()
        if direction not in ["RIGHT", "LEFT", "UP", "DOWN"]:
            direction = "RIGHT"
        is_up = direction in ["RIGHT", "UP"]

        left = sorted([r for r in requests if r < initial_head])
        right = sorted([r for r in requests if r >= initial_head])

        seq = [initial_head]

        if is_up:
            seq.extend(right)
            # Scan hits maximum cylinder if there are cylinders on the left
            if left:
                seq.append(cylinders - 1)
                seq.extend(reversed(left))
        else:
            seq.extend(reversed(left))
            if right:
                seq.append(0)
                seq.extend(right)

        total_movement = cls._compute_total_movement(seq)
        avg = total_movement / len(requests) if requests else 0.0

        return DiskScheduleResult(
            algorithm_name="SCAN (Elevator)",
            initial_head=initial_head,
            direction="RIGHT" if is_up else "LEFT",
            disk_cylinders=cylinders,
            request_queue=list(requests),
            seek_sequence=seq,
            total_head_movement=total_movement,
            average_seek_distance=avg
        )

    @classmethod
    def schedule_cscan(cls, initial_head: int, cylinders: int, requests: List[int], direction: str = "RIGHT") -> DiskScheduleResult:
        """Circular SCAN (C-SCAN). Sweeps in one direction, jumps to opposite boundary."""
        InputValidator.validate_disk_workload(initial_head, cylinders, requests)
        direction = direction.upper()
        is_up = direction in ["RIGHT", "UP"]

        left = sorted([r for r in requests if r < initial_head])
        right = sorted([r for r in requests if r >= initial_head])

        seq = [initial_head]

        if is_up:
            seq.extend(right)
            if left:
                seq.append(cylinders - 1)
                seq.append(0)
                seq.extend(left)
        else:
            seq.extend(reversed(left))
            if right:
                seq.append(0)
                seq.append(cylinders - 1)
                seq.extend(reversed(right))

        total_movement = cls._compute_total_movement(seq)
        avg = total_movement / len(requests) if requests else 0.0

        return DiskScheduleResult(
            algorithm_name="C-SCAN (Circular SCAN)",
            initial_head=initial_head,
            direction="RIGHT" if is_up else "LEFT",
            disk_cylinders=cylinders,
            request_queue=list(requests),
            seek_sequence=seq,
            total_head_movement=total_movement,
            average_seek_distance=avg
        )

    @classmethod
    def schedule_look(cls, initial_head: int, cylinders: int, requests: List[int], direction: str = "RIGHT") -> DiskScheduleResult:
        """LOOK Algorithm. Reverses direction at the furthest request without traveling to disk boundary."""
        InputValidator.validate_disk_workload(initial_head, cylinders, requests)
        direction = direction.upper()
        is_up = direction in ["RIGHT", "UP"]

        left = sorted([r for r in requests if r < initial_head])
        right = sorted([r for r in requests if r >= initial_head])

        seq = [initial_head]

        if is_up:
            seq.extend(right)
            seq.extend(reversed(left))
        else:
            seq.extend(reversed(left))
            seq.extend(right)

        total_movement = cls._compute_total_movement(seq)
        avg = total_movement / len(requests) if requests else 0.0

        return DiskScheduleResult(
            algorithm_name="LOOK",
            initial_head=initial_head,
            direction="RIGHT" if is_up else "LEFT",
            disk_cylinders=cylinders,
            request_queue=list(requests),
            seek_sequence=seq,
            total_head_movement=total_movement,
            average_seek_distance=avg
        )

    @classmethod
    def schedule_clook(cls, initial_head: int, cylinders: int, requests: List[int], direction: str = "RIGHT") -> DiskScheduleResult:
        """Circular LOOK (C-LOOK). Jumps to lowest requested track without servicing in return sweep."""
        InputValidator.validate_disk_workload(initial_head, cylinders, requests)
        direction = direction.upper()
        is_up = direction in ["RIGHT", "UP"]

        left = sorted([r for r in requests if r < initial_head])
        right = sorted([r for r in requests if r >= initial_head])

        seq = [initial_head]

        if is_up:
            seq.extend(right)
            seq.extend(left)
        else:
            seq.extend(reversed(left))
            seq.extend(reversed(right))

        total_movement = cls._compute_total_movement(seq)
        avg = total_movement / len(requests) if requests else 0.0

        return DiskScheduleResult(
            algorithm_name="C-LOOK (Circular LOOK)",
            initial_head=initial_head,
            direction="RIGHT" if is_up else "LEFT",
            disk_cylinders=cylinders,
            request_queue=list(requests),
            seek_sequence=seq,
            total_head_movement=total_movement,
            average_seek_distance=avg
        )

    @classmethod
    def run_all(
        cls,
        initial_head: int,
        cylinders: int,
        requests: List[int],
        direction: str = "RIGHT"
    ) -> Dict[str, DiskScheduleResult]:
        """Run all disk scheduling algorithms on the identical queue."""
        return {
            "FCFS": cls.schedule_fcfs(initial_head, cylinders, requests),
            "SSTF": cls.schedule_sstf(initial_head, cylinders, requests),
            "SCAN": cls.schedule_scan(initial_head, cylinders, requests, direction),
            "C-SCAN": cls.schedule_cscan(initial_head, cylinders, requests, direction),
            "LOOK": cls.schedule_look(initial_head, cylinders, requests, direction),
            "C-LOOK": cls.schedule_clook(initial_head, cylinders, requests, direction)
        }
