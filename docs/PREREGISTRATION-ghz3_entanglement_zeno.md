# Preregistration: 3-Qubit GHZ Genuine Multipartite Entanglement (GME) Active Zeno Protection

Author: Máté Róbert (ORCID: 0009-0003-3986-6039)  
Repository: https://github.com/silentnoisehun/quantum-active-space-memory  
Date: 2026-11-08  
Hardware Target: IBM Quantum Heron Processor (`ibm_marrakesh`, 156 qubits)

---

## 1. Objective and Hypothesis
To evaluate whether non-destructive parity stabilizer Quantum Zeno dynamics (continuous/mid-circuit syndrome detection + fast classical feedforward) can preserve **Genuine Multipartite Entanglement (GME)** of a 3-qubit GHZ state $|\text{GHZ}_3\rangle = (|000\rangle + |111\rangle)/\sqrt{2}$ against coherent rotational perturbations and environmental decoherence.

### Primary Criteria
1. **GME Entanglement Witness:** Genuine multipartite entanglement is confirmed if and only if:
   $$F_{\text{GHZ}} = \frac{P_{000} + P_{111}}{2} + \text{Re}[\rho_{000, 111}] > 0.50 \quad (50.0\%)$$
   where:
   $$\text{Re}[\rho_{000, 111}] = \frac{1}{8} \left( \langle XXX \rangle - \langle XYY \rangle - \langle YXY \rangle - \langle YYX \rangle \right)$$
2. **Active Zeno Advantage:** The active parity stabilization arm must demonstrate a statistically significant fidelity advantage:
   $$\Delta F_{\text{GHZ}} = F_{\text{active}} - F_{\text{passive}} > 0.15 \quad (p < 0.001)$$

---

## 2. Hardware Topology & Calibration Ceiling
- **Physical Qubits on `ibm_marrakesh`:**
  - Data Qubits: Qubit 0, Qubit 2, Qubit 4
  - Parity Ancilla Qubits: Qubit 1 (couples Q0 and Q2), Qubit 3 (couples Q2 and Q4)
  - Topology: Linear nearest-neighbor chain `0 — 1 — 2 — 3 — 4`
- **Daily Calibration Ceiling (2026-11-08):**
  - Q0: $p(0|1) = 5.47\%$
  - Q2: $p(0|1) = 0.78\%$
  - Q4: $p(0|1) = 2.93\%$
  - Unmitigated 3-Qubit Readout Ceiling: $(1 - 0.0547)(1 - 0.0078)(1 - 0.0293) = \mathbf{91.04\%}$

---

## 3. Circuit Protocol ($N = 3$ Cycles)
- **Target State:** $|\text{GHZ}_3\rangle = (|000\rangle + |111\rangle)/\sqrt{2}$ initialized via $H(q_0) \to CX(q_0, q_1) \to CX(q_1, q_2)$.
- **Perturbation Operator:** $R_x(\theta = 0.15\pi)$ simultaneously applied to all 3 data qubits.
- **Active Stabilizer Loop:**
  - Ancilla 1 measures $S_1 = Z_0 Z_1 \to$ if odd, conditional $X(q_0)$.
  - Ancilla 2 measures $S_2 = Z_1 Z_2 \to$ if odd, conditional $X(q_2)$.
- **Passive Arm:** Identical perturbations without intermediate syndrome measurements or feedback.
- **4 Measurement Bases:**
  1. `ZZZ`: computational basis readout.
  2. `XXX`: $H \otimes H \otimes H$ rotation before readout.
  3. `XYY`: $H \otimes (S^\dagger H) \otimes (S^\dagger H)$ rotation.
  4. `YXY` / `YYX`: permuted phase rotations.
- **Shots:** 1,000 physical shots per basis per arm (total 8,000 shots).
