## v1.3.1 — Verified Correction Release: Every Number Re-Derived From the Raw Data

This is a **correction release**, not a new experiment. No QPU time was consumed. Every quantitative
claim in the paper was re-derived from the committed raw files in `measurement_raw/` by a new
committed script, `scripts/verify_paper_statistics.py`, which re-computes the arm probabilities,
the Wilson confidence intervals, the Newcombe–Wald interval on the probability difference, the
unpooled and pooled two-proportion z-scores, the exact two-sided binomial p-values, and the GHZ GME
fidelity re-assembled from its five tomographic components.

```
python scripts/verify_paper_statistics.py   ->  60/60 checks passed
```

Hardware-side claims that could be checked without spending QPU time were re-measured against the
live backend (`ibm_marrakesh`): the transpiled circuit structure and the qubit-0 calibration
snapshot.

### 1. Headline results — unchanged

| Experiment | Hardware Job ID | Active Zeno | Passive Control | Net Advantage ($\Delta$) | Significance |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Single-qubit state** | `dbo63b5t7fqc73akk78g` | **97.20%** | 50.10% | **+47.10pp** | unpooled $z = 28.29$, pooled $z = 23.91$, $p < 10^{-15}$ |
| **Two-qubit Bell parity** | `dbo6lqgou4as73b5jdag` | **33.60%** | 10.90% | **+22.70pp** | unpooled $z = 12.69$, pooled $z = 12.20$, $p = 7.1\times10^{-37}$ (unpooled) |
| **Three-qubit GHZ population** | `dbo6t18qtr0c73ae383g` | **39.25%** | 12.85% | **+26.40pp** | $>3\times$ vs the 12.5% mixed floor |
| **Three-qubit GHZ fidelity** | `dbo6t18qtr0c73ae383g` | **36.62% [±2.00%]** | **24.07% [±1.94%]** | **+12.55% [±2.79%]** | unpooled $z = 8.83$, $p = 1.1\times10^{-18}$ |

No scientific conclusion changed: the GME falsification, the Bell-state arbitration and the Zeno
advantage stand exactly as published.

### 2. Corrections applied

1. **Active-arm Wilson interval.** v1.3.0 reported [95.96%, 98.08%] for 972/1,000 under the label
   "Wilson". No standard method reproduces that pair (Wilson [95.983%, 98.056%], Wilson+CC
   [95.933%, 98.106%], Agresti–Coull [95.967%, 98.071%], Clopper–Pearson [95.979%, 98.132%]). The
   published value is replaced by the Wilson value, the method named in the table and the one that
   reproduces the other three arm intervals exactly. The abstract half-width moves from ±1.02pp to
   ±1.04pp.
2. **Bell-arm p-value.** The single quoted $p = 7.6\times10^{-37}$ is replaced by the exact values:
   $7.1\times10^{-37}$ (unpooled) and $3.0\times10^{-34}$ (pooled). The unpooled z-score is
   12.69 (was 12.68).
3. **Active-arm CZ count.** "23 native CZ gates" is replaced by the re-transpiled value **26**, for
   all five tomographic bases. The circuit-depth figures of v1.3.0 describe the `ZZZ` basis only;
   the depth ranges are now given (active 59–62, passive 18–23).
4. **Passive-arm measurement count.** "0 measurements" becomes "0 mid-circuit measurements (3
   terminal readout measurements)", which is what the transpiled circuit contains.
5. **Aer table precision.** Exact simulator values replace the draft's one-decimal rounding
   (e.g. $N=5$: 15.15% / 99.00% / +83.85%). Simulation outputs unchanged.
6. **New limitation (4.4).** The readout-drift explanation for the single-qubit arm is now flagged
   explicitly as an inference from the observed survival, not a contemporaneous measurement, with
   the concrete remedy (a back-to-back calibration circuit in every Zeno job).
7. **Metadata consistency.** `README.md` BibTeX, `CITATION.cff` and `.zenodo.json` are aligned to
   v1.3.1, and the Zenodo description quotes the corrected p-value.

### 3. Newly verified against the live backend (no QPU time)

| Claim | Published | Re-measured | Status |
| :--- | :--- | :--- | :--- |
| Qubit-0 $T_1$ | 373.22 µs | 373.22 µs | ✔ |
| Qubit-0 $T_2$ | 35.05 µs | 35.05 µs | ✔ |
| Qubit-0 readout error | 3.125% | 3.125% | ✔ |
| Readout pulse duration | 2,684 ns | 2,684 ns | ✔ |
| Active arm ISA (CZ / reset / if_else) | 26 / 6 / 6 | 26 / 6 / 6 | ✔ |
| Passive arm ISA (CZ / if_else) | 8 / 0 | 8 / 0 | ✔ |

### 4. New in this release

- `docs/PAPER-v1.3.1.md` — the standalone, corrected paper (real tables, restored mathematics).
- `docs/PAPER-v1.3.1.html` — a self-contained, print-ready HTML rendering (no network, no JS).
- `scripts/verify_paper_statistics.py` — offline re-derivation of every published statistic from
  the raw measurement files; exits non-zero on any mismatch.
- Section 6 of the paper — the full verification ledger and the itemised list of corrections.

### 5. Data integrity

`measurement_raw/` was **not** modified. It remains the ground truth for every number above, and
every figure in the paper can be recomputed from it with one command.
