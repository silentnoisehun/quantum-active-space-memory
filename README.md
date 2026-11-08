Quantum Active Space Memory: Experimental Demonstration of Active Quantum Zeno Dynamics on IBM Quantum Heron Processors
Author: Máté Róbert (ORCID: 0009-0003-3986-6039)
Repository: https://github.com/silentnoisehun/quantum-active-space-memory
Hardware Verification: ibm_marrakesh (156-qubit Heron r2, Job dbo63b5t7fqc73akk78g, Physical Qubit 0, 2026-11-08)
License: MIT
Version: v1.3.1

Abstract
Passive quantum memory in superconducting architectures, defined as unmonitored residual state retention in idle transmon chips across independent executions, was recently shown to be strictly null across a pooled meta-analysis of 1,016 hardware jobs (Fisher chi2 = 24.63, p = 0.135; Stouffer Z = +0.29, p = 0.387, see silentnoisehun/quantum-pooled-holdout). Here we demonstrate that Active Space Memory, where the quantum state is continuously coupled to an electromagnetic cavity field via mid-circuit measurement and fast classical feedforward (Quantum Zeno Dynamics), dynamically stabilizes the transmon state against coherent rotational perturbations and environmental decoherence.

Executing OpenQASM 3 dynamic circuits on the 156-qubit IBM Quantum Heron processor (ibm_marrakesh), we observe an active Z-basis survival probability of 97.20% over N = 10 perturbation cycles, compared to 50.10% in the unmonitored passive control arm. This constitutes a statistically definitive net protection advantage of Delta P|1> = +47.10pp (two-sample binomial: unpooled z = 28.29, pooled z = 23.91, p < 10^-15, two-sided).

1. Physical Model & Paradigm Shift
1.1 The Limits of Passive Quantum Storage
Classical information storage operates predominantly as a passive container: physical media retain bit values under zero power input. In superconducting transmon architectures, however, an isolated system is strictly open to thermal and radiative environments, undergoing spontaneous relaxation (T1) and pure dephasing (T_phi). Without continuous active intervention or macroscopic quantum error correction, passive quantum space memory decays monotonically to the thermal ground state.

1.2 Active Space Coupling via Quantum Zeno Dynamics
By driving the transmon-cavity dispersive interaction H_int = hbar chi (a† a) sigma_z through mid-circuit projective readout and FPGA feedforward (if_else), we construct an active dynamical attractor:

Zeno Projection: Frequent mid-circuit measurements along sigma_z suppress coherent rotations Omega sigma_x with a transition probability scaling quadratically as P_flip approx (Omega tau)^2 << 1.
Conditional Feedforward: If a projection error or decay event (|0>) is detected, the FPGA branch logic evaluates with sub-microsecond latency (approx 300 ns), triggering a fast conditional X pulse (approx 60 ns). The closed-loop cycle duration is dominated by dispersive resonator readout integration (2,684 ns), yielding an overall stabilization loop time of tau_loop approx 3.0 us.
Active Medium: The quantum state is dynamically sustained through the continuous energy and information exchange between the transmon and the cavity field.
2. Experimental Protocol
2.1 State Preparation and Perturbation
Target State: |1> = X |0>.

Perturbation Operator: Rx(theta = 0.15 pi) per cycle.

Active Arm: N cycles of [Rx(theta) -> Measure(q, c_step) -> if c_step == 0: X(q)], followed by terminal measurement.

Passive Control Arm: N unmonitored rotations Rx(theta) without intermediate measurements or feedback, followed by terminal measurement.

2.2 Metric Definition
We report the Z-basis Target Survival Probability P|1> = N|1> / N_total, where N|1> is the count of terminal |1> outcomes over N_total = 1,000 physical shots. This metric directly reflects state retention against the applied X-rotation without requiring full quantum state tomography.

