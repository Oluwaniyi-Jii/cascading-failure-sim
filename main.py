import argparse
from cascading_sim.graph import generate_network, SUPPORTED_TOPOLOGIES
from cascading_sim.engine import simulate_cascade


def main():
    parser = argparse.ArgumentParser(description="Cascading Failure Simulator")
    parser.add_argument("--topology", choices=list(SUPPORTED_TOPOLOGIES), default="barabasi_albert")
    parser.add_argument("--nodes", type=int, default=100)
    parser.add_argument("--alpha", type=float, default=0.15)
    parser.add_argument("--load-strategy", choices=["degree", "betweenness", "uniform"], default="degree")
    parser.add_argument("--initial-failures", type=int, default=1, help="Number of initial node failures")
    parser.add_argument("--attack-strategy", choices=["target_hub", "random"], default="target_hub")
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

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
