# Quantum Active Space Memory: Experimental Demonstration of Active Quantum Zeno Dynamics on IBM Quantum Heron Processors

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.quantum-active-space-memory.svg)](https://zenodo.org/badge/latestdoi/silentnoisehun/quantum-active-space-memory)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Author:** Máté Róbert (ORCID: [0009-0003-3986-6039](https://orcid.org/0009-0003-3986-6039))  
**Repository:** https://github.com/silentnoisehun/quantum-active-space-memory  
**Hardware Verification:** `ibm_marrakesh` (156-qubit Heron r2, Job `dbo63b5t7fqc73akk78g`, Physical Qubit 0, 2026-11-08)  

---

## Abstract
Passive quantum memory in superconducting architectures—defined as unmonitored residual state retention in idle transmon chips across independent executions—was recently shown to be strictly null across a pooled meta-analysis of 1,016 hardware jobs (Fisher $\chi^2 = 24.63$, $p = 0.135$; Stouffer $Z = +0.29$, $p = 0.387$, see `silentnoisehun/quantum-pooled-holdout`). Here we demonstrate that **Active Space Memory**—where the quantum state is continuously coupled to an electromagnetic cavity field via mid-circuit measurement and fast classical feedforward (Quantum Zeno Dynamics)—dynamically stabilizes the transmon state against coherent rotational perturbations and environmental decoherence. 

Executing OpenQASM 3 dynamic circuits on the 156-qubit IBM Quantum Heron processor (`ibm_marrakesh`), we observe an active Z-basis survival probability of **$97.20\% \pm 1.02\text{pp}$** ($95\%\text{ CI}: [95.96\%, 98.08\%]$) over $N=10$ perturbation cycles, compared to **$50.10\% \pm 3.10\text{pp}$** ($95\%\text{ CI}: [47.01\%, 53.19\%]$) in the unmonitored passive control arm. This constitutes a statistically definitive net protection advantage of **$\Delta P_{|1\rangle} = +47.10\text{pp}$** ($95\%\text{ CI}: [43.84\%, 50.36\%]$, two-sample binomial $z = 24.31$, $p < 10^{-15}$).

---

## 1. Physical Model & Paradigm Shift

### 1.1 The Limits of Passive Quantum Storage
Classical information storage operates predominantly as a passive container: physical media retain bit values under zero power input. In superconducting transmon architectures, however, an isolated system is strictly open to thermal and radiative environments, undergoing spontaneous relaxation ($T_1$) and pure dephasing ($T_\phi$). Without continuous active intervention or macroscopic quantum error correction, passive quantum space memory decays monotonically to the thermal ground state.

### 1.2 Active Space Coupling via Quantum Zeno Dynamics
By driving the transmon-cavity dispersive interaction $H_{\text{int}} = \hbar \chi (a^\dagger a) \sigma_z$ through mid-circuit projective readout and sub-microsecond FPGA feedforward (`if_else`), we construct an active dynamical attractor:
1. **Zeno Projection:** Frequent mid-circuit measurements along $\sigma_z$ suppress coherent rotations $\Omega \sigma_x$ with a transition probability scaling quadratically as $P_{\text{flip}} \approx (\Omega \tau)^2 \ll 1$.
2. **Conditional Feedforward:** If a projection error or decay event ($|0\rangle$) is detected, a fast conditional $X$ gate restores the target $|1\rangle$ state within 200–300 ns.
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
| **Active Zeno Dynamic Arm** | **97.20%** | **972 / 1,000** | **[95.96%, 98.08%]** | Coherently locked in target eigenstate |
| **Passive Control Arm** | **50.10%** | **501 / 1,000** | **[47.01%, 53.19%]** | Complete rotational dephasing to mixed state |
| **Net Zeno Advantage ($\Delta P_{|1\rangle}$)** | **+47.10pp** | **+471 shots** | **[+43.84pp, +50.36pp]** | **Confirmed on physical hardware ($z = 24.31$, $p < 10^{-15}$)** |

### 3.2 Simulation Benchmark (Qiskit Aer Thermal Noise)
Under realistic transmon thermal noise ($T_1 = 80\ \mu\text{s}$, $T_2 = 100\ \mu\text{s}$, gate time $= 30\text{ ns}$, readout time $= 800\text{ ns}$):

| Cycles ($N$) | Passive Control $P_{|1\rangle}$ | Active Zeno $P_{|1\rangle}$ | Net Delta ($\Delta P_{|1\rangle}$) |
| :---: | :---: | :---: | :---: |
| **$N = 5$** | 15.2% | **99.0%** | **+83.8%** |
| **$N = 10$** | 49.7% | **99.4%** | **+49.7%** |
| **$N = 20$** | **0.7%** | **98.9%** | **+98.2%** |
| **$N = 30$** | 49.7% | **99.0%** | **+49.3%** |

*(Note: In the preliminary draft, $N=5$ delta was recorded as 83.9% due to intermediate rounding; the exact difference is $99.0\% - 15.2\% = 83.8\%$.)*

---

## 4. Limitations and Future Work
1. **Single-Qubit Demonstration:** This execution was conducted on physical Qubit 0 of `ibm_marrakesh`. Replicating across diverse qubit topologies, frequency detunings, and multi-qubit entangled states is required.
2. **Metric Scope:** We measure the computational Z-basis retention probability $P_{|1\rangle}$. Quantum state tomography is planned to characterize off-diagonal coherence preservation in superposition states $|+\rangle = (|0\rangle + |1\rangle)/\sqrt{2}$.
3. **Temporal Scope:** Physical hardware trials evaluated $N=10$ dynamic cycles. Extended testing up to $N=100$ cycles will probe the asymptotic equilibrium fidelity limit imposed by measurement fidelity ($p(0|1) = 5.47\%$) and FPGA latency.

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
  version      = {v1.1.0},
  url          = {https://github.com/silentnoisehun/quantum-active-space-memory}
}
```
