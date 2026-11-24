"""Unit tests for MetricsFormatter and tabular rendering."""

import pytest
from src.analytics.metrics import MetricsFormatter
from src.modules.cpu_scheduler import CPUScheduler, Process
from src.modules.memory_manager import PageReplacementSimulator, ContiguousMemoryManager
from src.modules.disk_scheduler import DiskScheduler

def test_metrics_formatter_cpu():
    procs = [
        Process("P1", 0, 4, 1),
        Process("P2", 1, 2, 2)
    ]
    results = CPUScheduler.run_all(procs, quantum=2)
    comp_table = MetricsFormatter.format_cpu_comparison(results)
    assert "Algorithm" in comp_table
    assert "FCFS" in comp_table
    assert "Round Robin" in comp_table

    proc_table = MetricsFormatter.format_cpu_process_table(results["FCFS"])
    assert "PID" in proc_table
    assert "P1" in proc_table
    assert "P2" in proc_table

def test_metrics_formatter_page_replacement():
    res = PageReplacementSimulator.run_all(3, [7, 0, 1, 2, 0])
    table = MetricsFormatter.format_page_replacement_comparison(res)
    assert "FIFO" in table
    assert "LRU" in table
    assert "Optimal" in table
    assert "Page Faults" in table

def test_metrics_formatter_disk():
    res = DiskScheduler.run_all(50, 200, [90, 120, 30])
    table = MetricsFormatter.format_disk_comparison(res)
    assert "FCFS" in table
    assert "SSTF" in table
    assert "Total Seek Movement" in table

def test_metrics_formatter_contiguous_memory():
    mgr = ContiguousMemoryManager([100, 200])
    res = mgr.simulate_allocation("FIRST_FIT", [{"pid": "J1", "size": 50}])
    table = MetricsFormatter.format_memory_contiguous_table(res)
    assert "Partition #" in table
    assert "ALLOCATED" in table
