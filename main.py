import argparse
from cascading_sim.graph import generate_network, SUPPORTED_TOPOLOGIES


def main():
    parser = argparse.ArgumentParser(description="Cascading Failure Simulator")
    parser.add_argument("--topology", choices=list(SUPPORTED_TOPOLOGIES), default="barabasi_albert")
    parser.add_argument("--nodes", type=int, default=100)
    parser.add_argument("--alpha", type=float, default=0.2)
    parser.add_argument("--load-strategy", choices=["degree", "betweenness", "uniform"], default="degree")
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    G = generate_network(
        topology=args.topology,
        num_nodes=args.nodes,
        alpha=args.alpha,
        load_strategy=args.load_strategy,
        seed=args.seed,
    )

    loads = [G.nodes[n]["load"] for n in G.nodes]
    capacities = [G.nodes[n]["capacity"] for n in G.nodes]

    print(f"Graph initialized: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    print(f"Loads: min={min(loads):.2f}, max={max(loads):.2f}, avg={sum(loads)/len(loads):.2f}")
    print(f"Capacities (alpha={args.alpha}): min={min(capacities):.2f}, max={max(capacities):.2f}")


if __name__ == "__main__":
    main()

