## Experimental Hardware Confirmation: Scaling Active Space Memory to Multi-Qubit & Tripartite States

This release delivers the complete physical hardware dataset measuring Active Quantum Space Memory across 1, 2, and 3-qubit states on the 156-qubit IBM Quantum Heron processor (`ibm_marrakesh`).

### 1. Summary of Physical Hardware Executions on `ibm_marrakesh`
| Experiment | Target State | Hardware Job ID | Active Zeno | Passive Control | Net Advantage ($\Delta$) | Statistical Significance | Physical Interpretation |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **Single-Qubit State** | $|1\rangle$ (Q0) | `dbo63b5t7fqc73akk78g` | **97.20%** | 50.10% | **+47.10pp** | unpooled $z = 28.29$ (pooled $z = 23.91$), $p < 10^{-15}$ | Z-basis pinned in target eigenstate |
| **Two-Qubit Bell State** | $|\Phi^+\rangle$ (Q0, Q2 via Q1) | `dbo6lqgou4as73b5jdag` | **33.60%** | 10.90% | **+22.70pp** | unpooled $z = 12.68$ (pooled $z = 12.20$), $p = 3.8 \times 10^{-37}$ | Parity subspace preserved (3x vs passive); $F \le 50\%$ |
| **Three-Qubit GHZ Population** | $|\text{GHZ}_3\rangle$ (Q0, Q2, Q4) | `dbo6t18qtr0c73ae383g` | **39.25%** | 12.85% | **+26.40pp** | $>3\times$ vs 12.5% mixed floor | Classical bit population pinned |
| **Three-Qubit GHZ Fidelity** | 5-Basis GME Witness | `dbo6t18qtr0c73ae383g` | **36.62% [95% CI: ±2.00%]** | **24.07% [95% CI: ±1.94%]** | **+12.55% [95% CI: ±2.79%]** | unpooled $z = 8.83$, $p = 1.1 \times 10^{-18}$ | Population gain outweighs phase loss; GME not preserved |

---

### 2. Tripartite GHZ GME Witness Analysis (Job `dbo6t18qtr0c73ae383g`, 10,000 Shots)
- **Physical Topology:** 5 transmons in a linear chain `Q0 — Q1 — Q2 — Q3 — Q4`. Logical data qubits $q_0, q_1, q_2$ mapped to physical transmons Q0, Q2, Q4; ancillas Q1 and Q3 measure non-destructive parity stabilizers $S_1 = Z_{\text{Q0}} Z_{\text{Q2}}$ and $S_2 = Z_{\text{Q2}} Z_{\text{Q4}}$.
- **Circuit Complexity:**
  - **Active Arm:** 23 native CZ gates, 6 mid-circuit measurements, 6 dynamic resets, 6 feedforward branches (circuit depth 59). Total readout integration time = $6 \times 2,684\text{ ns} \approx 16.1\ \mu\text{s}$ ($46\%$ of transmon $T_2 = 35.05\ \mu\text{s}$).
  - **Passive Arm:** 8 native CZ gates, 0 mid-circuit measurements, 0 feedforward branches (circuit depth 19).
- **Fidelity Formulation:**
  $$F_{\text{GHZ}} = \frac{P_{000} + P_{111}}{2} + \frac{1}{8} \left( \langle XXX \rangle - \langle XYY \rangle - \langle YXY \rangle - \langle YYX \rangle \right)$$

### 3. Rigorous Scientific Discoveries & Phase Decoherence Mechanism
1. **Classical Population Pinning Confirmed:** Active Zeno dynamics forcefully pins computational populations ($39.25\%$ active vs $12.85\%$ passive, where $12.5\%$ is the random 8-state mixed floor).
2. **Entanglement Preservation Falsified ($F \le 50.0\%$):** Active Zeno dynamics with non-destructive $ZZ$ stabilizers does **NOT** preserve Genuine Multipartite Entanglement ($F_{\text{active}} = 36.62\% \le 50.0\%$).
3. **Why Passive $\langle XXX \rangle = +0.894$:** The perturbation drive $R_x(\theta) = \exp(-i \frac{\theta}{2} X)$ strictly commutes with the $X$ Pauli operator ($[R_x, X] = 0$). The drive cannot rotate the state out of the $XXX$ eigenspace; it degrades only through minimal idle thermal relaxation across depth 19.
4. **Why Active Destroys Phase Coherence ($\text{Re}[\rho] = -2.63\%$ vs $+11.22\%$):** Repeated projective $Z$-stabilizer measurements project the superposition into the $Z$-eigenbasis, collapsing $(|000\rangle + |111\rangle)/\sqrt{2}$ into a classical statistical mixture $\frac{1}{2}(|000\rangle\langle 000| + |111\rangle\langle 111|)$. Together with 23 CZ gates and $16.1\ \mu\text{s}$ of measurement idle dephasing, off-diagonal phase coherence is destroyed ($-13.85\text{pp}$ loss).
5. **Readout Calibration Drift on Qubit 0:** Raw single-qubit retention of $97.20\%$ (exceeding nominal static $1 - p(0|1) = 94.53\%$) reflects physical transmon parameter drift over 4 hours between 08:04 UTC daily calibration and 11:57 UTC execution (real-time $p(0|1) \le 2.80\%$, inferred from observed survival under the hypothesis of parameter drift, not directly measured via a contemporaneous isolated $|1\rangle$ calibration circuit).
6. **Closed-Loop Latency:** FPGA decision branch logic operates in sub-microsecond latency ($\sim 300\text{ ns}$), but the total closed-loop cycle is dominated by the dispersive readout integration pulse ($2,684\text{ ns}$), resulting in an overall stabilization loop time of $\tau_{\text{loop}} \approx 3.0\ \mu\text{s}$.
