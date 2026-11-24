"""Custom structured exception hierarchy for the OS Simulation Suite."""

class SimulationError(Exception):
    """Base exception class for all simulation errors."""
    pass

class ValidationError(SimulationError):
    """Raised when user input or dataset fails schema or domain validation."""
    pass

class AllocationError(SimulationError):
    """Raised when memory allocation cannot be satisfied."""
    pass

class DeadlockError(SimulationError):
    """Raised when an unsafe state or circular wait condition is detected."""
    pass

class InvalidStateError(SimulationError):
    """Raised when an internal simulator state becomes inconsistent."""
    pass
