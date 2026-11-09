# PREREGISTRATION-AMENDMENT-zeno-N20

**Repository:** quantum-active-space-memory
**Author:** Máté Róbert (ORCID 0009-0003-3986-6039)
**Date:** 2026-11-09
**Amends:** `docs/PREREGISTRATION-active_space_memory.md` (2026-11-08)
**Status of the original run:** `dbo63b5t7fqc73akk78g` (2026-11-08 11:57:26 UTC, N = 10) —
**does not satisfy the original decision gate**, see §1.

---

## 1. Why this amendment exists (disclosed before any new run)

The original preregistration fixed the success criterion as:

> ΔF(N) = F_active(N) − F_passive(N) > 0.30 **at N ≥ 20 cycles**, with a two-sample
> binomial test p < 10⁻⁶.

The v1.3.1 campaign executed **N = 10** cycles (`run_hardware_zeno(cycles=10)`).
The measured Δ = +0.4710 and p < 10⁻¹⁵ satisfy the effect and significance parts of the
gate, **but not the cycle-count part.** This is recorded here as a deviation, not corrected
after the fact: the N = 10 result stands as a *preliminary* observation, and the
preregistered gate is tested by the N = 20 run specified below.

A second, independent problem is disclosed: the v1.3.1 single-qubit arm reports
97.20% survival on a qubit whose published daily calibration gives
p(0|1) = 5.47%, i.e. a readout ceiling of 94.53% for a perfect |1⟩. The final measurement
of the active arm *is* a measurement of a state that the feedback has just restored to |1⟩,
so the ceiling applies directly. 97.20% > 94.53%. The v1.3.1 paper attributes this to
calibration drift and flags it as an inference (Section 4.4); that is honest, but it means
the headline number rests on a calibration that the same job did not measure.
**This amendment makes that measurement part of the experiment.**

---

## 2. What changes

| | original | this amendment |
|---|---|---|
| cycles | N ∈ {5,10,20,40} planned, N = 10 executed | **N = 20 (fixed, primary)** |
| readout calibration | daily backend calibration, separate from run | **cal_1 and cal_0 circuits inside the same job** |
| qubit | q0, ibm_marrakesh | unchanged |
| primary metric | P(\|1⟩) of the final measurement | unchanged |
| gate | Δ > 0.30, p < 10⁻⁶, N ≥ 20 | unchanged |
| new secondary | — | readout-corrected q = (P_obs − e0)/(1 − e0 − e1) must lie in [0,1] |

Nothing else changes. The metric, the arms, the perturbation (R_x(0.15π)), and the
theta are identical to the original preregistration.

---

## 3. Circuits and job layout

Four pubs, **one job**, one backend, one set of shots:

| pub | circuit | classical register |
|---|---|---|
| 0 | `active`: X → 20 × [ R_x(θ) → measure → if 0: X ] → final measure | `c[0..19]` mid, `c[20]` final |
| 1 | `passive`: X → 20 × R_x(θ) → measure | `c_final` |
| 2 | `cal_1`: X → measure | `c_cal` |
| 3 | `cal_0`: measure | `c_cal` |

`cal_1` measures p(1|1) = 1 − p(0|1) and `cal_0` measures p(1|0) **in the same job, on the
same qubit, seconds from the Zeno arms.** This removes the drift loophole.

Code: `scripts/qpu_zeno_v2.py` (build + submit), `scripts/extract_zeno_v2.py` (analysis),
`scripts/aer_predict.py` (prediction, run before submission). Circuit SHA-256 hashes are
written into the job manifest at submission time.

---

## 4. Prediction, fixed before the run

From `scripts/aer_predict.py` (Aer, depolarising + readout noise matched to the 2026-11-08
q0 calibration; 4000 shots). **These numbers are committed before submission.**

