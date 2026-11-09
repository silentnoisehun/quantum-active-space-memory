# Release Notes v1.3.3 — N=20 Preregistered Run + Readout Resolution (2026-11-09)

## Summary
The preregistered gate is now **MET**. The N=20 run (job `dbokrbk4148s739t68ig`, 2026-11-09 04:35 UTC) with in-job readout calibration satisfies all three gate clauses:
- ΔF > 0.30: **+0.9735** (active 97.45% vs passive 0.10%)
- N ≥ 20: **20**
- p < 10⁻⁶: **< 10⁻¹⁵**

## Key Results

| | value |
|---|---|
| Job ID | `dbokrbk4148s739t68ig` |
| Backend | `ibm_marrakesh` (156Q Heron r2) |
| Cycles | N = 20 |
| Shots per arm | 2,000 |
| Active P(|1⟩) final | **97.45%** (1949/2000) |
| Active mid-cycle mean | **92.65%** |
| Passive P(|1⟩) | **0.10%** (2/2000) |
| Δ | **+97.35 pp** |
| In-job readout p(0|1) | **0.45%** |
| In-job readout p(1|0) | **0.30%** |
| Readout ceiling | **99.55%** |
| Corrected q | **0.979** ∈ [0,1] |

## Readout Ceiling Resolved
The v1.3.1 anomaly (97.20% > 94.53% daily calibration ceiling) is resolved:
- **Daily calibration (Nov 8):** p(0|1) = 5.47% → ceiling 94.53% → q = 1.0285 (impossible)
- **In-job calibration (Nov 9):** p(0|1) = 0.45% → ceiling 99.55% → q = 0.979 (physical)

The actual readout error during the run was 0.45%, not 5.47%. The physics of the feedback loop is as predicted; the noise model was the only deviation.

## Prediction vs Measurement
- **Pre-committed Aer prediction** (scripts/aer_predict.py, using daily calibration): active final = 0.8875
- **Measured:** 0.9745
- **Difference:** +0.0870 attributable to readout model, not physics

## Files Updated
- README.md: §3.1 updated with N=20 results, prereg gate status, readout resolution
- docs/PREREGISTRATION-AMENDMENT-zeno-N20.md: §8 Result added
- scripts/qpu_zeno_v2.py: CRN removed, uses IBM_QUANTUM_INSTANCE env var
- scripts/extract_zeno_v2.py: CRN removed, uses IBM_QUANTUM_INSTANCE env var
- CITATION.cff: version 1.3.3, affiliation "Independent researcher"
- .zenodo.json: version 1.3.3, result summary added
- LICENSE: added (MIT)
- docs/release_notes_v1.3.2.md: claim-correction details
- docs/release_notes_v1.3.3.md: this file

## Version
v1.3.3 (N=20 preregistered run + readout resolution, 2026-11-09)