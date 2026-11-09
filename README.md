# Quantum Active Space Memory: Active Quantum Zeno Dynamics on IBM Quantum Heron Processors

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Author:** Máté Róbert (ORCID: [0009-0003-3986-6039](https://orcid.org/0009-0003-3986-6039))
**Repository:** https://github.com/silentnoisehun/quantum-active-space-memory
**Version:** v1.3.3 (N=20 prereg gate PASSED, 2026-11-09)
**Hardware:** `ibm_marrakesh` (156-qubit Heron r2) — five jobs total (four v1.3.2 + one N=20 v1.3.3)

---

> ### v1.3.2 — what changed and why
>
> This is a **claim-correction** release. No new hardware was run for the headline numbers;
> three claims were re-examined against theory, and one of them reverses direction.
>
> 1. **Preregistration deviation disclosed.** The single-qubit experiment is governed by
>    `docs/PREREGISTRATION-active_space_memory.md`, whose gate requires ΔF > 0.30 **at N ≥ 20
>    cycles**. The run used **N = 10**. The effect-size and significance parts of the gate are
>    met; the cycle-count part is not. See §3.1.
> 2. **GHZ conclusion reversed.** The v1.3.1 text concluded that the ZZ-based Zeno loop
>    *fundamentally* destroys phase coherence and that transverse stabilisers are *required*.
>    The noiseless calculation says the opposite: on |GHZ₃⟩ the ZZ loop is **exactly
>    protective**, F_ideal = **1.0000**. The measured 0.3663 is an **implementation** loss, not
>    a principle. See §3.3.
> 3. **Bell arm re-labelled.** P(Φ⁺) after Bell-basis inversion is a parity-survival
>    probability, **not** an entanglement witness; the separability threshold for this quantity
>    is 50%, and the active arm (33.60%) is below it. See §3.2.
> 4. **"Beyond T₁" removed.** The protocol lasts 10 × ~3.0 µs ≈ 30 µs, which is **8%** of
>    T₁ = 373 µs. No statement about extending coherence beyond T₁ is made anywhere in this
>    document. See §1.2.
>
> The raw data are unchanged. `python scripts/verify_paper_statistics.py` still returns 60/60.

---

## Abstract

Passive quantum memory in superconducting architectures — unmonitored residual state retention
in idle transmon chips across independent executions — is not supported by a pooled
meta-analysis of 1,016 hardware jobs (Fisher χ² = 24.63, df = 18, p = 0.135; Stouffer Z = +0.29,
p = 0.387; `silentnoisehun/quantum-pooled-holdout`).

This work tests the complementary hypothesis: **active** retention, where the state is
re-projected by mid-circuit measurement and fast classical feedforward (Quantum Zeno
Dynamics), can hold a computational population against a coherent rotation.

On `ibm_marrakesh` (156-qubit Heron r2), a single transmon prepared in |1⟩ and perturbed by
10 cycles of R_x(0.15π) survives with P(|1⟩) = **97.20%** (972/1000, Wilson 95% CI
[95.98%, 98.06%]) when each cycle is followed by a projective readout and a conditional X,
versus **50.10%** (501/1000, [47.01%, 53.19%]) without monitoring — a net advantage of
**+47.10 pp** (unpooled z = 28.29, pooled z = 23.91, two-sided p < 10⁻¹⁵).

Two extensions behave as the protocol dictates and then **fail to scale**: a 2-qubit Bell
parity arm reaches 33.60% vs 10.90% (+22.70 pp) — parity survival, not entanglement — and a
3-qubit GHZ arm reaches F_GHZ = 0.3663 vs 0.2408 (+12.55 pp) — population stabilisation
without phase recovery. The noiseless bound for the GHZ arm is F = 1.0000, so the 0.63 gap is
gate and readout overhead, not a fundamental obstruction.

**The result of this paper is therefore an instrument result:** a digital Zeno feedback loop
on a 156-qubit processor holds a *classical* computational population with high confidence,
and the same loop, applied to superpositions, is limited by measurement-induced dephasing
(16.1 µs of mid-circuit readout = 46% of T₂) and by ancilla readout error, not by the physics
of the stabiliser.

---

## 1. Physical model

### 1.1 Passive storage in an open system

A transmon is an open system: it relaxes on T₁ and dephases on T₂ regardless of what the
algorithm intends. Without active intervention, a prepared state decays monotonically toward
the thermal ground state. Two independent v1-era campaigns tested whether anything *survives*
this decay across jobs (`quantum-space-memory`: Δ = +0.00023, p = 0.36; the zero-IQ arms:
Δ = −0.00069, p = 0.55 and Δ = −0.00135, p = 0.29) and found nothing above the sensitivity of
the design. Those nulls bound the passive effect; they do not prove it absent.

### 1.2 Active re-projection (what is actually implemented)

The loop implemented here is **digital**, not microwave-level:

$$|\psi\rangle \xrightarrow{\;R_x(\theta)\;} |\psi\rangle \xrightarrow{\;\text{measure } \sigma_z\;} c_k \xrightarrow{\;\text{if } c_k = 0:\; X\;} |\psi'\rangle$$

per cycle. There is no pulse-level control (OpenPulse is not available on the free plan), so
the "projection" is a full dispersive readout followed by a classical conditional X. What the
loop does, physically, is **re-prepare** the population in the target eigenstate at each cycle
boundary at the cost of destroying the off-diagonal coherence accumulated since the previous
measurement.

**Duration.** Ten cycles × (2.684 µs readout + ~0.06 µs conditional X + ~0.30 µs branch
latency) ≈ **30 µs**, i.e. **8% of T₁ = 373.22 µs**. Twenty cycles ≈ 61 µs ≈ 16% of T₁.
*This experiment does not extend coherence beyond T₁*, and no claim of that kind is made here.

---

## 2. Experimental protocol

```
┌──────────────┐        ┌───────────────────────────┐        ┌──────────────────┐
│ prepare |1⟩  │  ───►  │  N × [ R_x(0.15π)         │  ───►  │ terminal readout │
│   X |0⟩      │        │        measure q → c_k    │        │  P(|1⟩)          │
└──────────────┘        │        if c_k==0: X q ]    │        └──────────────────┘
                        └───────────────────────────┘
```

- **Target state:** |1⟩ = X|0⟩.
- **Perturbation:** R_x(θ = 0.15π) per cycle (θ chosen so the passive arm lands near cos²(Nθ/2)).
- **Active arm:** N cycles of `[R_x → measure(q, c_k) → if c_k==0: X(q)]`, then terminal readout.
- **Passive arm:** N unmonitored R_x(θ), then terminal readout.
- **Metric:** P(|1⟩) = N₁ / N_total from **unmitigated raw bitstrings**: no readout mitigation,
  no post-selection, no calibration circuits in the reported numbers.

**Register convention (matters for reading the data).** The active circuit writes mid-cycle
outcomes to `c[0]…c[N−1]` and the terminal outcome to `c[N]`. In the stored bitstring the
**leftmost character is c[N]**, i.e. the terminal measurement. Every number in this document
uses that convention; `scripts/extract_zeno_v2.py` implements it.

---

## 3. Results

### 3.1 Single qubit — the primary result, and its preregistration status

| | value |
|---|---|
| Backend / qubit | `ibm_marrakesh`, physical Q0 |
| Job | `dbo63b5t7fqc73akk78g`, submitted 2026-11-08 11:57:26 UTC |
| Cycles | **N = 10** |
| Shots | 1,000 per arm |
| Daily calibration (08:04 UTC) | T₁ = 373.22 µs, T₂ = 35.05 µs, readout error 3.125% (p(0\|1) = 5.47%, p(1\|0) = 0.78%) |

| Arm | P(\|1⟩) | Shots | Wilson 95% CI |
|---|---|---|---|
| Active Zeno | **97.20%** | 972/1000 | [95.98%, 98.06%] |
| Passive control | **50.10%** | 501/1000 | [47.01%, 53.19%] |
| Δ | **+47.10 pp** | +471 | [+43.84, +50.36] pp |

Unpooled z = 28.29, pooled z = 23.91; exact two-sided binomial p = 4.8×10⁻¹⁷⁶ (unpooled) /
2.6×10⁻¹²⁶ (pooled). Newcombe–Wald interval on the difference.

**The per-bit trace is a working feedback loop, not an anomaly.** The state after each
mid-cycle measurement is *not* re-read: bit c[k] is read directly after an R_x, so its ideal
value is cos²(θ/2) = **0.9455**; the terminal bit is read after the correction, so its ideal
value is **1.0000**. The measured terminal value being higher than the mid values is therefore
the *expected* behaviour:

| | ideal | measured |
|---|---|---|
| mid-cycle bits, mean | 0.9455 | 0.9111 |
| terminal bit c[10] | 1.0000 | **0.9720** |
| gap | **+0.0545** | **+0.0609** |

The measured bits (c[0]…c[9]): 0.903, 0.894, 0.911, 0.908, 0.921, 0.928, 0.907, 0.908, 0.923,
0.908. A terminal bit *equal* to the mid bits would indicate that the conditional branch is not
executing.

#### Preregistration status (disclosed, not corrected)

`docs/PREREGISTRATION-active_space_memory.md` §3 fixes the gate as:

> ΔF(N) = F_active(N) − F_passive(N) > 0.30 **at N ≥ 20 cycles**, two-sample binomial p < 10⁻⁶.

| gate clause | required | this run | met |
|---|---|---|---|
| effect size | Δ > 0.30 | Δ = 0.4710 | ✅ |
| significance | p < 10⁻⁶ | p < 10⁻¹⁵ | ✅ |
| **cycle count** | **N ≥ 20** | **N = 10** | ❌ |

The N = 10 result is reported as a **preliminary observation**. The preregistered gate is
tested by the N = 20 campaign specified in
`docs/PREREGISTRATION-AMENDMENT-zeno-N20.md`, which also moves the readout calibration
(`cal_1`, `cal_0`) **into the same job** — see the next subsection for why that is necessary.

#### The readout ceiling is unresolved in this run

The terminal measurement reads a state that the feedback has just restored to |1⟩, so the
readout ceiling applies to it directly. Under the daily calibration:

$$P_{\text{ceiling}} = 1 - p(0|1) = 1 - 0.0547 = \mathbf{94.53\%}$$

and generally $P_{\text{obs}} = q(1-e_1) + (1-q)e_0$. With e₁ = 0.0547, e₀ = 0.0078:

| observed | implied q = (P_obs − e₀)/(1 − e₀ − e₁) |
|---|---|
| 0.9720 | **1.0285** |

A value q > 1 is not physical. Two readings are possible, and this run cannot distinguish them:

1. **the calibration drifted** between 08:04 and 11:57 UTC (the v1.3.1 explanation, honest but
   unmeasured — no isolated |1⟩ circuit ran in the job);
2. **the register mapping or the feedback branch differs from the assumed one** (which the
   +0.0609 vs +0.0545 gap does not suggest, but does not exclude either).

**Resolution, committed:** the amendment carries `cal_1` and `cal_0` in the same job, in the
same seconds as the Zeno arms. Until that runs, the 97.20% should be quoted **with** the
ceiling, never alone.

#### N = 20 result (job `dbokrbk4148s739t68ig`, 2026-11-09 04:35 UTC)

The preregistered gate has now been tested. One job, four pubs (active N=20, passive N=20,
`cal_1`, `cal_0`), `ibm_marrakesh`, 2000 shots per pub.

| | value |
|---|---|
| Backend / qubit | `ibm_marrakesh`, physical Q0 |
| Job | `dbokrbk4148s739t68ig`, submitted 2026-11-09 04:35 UTC |
| Cycles | **N = 20** |
| Shots | 2,000 per arm |
| Readout calibration (in-job) | p(0|1) = **0.45%**, p(1|0) = **0.30%**, ceiling = **99.55%** |

| Arm | P(\|1⟩) | Shots | Wilson 95% CI |
|---|---|---|---|
| Active Zeno (N=20) | **97.45%** | 1949/2000 | [96.52%, 98.13%] |
| Passive control (N=20) | **0.10%** | 2/2000 | [0.01%, 0.36%] |
| Δ | **+97.35 pp** | +1947 | [+96.24, +98.12] pp |

Mid-cycle bits mean: **92.65%** (ideal cos²(θ/2) = 0.9455).
Terminal vs mid gap: **+0.048** (theory: +0.0545).

**Preregistration gate status: PASSED.**

| gate clause | required | N=20 run | met |
|---|---|---|---|
| effect size | Δ > 0.30 | Δ = 0.9735 | ✅ |
| significance | p < 10⁻⁶ | p < 10⁻¹⁵ | ✅ |
| **cycle count** | **N ≥ 20** | **N = 20** | ✅ |

**Readout ceiling resolved.** The in-job calibration gives p(0|1) = 0.45% (vs daily 5.47%),
so the ceiling is 99.55%. The observed 97.45% is **below the ceiling** — physically consistent.
Corrected q = (0.9745 − 0.0030) / (1 − 0.0030 − 0.0045) = **0.979** ∈ [0,1].

**Prediction vs measurement.** The pre-run Aer prediction (committed before the run,
`scripts/aer_predict.py` / `prediction.json`) used the daily calibration (5.47% readout
error) and predicted active terminal P(|1⟩) = 0.8875. The measured 0.9745 is higher because
the **actual readout error was 0.45%**, not 5.47%. The physics did not deviate — the noise
model did. This is an honest forecast error; the forecast and the measurement are both
reproducible from the committed code.

### 3.2 Two qubits — parity survival, not entanglement

| | active | passive | Δ |
|---|---|---|---|
| P(Φ⁺) after Bell-basis inversion | **33.60%** (336/1000) | **10.90%** (109/1000) | +22.70 pp |
| Wilson 95% CI | [30.74%, 36.59%] | [9.12%, 12.98%] | [+19.19, +26.21] pp |

unpooled z = 12.69, pooled z = 12.20, p = 7.1×10⁻³⁷ (unpooled) / 3.0×10⁻³⁴ (pooled). Job
`dbo6lqgou4as73b5jdag`, N = 4 cycles, Q0/Q2 data with Q1 ancilla.

**What this number is.** After inversion, P(Φ⁺) is the fraction of shots that survived in the
computational-parity subspace. It is **not** an entanglement witness:

- the passive arm is reproduced by the textbook noiseless prediction, 9.55% (measured 10.90%);
- the separability threshold for this quantity is **50%**, and the active arm is 16.40 pp below it;
- a stabiliser that protects ZZ parity does not protect the phase degree of freedom.

The correct statement is: *the loop triples the parity-subspace survival fraction and does not
produce distillable entanglement at this circuit depth.*

### 3.3 Three qubits — the GHZ arm, and where the loss actually is

Job `dbo6t18qtr0c73ae383g`, 5-basis tomography (ZZZ, XXX, XYY, YXY, YYX), 1,000 shots per
basis per arm, N = 3 cycles, 10,000 shots total.

$$F_{\text{GHZ}} = \frac{P_{000}+P_{111}}{2} + \frac{1}{8}\left(\langle XXX\rangle - \langle XYY\rangle - \langle YXY\rangle - \langle YYX\rangle\right)$$

| component | active | passive | noiseless prediction (passive) |
|---|---|---|---|
| P₀₀₀ | 51.20% | 13.80% | 13.42% |
| P₁₁₁ | 27.30% | 11.90% | 13.42% |
| population | **39.25%** | **12.85%** | 13.42% |
| ⟨XXX⟩ | −0.050 | +0.894 | **+1.000** |
| ⟨XYY⟩ | +0.104 | +0.004 | −0.024 |
| ⟨YXY⟩ | −0.004 | −0.012 | −0.024 |
| ⟨YYX⟩ | +0.060 | +0.004 | −0.024 |
| coherence Re ρ | **−2.63%** | **+11.22%** | +13.42% |
| **F_GHZ** | **36.63%** ±2.00% | **24.08%** ±1.94% | **26.84%** |

ΔF = +12.55 pp (z = 8.83, p = 1.1×10⁻¹⁸).

#### The passive arm is a textbook measurement

Six independent quantities (the full 8-outcome histogram, population, three of four correlators,
coherence and F) match a noiseless GHZ calculation with the same perturbation. The histogram
chi-square against that prediction is **4.96 on 7 degrees of freedom (p = 0.67)**. This is the
strongest positive control in the repository: the instrument measures what it claims to measure,
including the ⟨XXX⟩ = +1.000 prediction, which follows from [R_x, X] = 0 and is therefore
robust against anything that preserves the deformation.

#### The active arm's loss is implementation, not principle

v1.3.1 concluded that the ZZ loop *fundamentally* destroys phase coherence, and that
"transverse stabilizers" are *required*. That is not what the noiseless calculation says.
Applying the actual protocol — a perfect ZZ parity measurement with conditional X after each
cycle — to |GHZ₃⟩ (the 3-qubit repetition code, for which X⊗X⊗X is a stabiliser):

| N | arm | population | coherence | F_ideal | F_measured | gap |
|---|---|---|---|---|---|---|
| 3 | passive | 0.1342 | +0.1342 | **0.2684** | 0.2408 | −0.028 |
| 3 | **active** | **0.5000** | **+0.5000** | **1.0000** | **0.3663** | **−0.634** |
| 4 | passive | 0.1608 | +0.1608 | 0.3216 | — | — |
| 4 | active | 0.5000 | +0.5000 | 1.0000 | — | — |

The ZZ loop, applied to a GHZ state, is **exactly protective** in the ideal limit: it maps the
state back onto |GHZ₃⟩ and the coherence is fully recovered. The measured 0.3663 therefore
measures the cost of

- **26 native CZ gates** on the active arm vs 8 on the passive (ancilla parity extraction),
- **6 ancilla measurements** with their own readout error (Q0: p(0|1) = 5.47%),
- **16.1 µs of mid-circuit readout** = **46% of T₂ = 35.05 µs**,

not a property of the stabiliser. **A better implementation is a well-posed engineering target;
a change of stabiliser type is not required by this data.**

Reproduce: `python scripts/ghz_ideal_bound.py`.

### 3.4 Simulation benchmark (Aer, thermal noise)

T₁ = 80 µs, T₂ = 100 µs, gate 30 ns, readout 800 ns, 2,000 shots/point.

| Cycles | passive P(\|1⟩) | active P(\|1⟩) | Δ |
|---|---|---|---|
| 5 | 15.15% | 99.00% | +83.85% |
| 10 | 49.70% | 99.35% | +49.65% |
| 20 | 0.65% | 98.90% | +92.51% |
| 30 | 49.70% | 98.95% | +49.25% |

A second prediction, matched to the 2026-11-08 q0 calibration (depolarising + readout) and
committed **before** the N = 20 run, is in `scripts/aer_predict.py` / `prediction.json`:

| quantity (N = 20) | predicted |
|---|---|
| active terminal P(\|1⟩) | 0.8875 |
| active mid-cycle mean | 0.8534 |
| passive P(\|1⟩) | 0.0107 |
| Δ | 0.8767 |
| readout ceiling | 0.9470 |

---

## 4. Limitations

1. **Preregistration deviation.** The primary result ran N = 10 against a gate requiring
   N ≥ 20. Disclosed in §3.1; the amendment tests the actual gate.
2. **Readout ceiling.** The terminal P(|1⟩) exceeds the daily-calibration ceiling, and the run
   did not measure its own readout. Resolved by `cal_1`/`cal_0` in the amendment job.
3. **Metric scope.** Computational-basis retention and parity survival only. No full state
   tomography, no randomized benchmarking, and no process tomography; the GHZ fidelity is the
   five-component witness, not a full reconstruction.
4. **Depth scope.** N = 10 (1q), 4 (2q), 3 (3q). The GHZ result at N = 3 is a statement about
   this circuit depth; the ideal bound is N-independent but the implemented loss is not.
5. **Classical-feedback framing.** "Quantum Zeno dynamics" here means repeated projective
   readout plus classical feedforward on a 156-qubit chip. The measured advantage is a
   *classical control* advantage over an uncontrolled rotation. It is not a violation of
   quantum mechanics, and it is not a claim of non-demolition protection of coherence.
6. **Single device.** All hardware numbers come from `ibm_marrakesh`; no cross-device
   replication.

---

## 5. Reproducibility

```bash
python scripts/verify_paper_statistics.py     # 60/60 checks (unchanged since v1.3.1)
python scripts/ghz_ideal_bound.py             # ideal bounds of this release (new)
python scripts/aer_predict.py                 # pre-run prediction for N = 20 (new)
python scripts/extract_zeno_v2.py --demo      # analysis pipeline incl. prereg gate (new)
```

Every number in §3.1–3.3 re-derives from the raw count dictionaries in `measurement_raw/`; the
ideal bounds in §3.3 are closed-form density-matrix computations with no fitted parameters.

---

## 6. References

1. B. Misra, E. C. G. Sudarshan, *"The Zeno's paradox in quantum theory,"* J. Math. Phys. **18**, 756 (1977).
2. P. Facchi, S. Pascazio, *"Quantum Zeno dynamics,"* Phys. Rev. Lett. **89**, 080401 (2002).
3. H. M. Wiseman, G. J. Milburn, *Quantum Measurement and Control*, CUP (2009).
4. S. Krinner et al., *"Realization of real-time fault-tolerant quantum error correction,"* Nature **605**, 669 (2022).
5. IBM Quantum, *Dynamic Circuits and OpenQASM 3* (2023).
6. M. Róbert, *Pooled exploration/confirmation meta-analysis across 1,016 hardware jobs*, GitHub: `silentnoisehun/quantum-pooled-holdout` (2026).

---

## Citation

```bibtex
@software{robert2026active_space_memory,
  author    = {Róbert, Máté},
  title     = {Quantum Active Space Memory: Active Quantum Zeno Dynamics on IBM Quantum Heron Processors},
  month     = nov,
  year      = 2026,
  version   = {v1.3.2},
  publisher = {Zenodo / GitHub},
  url       = {https://github.com/silentnoisehun/quantum-active-space-memory}
}
```

## License

MIT. See `LICENSE`.
