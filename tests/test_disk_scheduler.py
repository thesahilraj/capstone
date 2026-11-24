"""Unit and boundary tests for Disk Scheduling Subsystem."""

import pytest
from src.modules.disk_scheduler import DiskScheduler
from src.utils.exceptions import ValidationError

@pytest.fixture
def textbook_workload():
    return {
        "head": 53,
        "cylinders": 200,
        "requests": [98, 183, 37, 122, 14, 124, 65, 67]
    }

def test_disk_fcfs(textbook_workload):
    res = DiskScheduler.schedule_fcfs(
        textbook_workload["head"],
        textbook_workload["cylinders"],
        textbook_workload["requests"]
    )
    assert res.total_head_movement == 640

def test_disk_sstf(textbook_workload):
    res = DiskScheduler.schedule_sstf(
        textbook_workload["head"],
        textbook_workload["cylinders"],
        textbook_workload["requests"]
    )
    assert res.total_head_movement == 236

def test_disk_scan(textbook_workload):
    res = DiskScheduler.schedule_scan(
        textbook_workload["head"],
        textbook_workload["cylinders"],
        textbook_workload["requests"],
        direction="RIGHT"
    )
    # Head moves 53 -> 199, then down to 14: (199-53) + (199-14) = 146 + 185 = 331
    assert res.total_head_movement == 331

def test_disk_look(textbook_workload):
    res = DiskScheduler.schedule_look(
        textbook_workload["head"],
        textbook_workload["cylinders"],
        textbook_workload["requests"],
        direction="RIGHT"
    )
    # Head moves 53 -> 183 (max request), then down to 14: (183-53) + (183-14) = 130 + 169 = 299
    assert res.total_head_movement == 299

def test_disk_invalid_head():
    with pytest.raises(ValidationError):
        DiskScheduler.schedule_fcfs(200, 200, [50, 100])

def test_disk_out_of_bounds_request():
    with pytest.raises(ValidationError):
        DiskScheduler.schedule_fcfs(50, 200, [50, 250])