3. Results
3.1 Physical Hardware Execution (ibm_marrakesh)
Backend: ibm_marrakesh (156-qubit Heron r2, revision 2.1.0)
Physical Qubit: Qubit 0
Daily Backend Calibration Data (2026-11-08):
Energy relaxation: T1 = 373.22 us
Coherence dephasing: T2 = 35.05 us
Readout error: 3.125% (p(0|1) = 5.47%, p(1|0) = 0.78%)
Single-qubit initialization error: 0.098%
Readout pulse duration: 2,684 ns
Compiler Pass: Qiskit 2.4 Preset Pass Manager (optimization_level=1)
Execution Mode: Qiskit Runtime SamplerV2 (shots=1000, Job ID: dbo63b5t7fqc73akk78g)

Experimental Arm
Measured P
1>

Shots Retained
95% Confidence Interval (Wilson)
Physical Status
Active Zeno Dynamic Arm
97.20%
972 / 1,000
[95.96%, 98.08%]

Z-basis pinned in target eigenstate
1> via active feedforward

Passive Control Arm
50.10%
501 / 1,000
[47.01%, 53.19%]

Rotated pure state under unmitigated Rx(theta) drive (P
1> approx 50.1%)

Net Zeno Advantage (Delta P
1>)

+47.10pp
+471 shots
[+43.84pp, +50.36pp]

Confirmed on physical hardware (unpooled z = 28.29, pooled z = 23.91, p < 10^-15, two-sided)

Note on Readout Error Ceiling and Calibration Drift:
The nominal backend calibration report at 08:04 UTC indicated an assignment error p(0|1) = 5.47%, which would impose a theoretical static unmitigated detection ceiling of 1 - p(0|1) = 94.53%. The unmitigated physical execution of job dbo63b5t7fqc73akk78g at 11:57 UTC recorded 972/1,000 raw counts (97.20%). This +2.67pp excess over static nominal calibration reflects empirical temporal drift in transmon discriminator thresholds / readout resonator frequency over the approx 4 hours between calibration and execution (indicating real-time p(0|1) <= 2.80% during run, inferred from the observed survival under the hypothesis of parameter drift, not directly measured via a contemporaneous isolated |1> calibration circuit), rather than post-hoc error mitigation (all counts reported are unmitigated raw bitstrings).

3.2 Physical Multi-Qubit Hardware Demonstration: 2-Qubit Entangled Bell State (|Phi+>)
Target Backend: ibm_marrakesh (156-qubit Heron r2 processor)
Physical Hardware Job ID: dbo6lqgou4as73b5jdag
Topology: Physical Transmons Q0 and Q2 (Logical Data Qubits q0, q1) coupled via Qubit 1 (Ancilla Transmon)
Target Entangled State: |Phi+> = (|00> + |11>) / sqrt(2)
Active Mechanism: Non-destructive parity stabilizer S = Z_q0 Z_q1 = Z_Q0 Z_Q2 measured via ancilla Q1 + fast feedforward restoration
Terminal Verification: Bell-basis inversion (CX -> H -> Measure), where |00> indicates |Phi+> parity retention
Total Physical Shots: 1,000 shots per arm (Execution Date: 2026-11-08)

Experimental Arm
Measured P
Phi+>

Shots Retained
95% Confidence Interval (Wilson)
Physical Status
Active Parity Zeno Arm
33.60%
336 / 1,000
[30.74%, 36.59%]

Parity subspace protected (3x survival vs passive), but below bipartite GME threshold (F <= 50%)

Passive Control Arm
10.90%
109 / 1,000
[9.12%, 12.98%]

Rotational dispersion and dephasing below random mixed floor (25%)
Net Parity Survival Advantage (Delta P)
+22.70pp
+227 shots
[+19.19pp, +26.21pp]

Confirmed on physical hardware (unpooled z = 12.68, pooled z = 12.20, p = 7.6 x 10^-37, two-sided)
Delta P|Phi+> = P_active - P_passive = +22.70pp

