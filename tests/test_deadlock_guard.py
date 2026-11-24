"""Unit and boundary tests for Deadlock Avoidance (Banker's Algorithm)."""

import pytest
from src.modules.deadlock_guard import BankersAlgorithm
from src.utils.exceptions import ValidationError

@pytest.fixture
def standard_bankers():
    return BankersAlgorithm(
        resource_types=["A", "B", "C"],
        available=[3, 3, 2],
        processes=["P0", "P1", "P2", "P3", "P4"],
        allocation=[
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 2],
            [2, 1, 1],
            [0, 0, 2]
        ],
        maximum=[
            [7, 5, 3],
            [3, 2, 2],
            [9, 0, 2],
            [2, 2, 2],
            [4, 3, 3]
        ]
    )

def test_bankers_safety_sequence(standard_bankers):
    safety = standard_bankers.check_safety()
    assert safety.is_safe is True
    assert len(safety.safe_sequence) == 5
    # P1 can finish first in the standard textbook dataset
    assert safety.safe_sequence[0] == "P1"

def test_bankers_valid_request(standard_bankers):
    req_res = standard_bankers.request_resources("P1", [1, 0, 2])
    assert req_res.granted is True
    assert req_res.is_safe is True
    assert standard_bankers.available == [2, 3, 0]

def test_bankers_request_exceeds_need(standard_bankers):
    # P1 max is [3, 2, 2], alloc is [2, 0, 0], need is [1, 2, 2]
    # Requesting [2, 0, 0] exceeds its Need vector in resource A
    req_res = standard_bankers.request_resources("P1", [2, 0, 0])
    assert req_res.granted is False
    assert "exceeds its declared maximum need" in req_res.message

def test_bankers_request_exceeds_available(standard_bankers):
    # Available is [3, 3, 2], requesting 5 units of resource A
    # First set need to allow it: P0 need is [7, 4, 3]
    req_res = standard_bankers.request_resources("P0", [5, 0, 0])
    assert req_res.granted is False
    assert "must wait" in req_res.message

def test_bankers_unsafe_detection():
    # Setup inherently unsafe state with insufficient resources
    banker = BankersAlgorithm(
        resource_types=["R1"],
        available=[0],
        processes=["P1", "P2"],
        allocation=[[1], [1]],
        maximum=[[2], [2]]
    )
    safety = banker.check_safety()
    assert safety.is_safe is False
    assert len(safety.blocked_processes) == 2
