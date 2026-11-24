"""Integration tests verifying full simulation engine execution and artifact generation."""

import os
import pytest
from src.engine import SimulationEngine

def test_simulation_engine_full_suite():
    engine = SimulationEngine()
    res = engine.run_full_suite("data/sample_workload.json")

    assert "cpu" in res
    assert "memory" in res
    assert "deadlock" in res
    assert "disk" in res
    assert "pdf_report" in res

    # Verify figures generated
    base_dir = engine.base_dir
    assert os.path.exists(os.path.join(base_dir, "output", "figures", "cpu_gantt_chart.png"))
    assert os.path.exists(os.path.join(base_dir, "output", "figures", "cpu_comparison.png"))
    assert os.path.exists(os.path.join(base_dir, "output", "figures", "disk_trajectories.png"))
    assert os.path.exists(os.path.join(base_dir, "output", "figures", "page_replacement_comparison.png"))

    # Verify traces generated
    assert os.path.exists(os.path.join(base_dir, "output", "traces", "cpu_scheduling_trace.json"))
    assert os.path.exists(os.path.join(base_dir, "output", "traces", "memory_trace.json"))
    assert os.path.exists(os.path.join(base_dir, "output", "traces", "deadlock_trace.json"))
    assert os.path.exists(os.path.join(base_dir, "output", "traces", "disk_scheduling_trace.json"))

    # Verify PDF report generated and has non-zero size
    pdf_path = res["pdf_report"]
    assert os.path.exists(pdf_path)
    file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    assert file_size_mb > 0.01
    assert file_size_mb <= 25.0  # Must be well under the 25MB submission limit
