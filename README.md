# Cascading Failure Simulator

A hands-on Python simulator I'm building to experiment with cascading failures, feedback loops, and phase transitions in complex networks.

## What I've Learned So Far

Running a sweep on a 100-node scale-free network (Barabási–Albert) showed a clear tipping point:

- **$\alpha \le 0.15$**: Taking out 1 hub triggers a complete domino effect (100% network failure).
- **$\alpha \approx 0.20$**: Tipping point regime where the system starts struggling to contain the cascade.
- **$\alpha \ge 0.30$**: The network has enough buffer capacity to absorb the shock, keeping 99% of the system functional.

## Quick Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run a single target attack simulation
python main.py --topology barabasi_albert --nodes 100 --alpha 0.15

# Run a parameter sweep to see the phase transition
python main.py --sweep --topology barabasi_albert --nodes 100 --alpha-min 0.0 --alpha-max 0.5 --alpha-steps 6 --trials 3

# Run tests
pytest
```
