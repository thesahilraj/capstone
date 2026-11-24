"""Unit and boundary tests for Memory Subsystem."""

import pytest
from src.modules.memory_manager import (
    ContiguousMemoryManager,
    PageReplacementSimulator
)
from src.utils.exceptions import ValidationError

def test_contiguous_fits():
    partitions = [100, 500, 200, 300, 600]
    requests = [
        {"pid": "J1", "size": 212},
        {"pid": "J2", "size": 417},
        {"pid": "J3", "size": 112},
        {"pid": "J4", "size": 426}
    ]
    mgr = ContiguousMemoryManager(partitions)

    ff = mgr.simulate_allocation("FIRST_FIT", requests)
    assert ff.allocated_processes == 3  # J4 fails in textbook example
    assert ff.failed_processes == 1

    bf = mgr.simulate_allocation("BEST_FIT", requests)
    assert bf.allocated_processes == 4  # Best fit succeeds for all 4
    assert bf.failed_processes == 0

def test_page_replacement_fifo():
    ref_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
    fifo_res = PageReplacementSimulator.simulate_fifo(3, ref_string)
    assert fifo_res.page_faults == 15
    assert fifo_res.page_hits == 5

def test_page_replacement_lru():
    ref_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
    lru_res = PageReplacementSimulator.simulate_lru(3, ref_string)
    assert lru_res.page_faults == 12
    assert lru_res.page_hits == 8

def test_page_replacement_optimal():
    ref_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
    opt_res = PageReplacementSimulator.simulate_optimal(3, ref_string)
    assert opt_res.page_faults == 9
    assert opt_res.page_hits == 11
    # Optimal must produce fewer or equal faults compared to LRU and FIFO
    assert opt_res.page_faults <= lru_res_faults(3, ref_string)

def lru_res_faults(capacity, refs):
    return PageReplacementSimulator.simulate_lru(capacity, refs).page_faults

def test_paging_invalid_capacity():
    with pytest.raises(ValidationError):
        PageReplacementSimulator.simulate_fifo(0, [1, 2, 3])
