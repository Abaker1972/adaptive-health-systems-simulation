"""
Prototype simulation for:

Adaptive Health Systems Planning under Uncertainty:
A Multi-Level Systems Analytics Framework with Adaptive Policy Intelligence

This code is a conceptual implementation for appendix and transparency purposes.
It is designed to illustrate the simulation logic, not to claim empirical calibration.

Author: Dr. Ahmed Abdallah Abaker
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import random
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt


EPSILON = 1e-6


@dataclass
class Agent:
    """Represents an individual agent in the health system."""
    health_status: float
    decision_state: float
    resource_demand: float = 0.0


@dataclass
class ModelConfig:
    """Global configuration for the simulation."""
    n_agents: int = 500
    horizon: int = 100

    # Demand parameters
    alpha: float = 0.6
    beta: float = 0.4

    # Capacity dynamics
    gamma: float = 0.03
    delta: float = 0.02

    # Adaptive policy learning
    learning_rate: float = 0.05

    # Initial system conditions
    initial_resources: float = 1000.0
    initial_capacity: float = 800.0
    digital_transformation: float = 0.0

    # Scenario controls
    demand_shock_start: int = 30
    demand_shock_end: int = 45
    demand_shock_factor: float = 1.5

    resource_disruption_start: int = 50
    resource_disruption_end: int = 70
    resource_loss_factor: float = 0.25


class HealthSystemSimulation:
    """
    Integrated ABM + network influence + system dynamics + adaptive policy layer.
    """

    def __init__(self, config: ModelConfig, seed: int = 42) -> None:
        self.config = config
        self.random = random.Random(seed)

        self.agents: List[Agent] = self._initialize_agents()
        self.network: List[List[float]] = self._initialize_network()

        self.resources = config.initial_resources
        self.capacity = config.initial_capacity
        self.policy_strength = 0.2

        self.history: Dict[str, List[float]] = {
            "demand": [],
            "resources": [],
            "capacity": [],
            "system_pressure": [],
            "service_continuity": [],
            "resource_utilization_efficiency": [],
            "policy_strength": [],
        }

    def _initialize_agents(self) -> List[Agent]:
        """Create heterogeneous agents with random initial states."""
        agents: List[Agent] = []
        for _ in range(self.config.n_agents):
            health_status = self.random.uniform(0.3, 1.0)
            decision_state = self.random.uniform(0.2, 0.8)
            agents.append(
                Agent(
                    health_status=health_status,
                    decision_state=decision_state,
                )
            )
        return agents

    def _initialize_network(self) -> List[List[float]]:
        """
        Create a simple weighted adjacency matrix.
        This is a conceptual approximation of a healthcare interaction network.
        """
        n = self.config.n_agents
        network = [[0.0 for _ in range(n)] for _ in range(n)]

        # Sparse random connectivity
        for i in range(n):
            for j in range(i + 1, n):
                if self.random.random() < 0.01:
                    weight = self.random.uniform(0.1, 1.0)
                    network[i][j] = weight
                    network[j][i] = weight

        return network

    def _network_influence(self, idx: int) -> float:
        """Compute weighted influence from neighboring agents."""
        total = 0.0
        row = self.network[idx]
        for j, weight in enumerate(row):
            if weight > 0:
                total += weight * self.agents[j].decision_state
        return total

    def _demand_shock_multiplier(self, t: int) -> float:
        """Scenario shock to aggregate demand."""
        if self.config.demand_shock_start <= t <= self.config.demand_shock_end:
            return self.config.demand_shock_factor
        return 1.0

    def _resource_loss(self, t: int) -> float:
        """Scenario shock to resources."""
        if self.config.resource_disruption_start <= t <= self.config.resource_disruption_end:
            return self.resources * self.config.resource_loss_factor * 0.02
        return 0.0

    def _update_agents(self, system_pressure: float) -> None:
        """Update agent decisions and resource demand."""
        for i, agent in enumerate(self.agents):
            influence = self._network_influence(i)

            new_decision = (
                0.55 * agent.decision_state
                + 0.0005 * influence
                + 0.10 * system_pressure
                - 0.12 * self.policy_strength
            )

            # Clamp to [0, 1]
            agent.decision_state = max(0.0, min(1.0, new_decision))

            # Demand function
            agent.resource_demand = (
                self.config.alpha * agent.health_status
                + self.config.beta * agent.decision_state
            )

    def _aggregate_demand(self, t: int) -> float:
        """Aggregate agent demand with scenario shock."""
        total_demand = sum(agent.resource_demand for agent in self.agents)
        return total_demand * self._demand_shock_multiplier(t)

    def _update_system(self, t: int, demand: float) -> Tuple[float, float]:
        """Update resources and capacity."""
        inflow = 20.0 + 10.0 * self.policy_strength
        outflow = 0.03 * demand
        loss = self._resource_loss(t)

        self.resources = max(0.0, self.resources + inflow - outflow - loss)

        self.capacity = max(
            1.0,
            self.capacity
            + self.config.gamma * self.resources
            - self.config.delta * self.capacity
            + self.config.digital_transformation,
        )

        return self.resources, self.capacity

    def _service_continuity(self, demand: float, capacity: float) -> float:
        """Continuity score in [0, 1]."""
        unmet = max(0.0, demand - capacity)
        return max(0.0, 1.0 - (unmet / (demand + EPSILON)))

    def _resource_utilization_efficiency(
        self,
        demand: float,
        resources: float,
        capacity: float,
    ) -> float:
        """Simple efficiency metric."""
        served = min(demand, capacity)
        return served / (resources + EPSILON)

    def _policy_utility(
        self,
        system_pressure: float,
        resources: float,
        capacity: float,
        service_continuity: float,
    ) -> float:
        """Utility function for adaptive policy intelligence."""
        w1, w2, w3, w4 = 0.4, 0.2, 0.2, 0.2
        return (
            w1 * (-system_pressure)
            + w2 * resources / 1000.0
            + w3 * capacity / 1000.0
            + w4 * service_continuity
        )

    def _update_policy(
        self,
        current_utility: float,
        previous_utility: float,
    ) -> None:
        """Adaptive policy update rule."""
        gradient = current_utility - previous_utility
        self.policy_strength += self.config.learning_rate * gradient
        self.policy_strength = max(0.0, min(1.0, self.policy_strength))

    def run(self) -> Dict[str, List[float]]:
        """Run the full simulation."""
        previous_utility = 0.0
        system_pressure = 0.0

        for t in range(self.config.horizon):
            self._update_agents(system_pressure=system_pressure)
            demand = self._aggregate_demand(t=t)
            resources, capacity = self._update_system(t=t, demand=demand)

            system_pressure = demand / (capacity + EPSILON)
            service_continuity = self._service_continuity(demand, capacity)
            rue = self._resource_utilization_efficiency(demand, resources, capacity)

            current_utility = self._policy_utility(
                system_pressure=system_pressure,
                resources=resources,
                capacity=capacity,
                service_continuity=service_continuity,
            )
            self._update_policy(current_utility, previous_utility)
            previous_utility = current_utility

            self.history["demand"].append(demand)
            self.history["resources"].append(resources)
            self.history["capacity"].append(capacity)
            self.history["system_pressure"].append(system_pressure)
            self.history["service_continuity"].append(service_continuity)
            self.history["resource_utilization_efficiency"].append(rue)
            self.history["policy_strength"].append(self.policy_strength)

        return self.history

    def resilience_index(self) -> float:
        """Compute average resilience over the simulation horizon."""
        if not self.history["service_continuity"]:
            raise ValueError("Run the simulation before computing the resilience index.")

        scores = []
        for sci, sp in zip(
            self.history["service_continuity"],
            self.history["system_pressure"],
        ):
            scores.append(sci * (1.0 / (1.0 + sp)))

        return sum(scores) / len(scores)


def summarize_scenario(name: str, sim: HealthSystemSimulation) -> Dict[str, float | str]:
    """Compute summary metrics for one completed simulation."""
    history = sim.history

    avg_pressure = sum(history["system_pressure"]) / len(history["system_pressure"])
    peak_pressure = max(history["system_pressure"])
    avg_continuity = sum(history["service_continuity"]) / len(history["service_continuity"])
    avg_rue = (
        sum(history["resource_utilization_efficiency"])
        / len(history["resource_utilization_efficiency"])
    )
    resilience = sim.resilience_index()
    final_policy = history["policy_strength"][-1]
    final_capacity = history["capacity"][-1]
    final_resources = history["resources"][-1]

    return {
        "Scenario": name,
        "Avg System Pressure": avg_pressure,
        "Peak System Pressure": peak_pressure,
        "Avg Service Continuity": avg_continuity,
        "Avg Resource Efficiency": avg_rue,
        "Resilience Index": resilience,
        "Final Policy Strength": final_policy,
        "Final Capacity": final_capacity,
        "Final Resources": final_resources,
    }


def run_scenario(name: str, config: ModelConfig, seed: int = 42) -> Tuple[HealthSystemSimulation, Dict[str, float | str]]:
    """Run one scenario and return both the simulator and its summary."""
    sim = HealthSystemSimulation(config=config, seed=seed)
    sim.run()
    summary = summarize_scenario(name, sim)

    print(f"\nScenario: {name}")
    print(f"Average System Pressure     : {summary['Avg System Pressure']:.3f}")
    print(f"Peak System Pressure        : {summary['Peak System Pressure']:.3f}")
    print(f"Average Service Continuity  : {summary['Avg Service Continuity']:.3f}")
    print(f"Average Resource Efficiency : {summary['Avg Resource Efficiency']:.3f}")
    print(f"Resilience Index            : {summary['Resilience Index']:.3f}")
    print(f"Final Policy Strength       : {summary['Final Policy Strength']:.3f}")
    print(f"Final Capacity              : {summary['Final Capacity']:.3f}")
    print(f"Final Resources             : {summary['Final Resources']:.3f}")

    return sim, summary


def save_summary_csv(summaries: List[Dict[str, float | str]], output_path: Path) -> None:
    """Save scenario summaries as a CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "Scenario",
        "Avg System Pressure",
        "Peak System Pressure",
        "Avg Service Continuity",
        "Avg Resource Efficiency",
        "Resilience Index",
        "Final Policy Strength",
        "Final Capacity",
        "Final Resources",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in summaries:
            formatted_row = row.copy()
            for key in fieldnames[1:]:
                formatted_row[key] = f"{float(formatted_row[key]):.3f}"
            writer.writerow(formatted_row)


