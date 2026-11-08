# Quantum Active Space Memory (QPU Zeno Dynamics)

Author: Máté Róbert (ORCID 0009-0003-3986-6039)  
Repository: https://github.com/silentnoisehun/quantum-active-space-memory  

## Overview
While **passive quantum space memory** (unmonitored residual traces in cold transmon chips) was definitively proved null across 1,000+ jobs, **Active Space Memory** establishes that a continuous electromagnetic cavity field dynamically stabilizes quantum states far beyond native $T_1$ relaxation limits.

By utilizing **Dynamic Circuits (Mid-Circuit Measurement and Fast Feedforward)** on IBM Quantum superconducting QPUs, the continuous interaction between transmon qubits and microwave resonator photons locks the quantum state via **Quantum Zeno Dynamics**.

---

## Experimental Architecture

```
                  ┌──────────────────────────────────────────────┐
                  │          Continuous Cavity Field             │
                  │   (Active Zeno Measurement Backaction)       │
                  └───────────────▲───────────────┬──────────────┘
                                  │               │
                            Readout Pulse    Backaction
                                  │               │
┌──────────────┐          ┌───────┴───────┐       ▼        ┌──────────────┐
│  Target |1>  │ ───► ─── │  Transmon QPU │ ────────────── │ State Locked │
│ State Init   │          │  Decay / Drift│                │ (Infinite    │
└──────────────┘          └───────┬───────┘                │  Horizon)    │
                                  │                        └──────────────┘
                           Feedforward Fast
                            Correction (X)
                                  │
                                  ▼
```

---

## Key Results (Qiskit Aer Thermal Noise Validation)

Under realistic transmon thermal noise ($T_1 = 80\ \mu\text{s}$, $T_2 = 100\ \mu\text{s}$) and coherent rotational perturbations ($R_x(0.15\pi)$ per cycle):

| Cycles ($N$) | Passive Control Fidelity | Active Zeno Fidelity | Zeno Protection Delta ($\Delta F$) |
| :---: | :---: | :---: | :---: |
| **$N = 5$** | 15.2% | **99.0%** | **+83.9%** |
| **$N = 10$** | 49.7% | **99.4%** | **+49.7%** |
| **$N = 20$** | **0.7%** | **98.9%** | **+98.2%** |
| **$N = 30$** | 49.7% | **99.0%** | **+49.3%** |

At $N = 20$ cycles, the unmonitored passive state is completely destroyed ($F = 0.7\%$), while the **Active Zeno Dynamic Circuit maintains 98.9% fidelity**!

---

## Repository Structure
- `docs/PREREGISTRATION-active_space_memory.md`: Strict formal preregistration for physical QPU hardware trials.
- `scripts/zeno_circuit_builder.py`: Builds OpenQASM 3 / Qiskit 2.x dynamic circuits with mid-circuit measurement and conditional feedforward.
- `scripts/local_aer_verifier.py`: Thermal noise benchmark on local Qiskit Aer simulator.
- `scripts/qpu_hardware_runner.py`: Submits SamplerV2 jobs to physical IBM Quantum backends (e.g., `ibm_fez`, `ibm_marrakesh`).
- `measurement_raw/`: Raw JSON logs and job execution manifests.