Academic Arbitration on Bell State Entanglement:
While the active parity circuit triples parity subspace survival (33.60% vs 10.90%, +22.70pp, unpooled z = 12.68, pooled z = 12.20), the state remains 16.40pp below the bipartite entanglement witness threshold (F > 50.0%). The ZZ parity stabilizer protects computational bit-flip parities, but does not protect against phase dephasing. Genuine bipartite entanglement was not preserved.

3.3 Physical 3-Qubit GHZ Genuine Multipartite Entanglement (GME) Witness
Target Backend: ibm_marrakesh (156-qubit Heron r2 processor)
Physical Hardware Job ID: dbo6t18qtr0c73ae383g
Topology: 5 Physical transmons in a linear chain Q0 - Q1 - Q2 - Q3 - Q4. Logical data qubits q0, q1, q2 are mapped to physical transmons Q0, Q2, Q4. Ancilla transmons Q1 and Q3 measure the non-destructive parity stabilizers S1 = Z_q0 Z_q1 = Z_Q0 Z_Q2 and S2 = Z_q1 Z_q2 = Z_Q2 Z_Q4.
Target Tripartite State: |GHZ_3> = (|000> + |111>) / sqrt(2)
Tomographic Protocol: 5 Pauli bases (ZZZ, XXX, XYY, YXY, YYX) across 10 circuits
Total Physical Shots: 10,000 shots (1,000 shots / basis / arm, Execution Date: 2026-11-08)

Circuit Complexity & Physical Gate Overhead:
Active Arm: Transpiles to 23 native CZ gates, 6 mid-circuit measurements, 6 dynamic resets, 6 conditional feedforward branches (circuit depth 59). Total mid-circuit readout integration time = 6 x 2,684 ns approx 16.1 us, consuming 46% of transmon dephasing time (T2 = 35.05 us).
Passive Arm: Transpiles to 8 native CZ gates, 0 mid-circuit measurements, 0 feedforward branches (circuit depth 19).

Fidelity Formulation:
F_GHZ = (P_000 + P_111) / 2 + (1/8) * (<XXX> - <XYY> - <YXY> - <YYX>)

Component / Metric
Active Zeno Arm
Passive Control Arm
Net Zeno Advantage (Delta)
Physical Interpretation
P_000 (Z-basis)

51.20%
13.80%
+37.40pp
Ground state subspace pinned
P_111 (Z-basis)

27.30%
11.90%
+15.40pp
Excited subspace pinned
Population (P_000 + P_111) / 2

39.25%
12.85%
+26.40pp
3x population retention vs random mixed floor (12.5%)

<XXX> Expectation

-0.050
+0.894
-
Commutation with Rx(theta): = 0 preserves passive; active dephases
<XYY> Expectation

+0.104
+0.004
-
Stabilizer correlation
<YXY> Expectation

-0.004
-0.012
-
Stabilizer correlation
<YYX> Expectation

+0.060
+0.004
-
Stabilizer correlation
Coherence Re[rho_000,111]

-2.63%
+11.22%
-13.85pp
Active Zeno destroys phase coherence via projective dephasing and gate noise
TOTAL GHZ FIDELITY (F_GHZ)

36.62% [95% CI: ±2.00%]

24.07% [95% CI: ±1.94%]

+12.55% [95% CI: ±2.79%]

Population gain outweighs phase loss; GME not preserved (unpooled z = 8.83, p = 1.1 x 10^-18, two-sided)
[Rx][X]

(Note on Statistical Uncertainty: Error margins of ±2.00%, ±1.94%, and ±2.79% represent 95% Confidence Intervals (1.96 x SE) propagated from the independent multinomial variances of the 5 tomographic basis measurements.)

Rigorous Scientific Conclusion (GME Falsification & Phase Decoherence Mechanism):

Why Passive <XXX> = +0.894: The perturbation drive is Rx(theta) = exp(-i theta/2 X), which strictly commutes with the Pauli X operator ([Rx(theta), X] = 0). In the passive circuit, the drive mathematically cannot rotate the state out of the XXX eigenspace; <XXX> degrades only due to background thermal relaxation across its minimal depth (19 gates).

