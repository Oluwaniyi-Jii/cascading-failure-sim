from typing import Any, Sequence
import numpy as np
from .graph import generate_network
from .engine import simulate_cascade
from .metrics import compute_cascade_metrics


def run_alpha_sweep(
    alpha_values: Sequence[float],
    topology: str = "barabasi_albert",
    num_nodes: int = 100,
    load_strategy: str = "degree",
    initial_failures: int = 1,
    attack_strategy: str = "target_hub",
    num_trials: int = 5,
    base_seed: int = 42,
    **kwargs: Any
) -> dict[str, Any]:
    """
    Run a parameter sweep over capacity tolerance alpha across multiple trial seeds.

    Args:
        alpha_values: List or array of tolerance alpha values to test.
        topology: 'barabasi_albert', 'erdos_renyi', or 'watts_strogatz'.
        num_nodes: Number of nodes in the graph.
        load_strategy: 'degree', 'betweenness', or 'uniform'.
        initial_failures: Number of initial failed nodes.
        attack_strategy: 'target_hub' or 'random'.
        num_trials: Number of random seed repetitions per alpha value.
        base_seed: Base seed for reproducibility.

    Returns:
        Dict with keys: 'alpha', 'failed_pct_mean', 'failed_pct_std',
        'giant_cc_mean', 'giant_cc_std', 'steps_mean', 'steps_std', 'raw_results'.
    """
    results = {
        "alpha": list(alpha_values),
        "failed_pct_mean": [],
        "failed_pct_std": [],
        "giant_cc_mean": [],
        "giant_cc_std": [],
        "steps_mean": [],
        "steps_std": [],
        "raw_results": [],
    }

    for i, alpha in enumerate(alpha_values):
        trial_failed_pcts = []
        trial_giant_ccs = []
        trial_steps = []

        for trial in range(num_trials):
            seed = base_seed + i * 1000 + trial
            G = generate_network(
                topology=topology,
                num_nodes=num_nodes,
                alpha=alpha,
                load_strategy=load_strategy,
                seed=seed,
                **kwargs
            )
            sim_res = simulate_cascade(
                G,
                initial_failures=initial_failures,
                strategy=attack_strategy,
                seed=seed
            )
            metrics = compute_cascade_metrics(sim_res)

            trial_failed_pcts.append(metrics["failed_percentage"])
            trial_giant_ccs.append(metrics["giant_component_ratio"])
            trial_steps.append(metrics["steps_to_converge"])

        results["failed_pct_mean"].append(float(np.mean(trial_failed_pcts)))
        results["failed_pct_std"].append(float(np.std(trial_failed_pcts)))
        results["giant_cc_mean"].append(float(np.mean(trial_giant_ccs)))
        results["giant_cc_std"].append(float(np.std(trial_giant_ccs)))
        results["steps_mean"].append(float(np.mean(trial_steps)))
        results["steps_std"].append(float(np.std(trial_steps)))
        results["raw_results"].append({
            "alpha": alpha,
            "failed_pcts": trial_failed_pcts,
            "giant_ccs": trial_giant_ccs,
            "steps": trial_steps,
        })

    return results
