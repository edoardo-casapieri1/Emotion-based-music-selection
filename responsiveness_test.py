import pytest
from operativa import operative_phase
import threading


def operative_phase_simulated():
    file_available_event = threading.Event()
    file_available_event.set()
    operative_phase(file_available_event)


def test_operative_phase(benchmark):
    benchmark.pedantic(operative_phase_simulated, iterations=1, rounds=10)

    assert True