Why Active Destroys Phase Coherence (Re = -2.63% vs +11.22%): Repeated non-destructive ZZ syndrome projections project the quantum superposition onto the Z-eigenbasis subspace, acting as an aggressive phase dephasing channel that converts (|000> + |111>) / sqrt(2) into an incoherent classical statistical mixture (1/2)(|000><000| + |111><111|). Combined with the accumulated noise of 23 physical CZ gates and 16.1 us of mid-circuit measurement idle dephasing (T2 = 35.05 us), phase coherence is completely eradicated.[rho]

The Arbitration: Active Zeno stabilization does NOT preserve Genuine Multipartite Entanglement (F_active = 36.62%). It provides powerful, statistically verified stabilization of classical bit populations (39.25% vs 12.85%), but destroys quantum phase coherence. Preserving tripartite entanglement under continuous Zeno dynamics fundamentally requires transverse stabilizer measurements (e.g., interleaving an XXX stabilizer) to protect the phase degree of freedom.

3.4 Simulation Benchmark (Qiskit Aer Thermal Noise)
Under realistic transmon thermal noise (T1 = 80 us, T2 = 100 us, gate time = 30 ns, readout time = 800 ns):

Cycles (N)
Passive Control P
1>

Active Zeno P
1>

Net Delta (Delta P
1>)

N = 5
15.2%
99.0%
+83.8%
N = 10
49.7%
99.4%
+49.7%
N = 20
0.7%
98.9%
+98.2%
N = 30
49.7%
99.0%
+49.3%
(Note: In the preliminary draft, N=5 delta was recorded as 83.9% due to intermediate rounding; the exact difference is 99.0% - 15.2% = 83.8%.)

4. Limitations and Future Work
Multi-Qubit Scaling: Single-qubit state preservation (Delta = +47.10pp), 2-qubit entangled Bell-state parity protection (Delta = +22.70pp), and 3-qubit GHZ state population stabilization (>3x advantage over passive decay) have all been demonstrated on physical hardware (ibm_marrakesh). Scaling to 2D topological surface-code tiles and higher-order stabilizer lattices remains the next development milestone.

Metric Scope: We measure computational Z-basis retention probability P|1>, Bell-basis parity survival probability P|Phi+>, and 5-basis GME witness operators for tripartite GHZ states. Full multi-qubit state tomography and randomized benchmarking across varying cycle depths (N in ) are planned to further quantify phase coherence degradation mechanisms.[5][100]

Temporal Scope: Physical hardware trials evaluated N = 10 single-qubit, N = 4 two-qubit Bell, and N = 3 three-qubit GHZ dynamic cycles. Extended testing up to N = 100 cycles will probe the asymptotic equilibrium fidelity limit imposed by two-qubit CZ gate errors and FPGA latency.

5. References
B. Misra and E. C. G. Sudarshan, "The Zeno's paradox in quantum theory," Journal of Mathematical Physics 18, 756-763 (1977).
P. Facchi and S. Pascazio, "Quantum Zeno dynamics," Physical Review Letters 89, 080401 (2002).
H. M. Wiseman and G. J. Milburn, "Quantum Measurement and Control," Cambridge University Press (2009).
S. Krinner et al., "Realization of real-time fault-tolerant quantum error correction on a superconducting processor," Nature 605, 669-674 (2022).
IBM Quantum, "Dynamic Circuits and OpenQASM 3 Specification," IBM Research (2023).
M. Róbert, "Pooled Exploration/Confirmation Meta-Analysis across 1,016 Superconducting Hardware Jobs," GitHub repository: silentnoisehun/quantum-pooled-holdout (2026).

Citation
@software{robert2026active_space_memory,
author = {Róbert, Máté},
title = {Quantum Active Space Memory: Experimental Demonstration of Active Quantum Zeno Dynamics on IBM Quantum Heron Processors},
month = nov,
year = 2026,
publisher = {Zenodo / GitHub},
version = {v1.3.1},
url = {https://github.com/silentnoisehun/quantum-active-space-memory}
}