def save_plot(
    scenario_results: Dict[str, HealthSystemSimulation],
    metric_key: str,
    title: str,
    y_label: str,
    output_path: Path,
) -> None:
    """Save a single figure for a given metric across scenarios."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 5))

    for scenario_name, sim in scenario_results.items():
        x_values = list(range(1, len(sim.history[metric_key]) + 1))
        y_values = sim.history[metric_key]
        plt.plot(x_values, y_values, label=scenario_name)

    plt.xlabel("Time Step")
    plt.ylabel(y_label)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def main() -> None:
    """Run all scenarios and save outputs."""
    output_dir = Path("outputs")

    scenarios = [
        ("Baseline", ModelConfig()),
        ("Demand Shock", ModelConfig(demand_shock_factor=2.0)),
        ("Resource Constraint", ModelConfig(resource_loss_factor=0.40)),
        ("Digital Transformation", ModelConfig(digital_transformation=8.0)),
    ]

    scenario_results: Dict[str, HealthSystemSimulation] = {}
    summaries: List[Dict[str, float | str]] = []

    for name, config in scenarios:
        sim, summary = run_scenario(name, config, seed=42)
        scenario_results[name] = sim
        summaries.append(summary)

    save_summary_csv(summaries, output_dir / "simulation_results_summary.csv")

    save_plot(
        scenario_results,
        metric_key="system_pressure",
        title="System Pressure Trajectories Across Simulation Scenarios",
        y_label="System Pressure",
        output_path=output_dir / "figure_2_system_pressure.png",
    )

    save_plot(
        scenario_results,
        metric_key="capacity",
        title="Capacity Evolution Under Alternative Simulation Scenarios",
        y_label="Capacity",
        output_path=output_dir / "figure_3_capacity.png",
    )

    save_plot(
        scenario_results,
        metric_key="resources",
        title="Resource Trajectories Across Simulation Scenarios",
        y_label="Resources",
        output_path=output_dir / "figure_4_resources.png",
    )

    save_plot(
        scenario_results,
        metric_key="policy_strength",
        title="Evolution of Adaptive Policy Strength Over Time",
        y_label="Policy Strength",
        output_path=output_dir / "figure_5_policy_strength.png",
    )

    print(f"\nOutputs saved to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
