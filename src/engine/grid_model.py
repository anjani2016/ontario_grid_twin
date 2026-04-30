from typing import Dict, List
import numpy as np

class GridNode:
    """
    A professional-grade class to represent a grid substation.
    Encapsulates both data and simulation logic.
    """
    def __init__(self, name: str, capacity_mw: float, base_load_mw: float, voltage_kv: int):
        self.name = name
        self.capacity_mw = capacity_mw
        self.base_load_mw = base_load_mw
        self.voltage_kv = voltage_kv

    def calculate_reliability(self, new_load_mw: float, iterations: int = 1000) -> float:
        """
        Performs a Monte Carlo simulation to determine the probability 
        that the node stays within capacity limits.
        """
        # Simulate ambient grid fluctuation (standard deviation of 10%)
        fluctuations = np.random.normal(1.0, 0.10, iterations)
        simulated_loads = (self.base_load_mw * fluctuations) + new_load_mw
        
        successes = np.sum(simulated_loads <= self.capacity_mw)
        return (successes / iterations) * 100

    def estimate_losses(self, load_mw: float, resistance_ohms: float = 0.05) -> float:
        """
        Calculates I^2R losses based on simulated load and voltage.
        """
        # Current (Amps) = Power (Watts) / (Voltage (Volts))
        current = (load_mw * 1e6) / (self.voltage_kv * 1e3)
        losses_mw = (current**2 * resistance_ohms) / 1e6
        return losses_mw

# Example Usage:
if __name__ == "__main__":
    # Initializing Armitage TS with data from our previous steps
    armitage = GridNode(name="Armitage TS", capacity_mw=1250, base_load_mw=1050, voltage_kv=230)
    
    reliability = armitage.calculate_reliability(new_load_mw=100)
    print(f"Reliability for 100MW load: {reliability:.2f}%")