# Preregistration: Active Quantum Zeno Space Memory on Physical Superconducting QPUs

Author: Máté Róbert (ORCID 0009-0003-3986-6039)  
Repository: https://github.com/silentnoisehun/quantum-active-space-memory  
Date: 2026-11-08  
Hardware Target: IBM Quantum Superconducting Transmon Processors (with Dynamic Circuits / Mid-Circuit Feedforward support)

---

## 1. Scientific Hypothesis
Passive quantum space memory (unmonitored, decaying remnants in transmon chips) is strictly null.  
However, **Active Space Memory**—where the electromagnetic cavity mode and transmon are dynamically coupled via continuous/mid-circuit weak measurement and real-time feedforward (Quantum Zeno Dynamics)—maintains the quantum state significantly beyond the native $T_1$ relaxation and coherent dephasing horizon.

### Core Prediction
Under repeated perturbation drives $R_x(\theta)$ and environmental decay:
1. **Passive Arm (Unmonitored / Free Decay):** The excited state $|1\rangle$ rapidly decays into the ground state $|0\rangle$ with fidelity $F_{\text{passive}} \to 0$ as cycle count $N$ increases.
2. **Active Zeno Arm (Mid-Circuit Measurement + Dynamic Feedforward):** The measurement backaction and fast classical FPGA feedback pin the wavefunction to the target state, yielding $F_{\text{active}} \gg F_{\text{passive}}$ for all cycle horizons $N \in \{5, 10, 20, 40\}$.

---

## 2. Experimental Protocol & Circuit Design

### State Initialization
Target state: $|1\rangle = X |0\rangle$.

### Cycle Structure ($N$ iterations)
Each cycle applies:
1. **Perturbation operator:** $R_x(\theta = 0.15\pi)$ (coherent rotation trying to destroy $|1\rangle$).
2. **Mid-circuit readout:** `measure(q[0], c[step])` (diszperzív csatolás a readout üreghez).
3. **Dynamic conditional correction:**
   ```python
   with circuit.if_test((c[step], 0)):
       circuit.x(q[0]) # Immediate feedforward restoration
   ```

### Control Arm (Passive Decay)
Applies the identical sequence of $N$ perturbation operators $R_x(\theta)$ without mid-circuit measurements and without feedforward, followed by a single terminal measurement.

---

## 3. Decision Rules & Statistical Gate
- **Sample Size:** 1,000 to 4,000 shots per circuit.
- **Success Criterion:**
  $$\Delta F(N) = F_{\text{active}}(N) - F_{\text{passive}}(N) > 0.30$$
  at $N \ge 20$ cycles, with two-sample binomial test $p < 10^{-6}$.
- **Evidence Threshold:** Confirmed only when validated on a physical IBM Quantum QPU backend.
