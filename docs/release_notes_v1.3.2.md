# Release Notes v1.3.2 — Claim-Correction Release (2026-11-09)

## What changed and why

This is a **claim-correction** release. No new hardware was run for the headline numbers; three claims were re-examined against theory, and one of them reverses direction.

### 1. Preregistration deviation disclosed
The single-qubit experiment is governed by `docs/PREREGISTRATION-active_space_memory.md`, whose gate requires ΔF > 0.30 **at N ≥ 20 cycles**. The v1.3.1 run used **N = 10**. The effect-size and significance parts of the gate are met; the cycle-count part is not. See §3.1.

### 2. GHZ conclusion reversed
The v1.3.1 text concluded that the ZZ-based Zeno loop *fundamentally* destroys phase coherence and that transverse stabilisers are *required*. The noiseless calculation says the opposite: on |GHZ₃⟩ the ZZ loop is **exactly protective**, F_ideal = **1.0000**. The measured 0.3663 is an **implementation** loss, not a principle. See §3.3.

### 3. Bell arm re-labelled
P(Φ⁺) after Bell-basis inversion is a parity-survival probability, **not** an entanglement witness; the separability threshold for this quantity is 50%, and the active arm (33.60%) is below it. See §3.2.

### 4. "Beyond T₁" removed
The protocol lasts 10 × ~3.0 µs ≈ 30 µs, which is **8%** of T₁ = 373 µs. No statement about extending coherence beyond T₁ is made anywhere in this document. See §1.2.

The raw data are unchanged. `python scripts/verify_paper_statistics.py` still returns 60/60.

## New files added
- `scripts/ghz_ideal_bound.py` — noiseless GHZ bounds (passive 0.2684, active 1.0000)
- `scripts/aer_predict.py` — pre-run prediction for N=20
- `scripts/extract_zeno_v2.py` — analysis with prereg gate
- `scripts/qpu_zeno_v2.py` — N=20 + cal_1/cal_0 in single job
- `docs/PREREGISTRATION-AMENDMENT-zeno-N20.md` — prereg amendment

## Version
v1.3.2 (claim-correction release, 2026-11-09)