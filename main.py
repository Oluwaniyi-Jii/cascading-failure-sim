import argparse
import numpy as np
from cascading_sim.graph import generate_network, SUPPORTED_TOPOLOGIES
from cascading_sim.engine import simulate_cascade
from cascading_sim.sweep import run_alpha_sweep


def main():
    parser = argparse.ArgumentParser(description="Cascading Failure Simulator")
    parser.add_argument("--topology", choices=list(SUPPORTED_TOPOLOGIES), default="barabasi_albert")
    parser.add_argument("--nodes", type=int, default=100)
    parser.add_argument("--alpha", type=float, default=0.15, help="Capacity tolerance factor alpha (single run)")
    parser.add_argument("--load-strategy", choices=["degree", "betweenness", "uniform"], default="degree")
    parser.add_argument("--initial-failures", type=int, default=1, help="Number of initial node failures")
    parser.add_argument("--attack-strategy", choices=["target_hub", "random"], default="target_hub")
    parser.add_argument("--seed", type=int, default=42)

    # Sweep mode flags
    parser.add_argument("--sweep", action="store_true", help="Run a parameter sweep across alpha tolerance levels")
    parser.add_argument("--alpha-min", type=float, default=0.0, help="Min alpha for sweep")
    parser.add_argument("--alpha-max", type=float, default=0.5, help="Max alpha for sweep")
    parser.add_argument("--alpha-steps", type=int, default=6, help="Number of alpha steps in sweep")
    parser.add_argument("--trials", type=int, default=3, help="Number of trial seeds per alpha step")

    args = parser.parse_args()

    if args.sweep:
        alpha_vals = np.linspace(args.alpha_min, args.alpha_max, args.alpha_steps)
        print(f"=== Running Parameter Sweep over Alpha Tolerance ===")
        print(f"Topology: {args.topology} | Nodes: {args.nodes} | Attack: {args.attack_strategy}")
        print(f"Alpha range: [{args.alpha_min:.2f}, {args.alpha_max:.2f}] ({args.alpha_steps} steps, {args.trials} trials/step)\n")

        res = run_alpha_sweep(
            alpha_values=alpha_vals,
            topology=args.topology,
            num_nodes=args.nodes,
            load_strategy=args.load_strategy,
            initial_failures=args.initial_failures,
            attack_strategy=args.attack_strategy,
            num_trials=args.trials,
            base_seed=args.seed,
        )

        print(f"{'Alpha':<8} | {'Failed Nodes (%)':<20} | {'Giant Comp. Ratio':<20} | {'Avg Steps':<10}")
        print("-" * 65)
        for i in range(len(res["alpha"])):
            a = res["alpha"][i]
            f_mean = res["failed_pct_mean"][i]
            f_std = res["failed_pct_std"][i]
            g_mean = res["giant_cc_mean"][i]
            g_std = res["giant_cc_std"][i]
            s_mean = res["steps_mean"][i]
            print(f"{a:<8.3f} | {f_mean:6.1f}% (±{f_std:4.1f})     | {g_mean:6.3f} (±{g_std:5.3f})    | {s_mean:<10.1f}")

    else:
        G = generate_network(
            topology=args.topology,
            num_nodes=args.nodes,
            alpha=args.alpha,
            load_strategy=args.load_strategy,
            seed=args.seed,
        )

        print(f"Network initialized: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges (alpha={args.alpha})")
        
        results = simulate_cascade(
            G,
            initial_failures=args.initial_failures,
            strategy=args.attack_strategy,
            seed=args.seed,
        )

        print(f"\nCascade Simulation Results:")
        print(f"  - Attack strategy: {args.attack_strategy} ({args.initial_failures} initial failure(s))")
        print(f"  - Initial target node(s): {results['initial_failed_nodes']}")
        print(f"  - Converged in: {results['steps']} iteration step(s)")
        print(f"  - Total failed nodes: {results['total_failures']} / {G.number_of_nodes()} ({results['failure_percentage']:.1f}%)")

        print("\nStep History:")
        for entry in results["history"]:
            step_idx = entry["step"]
            new_f = len(entry["new_failures"])
            tot_f = entry["total_failures"]
            print(f"  Step {step_idx}: +{new_f} new failure(s) -> {tot_f} total failed")


if __name__ == "__main__":
    main()
