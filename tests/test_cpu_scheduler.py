"""Unit and boundary tests for CPU Scheduler."""

import pytest
from src.modules.cpu_scheduler import CPUScheduler, Process
from src.utils.exceptions import ValidationError

def test_fcfs_basic():
    procs = [
        Process(pid="P1", arrival_time=0, burst_time=4),
        Process(pid="P2", arrival_time=1, burst_time=3),
        Process(pid="P3", arrival_time=2, burst_time=1),
    ]
    res = CPUScheduler.schedule_fcfs(procs)
    assert res.average_waiting_time == pytest.approx((0 + 3 + 5) / 3, 0.01)
    assert res.total_time == 8
    assert len(res.gantt_chart) == 3

def test_sjf_vs_srtf():
    # In this dataset, SJF and SRTF diverge because P2 arrives at t=1 with shorter burst
    procs = [
        Process(pid="P1", arrival_time=0, burst_time=8),
        Process(pid="P2", arrival_time=1, burst_time=4),
        Process(pid="P3", arrival_time=2, burst_time=2),
    ]
    sjf_res = CPUScheduler.schedule_sjf_non_preemptive(procs)
    srtf_res = CPUScheduler.schedule_srtf(procs)

    # SRTF preempts P1, achieving lower average waiting time than non-preemptive SJF
    assert srtf_res.average_waiting_time <= sjf_res.average_waiting_time

def test_priority_scheduling():
    procs = [
        Process(pid="P1", arrival_time=0, burst_time=4, priority=3),
        Process(pid="P2", arrival_time=0, burst_time=2, priority=1),
        Process(pid="P3", arrival_time=0, burst_time=1, priority=2),
    ]
    res = CPUScheduler.schedule_priority_non_preemptive(procs)
    order = [s.pid for s in res.gantt_chart]
    assert order == ["P2", "P3", "P1"]

def test_round_robin():
    procs = [
        Process(pid="P1", arrival_time=0, burst_time=5),
        Process(pid="P2", arrival_time=0, burst_time=3),
    ]
    res = CPUScheduler.schedule_round_robin(procs, quantum=2)
    # Timeline: P1(2) -> P2(2) -> P1(2) -> P2(1) -> P1(1)
    assert res.total_time == 8
    p1 = next(p for p in res.processes if p.pid == "P1")
    assert p1.completion_time == 8

def test_cpu_validation_zero_burst():
    from src.utils.validator import InputValidator
    with pytest.raises(ValidationError):
        InputValidator.validate_cpu_workload([{"pid": "P1", "arrival_time": 0, "burst_time": 0}])

def test_cpu_validation_negative_arrival():
    from src.utils.validator import InputValidator
    with pytest.raises(ValidationError):
        InputValidator.validate_cpu_workload([{"pid": "P1", "arrival_time": -1, "burst_time": 5}])
