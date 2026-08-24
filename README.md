# Cascading Failure Simulator

A hands-on Python simulator built to experiment with cascading failures, feedback loops, phase transitions, and visual network state dynamics in complex systems.

## Interactive Browser Visualizer

You can launch the real-time interactive browser dashboard to watch cascades unfold visually step-by-step:

```bash
python main.py --web
```
*(Or simply open `visualizer.html` directly in your web browser!)*

### Visualizer Features:
- **Physics-Based Canvas**: Drag nodes, zoom/pan, hover over nodes to inspect real-time load vs. capacity limits.
- **Topology Selectors**: Switch between Barabási–Albert, Erdős–Rényi, and Watts–Strogatz networks.
- **Interactive Controls**: Adjust Node count ($N$) and Capacity Tolerance ($\alpha$), trigger targeted hub attacks or random faults, and step forward ($t+1$) or auto-play at variable speeds.

---

## Quick Command Line Usage

```bash
# Run a single target attack simulation & plot network state (healthy vs failed)
python main.py --topology barabasi_albert --nodes 100 --alpha 0.15 --plot

# Run a parameter sweep & generate phase transition curve
python main.py --sweep --topology barabasi_albert --nodes 100 --alpha-min 0.0 --alpha-max 0.5 --alpha-steps 6 --trials 3 --plot

# Run unit tests
pytest
```