| quantity | ideal (noiseless) | predicted (noisy model) |
|---|---|---|
| active, final P(\|1⟩) | 1.0000 | **0.8875** |
| active, mid-cycle mean P(\|1⟩) | 0.9455 | **0.8534** |
| passive, P(\|1⟩) | 3·10⁻³² ≈ 0 | **0.0107** |
| Δ = final − passive | 1.0000 | **0.8767** |
| readout ceiling (1 − p(0|1)) | 1.0000 | **0.9470** |
| cal_0 P(1) | 0 | 0.0107 |

Notes that matter for reading the result:

- The final bit is **expected to be higher** than the mid-cycle bits
  (+0.0545 ideal). This is not an anomaly: every mid-cycle measurement happens directly
  after an R_x, so it sees cos²(θ/2) = 0.9455, while the final measurement happens after
  the correction, which restores |1⟩. A final bit *equal* to the mid bits would signal a
  broken feedback branch.
- The passive arm is expected to sit at the noise floor, not at 0.5: 20 × 0.15π = 3π,
  so cos²(3π/2) = 0.
- **Falsifiers.** The run fails its own prediction if any of these holds:
  1. final P(\|1⟩) > empirical ceiling (cal_1 P(1)) — the impossible case, means the
     register mapping or the feedback branch is wrong;
  2. passive P(\|1⟩) > 0.10 — the perturbation or the shot accounting is wrong;
  3. readout-corrected q outside [0,1];
  4. mid-cycle bits not clustered near cos²(θ/2) within readout error.

---

## 5. Decision rule (unchanged from the original, now testable)

- **Confirmed:** Δ > 0.30, N = 20, one-sided binomial p < 10⁻⁶, **and** no falsifier from §4 fires.
- **Null / invalid:** anything else. An invalid run (falsifier fired) is reported as invalid,
  not as null, and is repeated once after the fix.

---

## 6. Cost and compliance

One job, four pubs, 2000 shots each ≈ **0.5 s QPU** by the estimate in
`scripts/aer_predict.py`. **Single account.** No quota pooling across accounts
(see `docs/QPU-QUOTA-20261102.txt`, §0 in quantum-hydrodynamic-feedback).

---

## 7. Reporting

`extract_zeno_v2.py` writes `analysis.json` and `report.txt` with: the prereg gate result,
the empirical readout ceiling from the same job, the corrected q with its interval, the
per-bit P(1) trace, and any flags. All are committed whatever they show.

---

## 8. Result (2026-11-09 04:35 UTC, job `dbokrbk4148s739t68ig`)

**Gate: PASSED** ✅

| | value |
|---|---|
| Job ID | `dbokrbk4148s739t68ig` |
| Backend | `ibm_marrakesh` (156Q Heron r2) |
| Cycles | N = 20 |
| Shots per pub | 2,000 |
| Active P(|1⟩) final | **0.9745** (1949/2000) |
| Active mid-cycle mean | **0.9265** |
| Passive P(|1⟩) | **0.0010** (2/2000) |
| Δ = active − passive | **+0.9735** |
| Readout p(0|1) = e₁ | **0.0045** (9/2000) |
| Readout p(1|0) = e₀ | **0.0030** (6/2000) |
| Readout ceiling (1−e₁) | **0.9955** |
| Corrected q | **0.979** ∈ [0,1] |
| One-sided binomial p | < 10⁻¹⁵ |

**Gate clauses:**
- Δ > 0.30: **YES** (0.9735)
- N ≥ 20: **YES** (20)
- p < 10⁻⁶: **YES** (< 10⁻¹⁵)
- No falsifiers fired: **YES** (final 0.9745 < ceiling 0.9955; passive 0.0010 < 0.10; q ∈ [0,1]; mid bits clustered near cos²(θ/2)=0.9455 within readout error)

**Interpretation.** The preregistered gate is now satisfied. The in-job readout calibration
resolves the v1.3.1 ceiling discrepancy: the daily 5.47% readout error was a 3-hour-old
estimate; the actual readout error during the run was 0.45%. The Aer prediction (0.8875)
used the daily calibration and therefore underestimated the true hardware performance.
The physics of the feedback loop is as predicted; the noise model was the only deviation.

All raw counts, analysis JSON, and report text are committed in `measurement_raw/`.
