from pathlib import Path
from typing import Any, Optional
import matplotlib
matplotlib.use("Agg")  # Use non-interactive backend for headless file output
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import seaborn as sns

# Set clean aesthetic styling
sns.set_theme(style="whitegrid", palette="muted")


def plot_phase_transition(
    sweep_results: dict[str, Any],
    save_path: Optional[str] = "outputs/phase_transition.png",
    title: str = "Phase Transition: Tolerance Factor vs Cascade Impact"
) -> plt.Figure:
    """
    Plot Initial Load Stress / Capacity Tolerance (alpha) vs.
    Final Cascade Size (Failed %) and Giant Component Ratio.
    """
    alphas = np.array(sweep_results["alpha"])
    failed_mean = np.array(sweep_results["failed_pct_mean"])
    failed_std = np.array(sweep_results["failed_pct_std"])
    giant_mean = np.array(sweep_results["giant_cc_mean"])
    giant_std = np.array(sweep_results["giant_cc_std"])

    fig, ax1 = plt.subplots(figsize=(9, 5.5), dpi=300)

    # Plot 1: Failed Node Percentage (Left Y-axis)
    color1 = "#d95f02"
    ax1.set_xlabel("Capacity Tolerance Factor (α)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Final Failed Nodes (%)", color=color1, fontsize=11, fontweight="bold")
    line1 = ax1.plot(alphas, failed_mean, "o-", color=color1, linewidth=2.5, label="Failed Nodes (%)")
    ax1.fill_between(alphas, failed_mean - failed_std, failed_mean + failed_std, color=color1, alpha=0.15)
    ax1.tick_params(axis="y", labelcolor=color1)
    ax1.set_ylim(-5, 105)

    # Plot 2: Giant Component Ratio (Right Y-axis)
    ax2 = ax1.twinx()
    color2 = "#7570b3"
    ax2.set_ylabel("Giant Component Ratio (P_∞)", color=color2, fontsize=11, fontweight="bold")
    line2 = ax2.plot(alphas, giant_mean, "s--", color=color2, linewidth=2.5, label="Giant Component Ratio")
    ax2.fill_between(alphas, giant_mean - giant_std, giant_mean + giant_std, color=color2, alpha=0.15)
    ax2.tick_params(axis="y", labelcolor=color2)
    ax2.set_ylim(-0.05, 1.05)

    # Combine legends
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="center right", frameon=True)

    plt.title(title, fontsize=12, fontweight="bold", pad=15)
    fig.tight_layout()

    if save_path:
        out_file = Path(save_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_file, bbox_inches="tight")
        print(f"Saved phase transition plot to: {out_file}")

    return fig


def plot_network_state(
    G: nx.Graph,
    save_path: Optional[str] = "outputs/network_state.png",
    title: str = "Network State (Healthy vs Failed)"
) -> plt.Figure:
    """
    Visualize network topology highlighting healthy vs failed nodes.
    """
    fig, ax = plt.subplots(figsize=(8, 7), dpi=300)
    pos = nx.spring_layout(G, seed=42)

    # Separate healthy and failed nodes
    healthy_nodes = [n for n in G.nodes() if G.nodes[n].get("status") == "healthy"]
    failed_nodes = [n for n in G.nodes() if G.nodes[n].get("status") == "failed"]

    # Draw edges
    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.2, edge_color="#cccccc")

    # Draw healthy nodes
    if healthy_nodes:
        nx.draw_networkx_nodes(
            G, pos, nodelist=healthy_nodes, ax=ax,
            node_color="#2b8cbe", node_size=120, label="Healthy"
        )

    # Draw failed nodes
    if failed_nodes:
        nx.draw_networkx_nodes(
            G, pos, nodelist=failed_nodes, ax=ax,
            node_color="#de2d26", node_size=160, label="Failed", node_shape="X"
        )

    plt.title(title, fontsize=12, fontweight="bold")
    plt.legend(loc="upper right", frameon=True)
    plt.axis("off")
    fig.tight_layout()

    if save_path:
        out_file = Path(save_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_file, bbox_inches="tight")
        print(f"Saved network state plot to: {out_file}")

    return fig
