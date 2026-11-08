# Quantum Active Space Memory: Experimental Demonstration of Active Quantum Zeno Dynamics on IBM Quantum Heron Processors

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.quantum-active-space-memory.svg)](https://zenodo.org/badge/latestdoi/silentnoisehun/quantum-active-space-memory)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Author:** Máté Róbert (ORCID: [0009-0003-3986-6039](https://orcid.org/0009-0003-3986-6039))  
**Repository:** https://github.com/silentnoisehun/quantum-active-space-memory  
**Hardware Verification:** `ibm_marrakesh` (156-qubit Heron r2, Job `dbo63b5t7fqc73akk78g`, Physical Qubit 0, 2026-11-08)  

---

## Abstract
Passive quantum memory in superconducting architectures—defined as unmonitored residual state retention in idle transmon chips across independent executions—was recently shown to be strictly null across a pooled meta-analysis of 1,016 hardware jobs (Fisher $\chi^2 = 24.63$, $p = 0.135$; Stouffer $Z = +0.29$, $p = 0.387$, see `silentnoisehun/quantum-pooled-holdout`). Here we demonstrate that **Active Space Memory**—where the quantum state is continuously coupled to an electromagnetic cavity field via mid-circuit measurement and fast classical feedforward (Quantum Zeno Dynamics)—dynamically stabilizes the transmon state against coherent rotational perturbations and environmental decoherence. 

Executing OpenQASM 3 dynamic circuits on the 156-qubit IBM Quantum Heron processor (`ibm_marrakesh`), we observe an active Z-basis survival probability of **$97.20\% \pm 1.04\text{pp}$** ($95\%\text{ CI}: [95.98\%, 98.06\%]$) over $N=10$ perturbation cycles, compared to **$50.10\% \pm 3.09\text{pp}$** ($95\%\text{ CI}: [47.01\%, 53.19\%]$) in the unmonitored passive control arm. This constitutes a statistically definitive net protection advantage of **$\Delta P_{|1\rangle} = +47.10\text{pp}$** ($95\%\text{ CI}: [43.84\%, 50.36\%]$, two-sample binomial: unpooled $z = 28.29$, pooled $z = 23.91$, two-sided $p < 10^{-15}$).

> **v1.3.1 — correction release.** Every number below was re-derived from the committed raw files in `measurement_raw/` and, where a hardware-side value was claimed, re-measured against the live backend **without consuming QPU time**. Run `python scripts/verify_paper_statistics.py` to reproduce the whole ledger (60/60 checks).
> Standalone paper: [`docs/PAPER-v1.3.1.md`](docs/PAPER-v1.3.1.md) · print-ready: [`docs/PAPER-v1.3.1.html`](docs/PAPER-v1.3.1.html) · full verification ledger and the list of corrections: [Section 6 of the paper](docs/PAPER-v1.3.1.md#6-reproducibility--verification-notes).

---

## 1. Physical Model & Paradigm Shift

### 1.1 The Limits of Passive Quantum Storage
Classical information storage operates predominantly as a passive container: physical media retain bit values under zero power input. In superconducting transmon architectures, however, an isolated system is strictly open to thermal and radiative environments, undergoing spontaneous relaxation ($T_1$) and pure dephasing ($T_\phi$). Without continuous active intervention or macroscopic quantum error correction, passive quantum space memory decays monotonically to the thermal ground state.

### 1.2 Active Space Coupling via Quantum Zeno Dynamics
By driving the transmon-cavity dispersive interaction $H_{\text{int}} = \hbar \chi (a^\dagger a) \sigma_z$ through mid-circuit projective readout and FPGA feedforward (`if_else`), we construct an active dynamical attractor:
1. **Zeno Projection:** Frequent mid-circuit measurements along $\sigma_z$ suppress coherent rotations $\Omega \sigma_x$ with a transition probability scaling quadratically as $P_{\text{flip}} \approx (\Omega \tau)^2 \ll 1$.
2. **Conditional Feedforward:** If a projection error or decay event ($|0\rangle$) is detected, the FPGA branch logic evaluates with sub-microsecond latency ($\sim 300\text{ ns}$), triggering a fast conditional $X$ pulse ($\sim 60\text{ ns}$). The closed-loop cycle duration is dominated by dispersive resonator readout integration ($2,684\text{ ns}$), yielding an overall stabilization loop time of $\tau_{\text{loop}} \approx 3.0\ \mu\text{s}$.
3. **Active Medium:** The quantum state is dynamically sustained through the continuous energy and information exchange between the transmon and the cavity field.

---

## 2. Experimental Protocol

```
                  ┌──────────────────────────────────────────────┐
                  │          Dispersive Cavity Readout           │
                  │        (Zeno Projection Backaction)          │
                  └───────────────▲───────────────┬──────────────┘
                                  │               │
                            Readout Pulse    Backaction
                                  │               │
┌──────────────┐          ┌───────┴───────┐       ▼        ┌──────────────┐
│  Target |1>  │ ───► ─── │  Transmon QPU │ ────────────── │ State Locked │
│ State Init   │          │  Rx(θ) Drift  │                │ (Metastable  │
└──────────────┘          └───────┬───────┘                │  Horizon)    │
                                  │                        └──────────────┘
                           FPGA Feedforward
                            Correction (X)
                                  │
                                  ▼
```

### 2.1 State Preparation and Perturbation
- **Target State:** $|1\rangle = X|0\rangle$.
- **Perturbation Operator:** $R_x(\theta = 0.15\pi)$ per cycle.
- **Active Arm:** $N$ cycles of $[R_x(\theta) \to \text{Measure}(q, c_{\text{step}}) \to \text{if } c_{\text{step}}==0: X(q)]$, followed by terminal measurement.
- **Passive Control Arm:** $N$ unmonitored rotations $R_x(\theta)$ without intermediate measurements or feedback, followed by terminal measurement.

### 2.2 Metric Definition
We report the **Z-basis Target Survival Probability** $P_{|1\rangle} = N_{|1\rangle} / N_{\text{total}}$, where $N_{|1\rangle}$ is the count of terminal $|1\rangle$ outcomes over $N_{\text{total}} = 1,000$ physical shots. This metric directly reflects state retention against the applied $X$-rotation without requiring full quantum state tomography.

---

## 3. Results

### 3.1 Physical Hardware Execution (`ibm_marrakesh`)
- **Backend:** `ibm_marrakesh` (156-qubit Heron r2, revision 2.1.0)
- **Physical Qubit:** Qubit 0
- **Daily Backend Calibration Data (2026-11-08):**
  - Energy relaxation: $T_1 = 373.22\ \mu\text{s}$
  - Coherence dephasing: $T_2 = 35.05\ \mu\text{s}$
  - Readout error: $3.125\%$ ($p(0|1) = 5.47\%$, $p(1|0) = 0.78\%$)
  - Single-qubit initialization error: $0.098\%$
  - Readout pulse duration: $2,684\text{ ns}$
- **Compiler Pass:** Qiskit 2.4 Preset Pass Manager (`optimization_level=1`)
- **Execution Mode:** Qiskit Runtime SamplerV2 (`shots=1000`, Job ID: `dbo63b5t7fqc73akk78g`)

| Experimental Arm | Measured $P_{|1\rangle}$ | Shots Retained | 95% Confidence Interval (Wilson) | Physical Status |
| :--- | :---: | :---: | :---: | :--- |
| **Active Zeno Dynamic Arm** | **97.20%** | **972 / 1,000** | **[95.98%, 98.06%]** | Z-basis pinned in target eigenstate $\|1\rangle$ via active feedforward |
| **Passive Control Arm** | **50.10%** | **501 / 1,000** | **[47.01%, 53.19%]** | Rotated pure state under unmitigated $R_x(\theta)$ drive ($P_{\|1\rangle} \approx 50.1\%$) |
| **Net Zeno Advantage ($\Delta P_{|1\rangle}$)** | **+47.10pp** | **+471 shots** | **[+43.84pp, +50.36pp]** | **Confirmed on physical hardware (unpooled $z = 28.29$, pooled $z = 23.91$, two-sided $p < 10^{-15}$)** |

> **Note on Readout Error Ceiling and Calibration Drift:**  
> The nominal backend calibration report at 08:04 UTC indicated an assignment error $p(0|1) = 5.47\%$, which would impose a theoretical static unmitigated detection ceiling of $1 - p(0|1) = 94.53\%$. The unmitigated physical execution of job `dbo63b5t7fqc73akk78g` at 11:57 UTC recorded 972/1,000 raw counts ($97.20\% \pm 1.04\text{pp}$). This $+2.67\text{pp}$ excess over static nominal calibration reflects empirical temporal drift in transmon discriminator thresholds / readout resonator frequency over the ~4 hours between calibration and execution (indicating real-time $p(0|1) \le 2.80\%$ during run, inferred from the observed survival under the hypothesis of parameter drift, not directly measured via a contemporaneous isolated $|1\rangle$ calibration circuit), rather than post-hoc error mitigation (all counts reported are unmitigated raw bitstrings).

---

### 3.2 Physical Multi-Qubit Hardware Demonstration: 2-Qubit Entangled Bell State (|Φ+⟩)
- **Target Backend:** `ibm_marrakesh` (156-qubit Heron r2 processor)
- **Physical Hardware Job ID:** `dbo6lqgou4as73b5jdag`
- **Topology:** Physical Transmons Q0 and Q2 (Logical Data Qubits $q_0, q_1$) coupled via Qubit 1 (Ancilla Transmon)
- **Target Entangled State:** $|\Phi^+\rangle = (|00\rangle + |11\rangle)/\sqrt{2}$
- **Active Mechanism:** Non-destructive parity stabilizer $S = Z_{q_0} Z_{q_1} = Z_{\text{Q0}} Z_{\text{Q2}}$ measured via ancilla Q1 + fast feedforward restoration
- **Terminal Verification:** Bell-basis inversion (CX $\to$ H $\to$ Measure), where $|00\rangle$ indicates $|\Phi^+\rangle$ parity retention
- **Total Physical Shots:** 1,000 shots per arm (Execution Date: 2026-11-08)

| Experimental Arm | Measured $P_{|\Phi^+\rangle}$ | Shots Retained | 95% Confidence Interval (Wilson) | Physical Status |
| :--- | :---: | :---: | :---: | :--- |
| **Active Parity Zeno Arm** | **33.60%** | **336 / 1,000** | **[30.74%, 36.59%]** | Parity subspace protected (3x survival vs passive), but below bipartite GME threshold ($F \le 50\%$) |
| **Passive Control Arm** | **10.90%** | **109 / 1,000** | **[9.12%, 12.98%]** | Rotational dispersion and dephasing below random mixed floor (25%) |
| **Net Parity Survival Advantage ($\Delta P$)** | **+22.70pp** | **+227 shots** | **[+19.19pp, +26.21pp]** | **Confirmed on physical hardware (unpooled $z = 12.69$, pooled $z = 12.20$, two-sided $p = 7.1 \times 10^{-37}$ unpooled / $3.0 \times 10^{-34}$ pooled)** |

$$\Delta P_{|\Phi^+\rangle} = P_{\text{active}} - P_{\text{passive}} = +22.70\% \quad (\text{unpooled } z = 12.69, \ \text{pooled } z = 12.20, \ \text{two-sided } p = 7.1 \times 10^{-37}\ \text{(unpooled)})$$

> **Academic Arbitration on Bell State Entanglement:**  
> While the active parity circuit triples parity subspace survival ($33.60\%$ vs $10.90\%$, $+22.70\text{pp}$, unpooled $z=12.69$), the state remains $16.40\text{pp}$ below the bipartite entanglement witness threshold ($F > 50.0\%$). The $ZZ$ parity stabilizer protects computational bit-flip parities, but does not protect against phase dephasing. Genuine bipartite entanglement was not preserved.

---

### 3.3 Physical 3-Qubit GHZ Genuine Multipartite Entanglement (GME) Witness
- **Target Backend:** `ibm_marrakesh` (156-qubit Heron r2 processor)
- **Physical Hardware Job ID:** `dbo6t18qtr0c73ae383g`
- **Topology:** 5 Physical transmons in a linear chain `Q0 — Q1 — Q2 — Q3 — Q4`. Logical data qubits $q_0, q_1, q_2$ are mapped to physical transmons Q0, Q2, Q4. Ancilla transmons Q1 and Q3 measure the non-destructive parity stabilizers $S_1 = Z_{q_0} Z_{q_1} = Z_{\text{Q0}} Z_{\text{Q2}}$ and $S_2 = Z_{q_1} Z_{q_2} = Z_{\text{Q2}} Z_{\text{Q4}}$.
- **Target Tripartite State:** $|\text{GHZ}_3\rangle = (|000\rangle + |111\rangle)/\sqrt{2}$
- **Tomographic Protocol:** 5 Pauli bases ($ZZZ$, $XXX$, $XYY$, $YXY$, $YYX$) across 10 circuits
- **Total Physical Shots:** **10,000 shots** (1,000 shots / basis / arm, Execution Date: 2026-11-08)

#### Circuit Complexity & Physical Gate Overhead:
Re-transpiled locally against the live `ibm_marrakesh` target (Qiskit 2.4.2, `optimization_level=1`, layouts `[0,2,4,1,3]` active / `[0,2,4]` passive):
- **Active Arm:** Transpiles to **26 native CZ gates, 6 mid-circuit measurements (+3 terminal readout), 6 dynamic resets, 6 conditional feedforward branches**. Circuit depth is 59 for the `ZZZ` basis and 61–62 for the four transverse bases. Total mid-circuit readout integration time = $6 \times 2,684\text{ ns} \approx 16.1\ \mu\text{s}$, consuming 46% of transmon dephasing time ($T_2 = 35.05\ \mu\text{s}$).
- **Passive Arm:** Transpiles to **8 native CZ gates, 0 mid-circuit measurements (3 terminal readout measurements), 0 dynamic resets, 0 feedforward branches**. Circuit depth is 19 for the `ZZZ` basis and 18–23 for the four transverse bases.

#### Fidelity Formulation:
$$F_{\text{GHZ}} = \frac{P_{000} + P_{111}}{2} + \frac{1}{8} \left( \langle XXX \rangle - \langle XYY \rangle - \langle YXY \rangle - \langle YYX \rangle \right)$$

| Component / Metric | Active Zeno Arm | Passive Control Arm | Net Zeno Advantage ($\Delta$) | Physical Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| **$P_{000}$ (Z-basis)** | **51.20%** | 13.80% | +37.40pp | Ground state subspace pinned |
| **$P_{111}$ (Z-basis)** | **27.30%** | 11.90% | +15.40pp | Excited subspace pinned |
| **Population $(P_{000}+P_{111})/2$** | **39.25%** | **12.85%** | **+26.40pp** | **>3x population retention vs random mixed floor (12.5%)** |
| $\langle XXX \rangle$ Expectation | -0.050 | +0.894 | - | Commutation with $R_x(\theta)$: $[R_x, X]=0$ preserves passive; active dephases |
| $\langle XYY \rangle$ Expectation | +0.104 | +0.004 | - | Stabilizer correlation |
| $\langle YXY \rangle$ Expectation | -0.004 | -0.012 | - | Stabilizer correlation |
| $\langle YYX \rangle$ Expectation | +0.060 | +0.004 | - | Stabilizer correlation |
| **Coherence $\text{Re}[\rho_{000, 111}]$** | **-2.63%** | **+11.22%** | **-13.85pp** | **Active Zeno destroys phase coherence via projective dephasing & gate noise** |
| **TOTAL GHZ FIDELITY ($F_{\text{GHZ}}$)** | **36.62% [95% CI: ±2.00%]** | **24.07% [95% CI: ±1.94%]** | **+12.55% [95% CI: ±2.79%]** | **Population gain outweighs phase loss; GME not preserved (unpooled $z = 8.83$, two-sided $p = 1.1 \times 10^{-18}$)** |

> *(Note on Statistical Uncertainty: Error margins of $\pm 2.00\%$, $\pm 1.94\%$, and $\pm 2.79\%$ represent 95% Confidence Intervals ($1.96 \times \text{SE}$) propagated from the independent multinomial variances of the 5 tomographic basis measurements.)*

> **Rigorous Scientific Conclusion (GME Falsification & Phase Decoherence Mechanism):**  
> 1. **Why Passive $\langle XXX \rangle = +0.894$:** The perturbation drive is $R_x(\theta) = \exp(-i \frac{\theta}{2} X)$, which strictly commutes with the Pauli $X$ operator ($[R_x(\theta), X] = 0$). In the passive circuit, the drive mathematically cannot rotate the state out of the $XXX$ eigenspace; $\langle XXX \rangle$ degrades only due to background thermal relaxation across its minimal depth (19 gates).  
> 2. **Why Active Destroys Phase Coherence ($\text{Re}[\rho] = -2.63\%$ vs $+11.22\%$):** Repeated non-destructive $ZZ$ syndrome projections project the quantum superposition onto the $Z$-eigenbasis subspace, acting as an aggressive phase dephasing channel that converts $(|000\rangle + |111\rangle)/\sqrt{2}$ into an incoherent classical statistical mixture $\frac{1}{2}(|000\rangle\langle 000| + |111\rangle\langle 111|)$. Combined with the accumulated noise of 26 physical CZ gates and $16.1\ \mu\text{s}$ of mid-circuit measurement idle dephasing ($T_2 = 35.05\ \mu\text{s}$), phase coherence is completely eradicated.  
> 3. **The Arbitration:** **Active Zeno stabilization does NOT preserve Genuine Multipartite Entanglement ($F_{\text{active}} = 36.62\% \le 50.0\%$)**. It provides powerful, statistically verified stabilization of classical bit populations ($39.25\%$ vs $12.85\%$), but destroys quantum phase coherence. Preserving tripartite entanglement under continuous Zeno dynamics fundamentally requires transverse stabilizer measurements (e.g., interleaving an $XXX$ stabilizer) to protect the phase degree of freedom.

---

### 3.4 Simulation Benchmark (Qiskit Aer Thermal Noise)
Under realistic transmon thermal noise ($T_1 = 80\ \mu\text{s}$, $T_2 = 100\ \mu\text{s}$, gate time $= 30\text{ ns}$, readout time $= 800\text{ ns}$), 2,000 shots per point:

| Cycles ($N$) | Passive Control $P_{|1\rangle}$ | Active Zeno $P_{|1\rangle}$ | Net Delta ($\Delta P_{|1\rangle}$) |
| :---: | :---: | :---: | :---: |
| **$N = 5$** | 15.15% | **99.00%** | **+83.85%** |
| **$N = 10$** | 49.70% | **99.35%** | **+49.65%** |
| **$N = 20$** | **0.65%** | **98.90%** | **+98.25%** |
| **$N = 30$** | 49.70% | **98.95%** | **+49.25%** |

*(Note: in the preliminary draft the $N=5$ delta was recorded as 83.9% due to intermediate rounding; the exact difference is $99.00\% - 15.15\% = 83.85\%$. The table carries the exact simulator values throughout; the underlying simulation outputs are unchanged.)*

---

## 4. Limitations and Future Work
1. **Multi-Qubit Scaling:** Single-qubit state preservation ($\Delta = +47.10\text{pp}$), 2-qubit entangled Bell-state parity protection ($\Delta = +22.70\text{pp}$), and 3-qubit GHZ state population stabilization ($>3\times$ advantage over passive decay) have all been demonstrated on physical hardware (`ibm_marrakesh`). Scaling to 2D topological surface-code tiles and higher-order stabilizer lattices remains the next development milestone.
2. **Metric Scope:** We measure computational Z-basis retention probability $P_{|1\rangle}$, Bell-basis parity survival probability $P_{|\Phi^+\rangle}$, and 5-basis GME witness operators for tripartite GHZ states. Full multi-qubit state tomography and randomized benchmarking across varying cycle depths ($N \in [5, 100]$) are planned to further quantify phase coherence degradation mechanisms.
3. **Temporal Scope:** Physical hardware trials evaluated $N=10$ single-qubit, $N=4$ two-qubit Bell, and $N=3$ three-qubit GHZ dynamic cycles. Extended testing up to $N=100$ cycles will probe the asymptotic equilibrium fidelity limit imposed by two-qubit CZ gate errors and FPGA latency.
4. **Calibration-Coupling Caveat:** The single-qubit arm's survival probability exceeds the static nominal readout-error ceiling ($94.53\%$). We attribute this to temporal calibration drift, and we did not run a contemporaneous isolated $|1\rangle$ calibration circuit in the same job, so the drift hypothesis is an inference from the observed survival rather than a direct measurement. A follow-up campaign should pair every Zeno job with a back-to-back calibration circuit to close this gap.

---

## 5. References
1. B. Misra and E. C. G. Sudarshan, *"The Zeno’s paradox in quantum theory,"* Journal of Mathematical Physics **18**, 756–763 (1977).
2. P. Facchi and S. Pascazio, *"Quantum Zeno dynamics,"* Physical Review Letters **89**, 080401 (2002).
3. H. M. Wiseman and G. J. Milburn, *"Quantum Measurement and Control,"* Cambridge University Press (2009).
4. S. Krinner et al., *"Realization of real-time fault-tolerant quantum error correction on a superconducting processor,"* Nature **605**, 669–674 (2022).
5. IBM Quantum, *"Dynamic Circuits and OpenQASM 3 Specification,"* IBM Research (2023).
6. M. Róbert, *"Pooled Exploration/Confirmation Meta-Analysis across 1,016 Superconducting Hardware Jobs,"* GitHub repository: `silentnoisehun/quantum-pooled-holdout` (2026).

---

## Citation

```bibtex
@software{robert2026active_space_memory,
  author       = {Róbert, Máté},
  title        = {Quantum Active Space Memory: Experimental Demonstration of Active Quantum Zeno Dynamics on IBM Quantum Heron Processors},
  month        = nov,
  year         = 2026,
  publisher    = {Zenodo / GitHub},
  version      = {v1.3.1},
  url          = {https://github.com/silentnoisehun/quantum-active-space-memory}
}
```
