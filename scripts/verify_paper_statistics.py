#!/usr/bin/env python3
"""verify_paper_statistics.py: a paperben szereplo minden szam visszaszamolasa a nyers fajlokbol.

Nincs halozati hozzaferes, nincs QPU-fogyasztas: a measurement_raw/*.json nyers
count fajlokbol dolgozik, es a papirban kozzelt ertekekkel hasonlit.

Hasznalat:
    python scripts/verify_paper_statistics.py

Kilepesi kod: 0 = minden ellenorzes sikeres, 1 = legalabb egy eltert (a hibak a stdoutra kerulnek).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RAW = REPO / "measurement_raw"

Z = 1.959963984540054  # 95% -os ketoldali normal kvantilis


# --------------------------------------------------------------------------- #
# statisztikai segedek
# --------------------------------------------------------------------------- #
def wilson(k: int, n: int, z: float = Z) -> tuple[float, float]:
    """Wilson score interval egy aranyra."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def newcombe_wald(k1: int, n1: int, k2: int, n2: int, z: float = Z) -> tuple[float, float]:
    """Kulonbseg aranyok kozt: ujrahasznositott (pooled) hiba nélkuli szt. hiba."""
    p1, p2 = k1 / n1, k2 / n2
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    d = p1 - p2
    return (d - z * se, d + z * se)


def two_prop(k1: int, n1: int, k2: int, n2: int, pooled: bool) -> tuple[float, float]:
    """Két arany összehasonlítása: (z, ketoldali p)."""
    p1, p2 = k1 / n1, k2 / n2
    if pooled:
        p = (k1 + k2) / (n1 + n2)
        se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    else:
        se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    if se == 0:
        return 0.0, 1.0
    z = (p1 - p2) / se
    return z, math.erfc(abs(z) / math.sqrt(2))


# --------------------------------------------------------------------------- #
# ellenorzes
# --------------------------------------------------------------------------- #
class Ledger:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str, bool]] = []

    def check(self, claim: str, published: str, derived: str, ok: bool) -> None:
        self.rows.append((claim, published, derived, ok))

    def close(self, claim: str, published: float, derived: float, tol: float = 5e-4) -> None:
        self.check(claim, f"{published:.6g}", f"{derived:.6g}", abs(published - derived) <= tol)

    def report(self) -> int:
        width = max(len(r[0]) for r in self.rows) + 2
        print("=" * (width + 78))
        print("PAPIR STATISZTIKAI ELLENORZES")
        print("=" * (width + 78))
        failed = 0
        for claim, pub, der, ok in self.rows:
            flag = "OK  " if ok else "HIBA"
            if not ok:
                failed += 1
            print(f"[{flag}] {claim:<{width}} papir: {pub:<26} visszaszamolva: {der}")
        print("-" * (width + 78))
        print(f"{len(self.rows) - failed}/{len(self.rows)} ellenorzes sikeres.")
        if failed:
            print(f"HIBA: {failed} ellenorzes eltart a kozzelt ertektol.")
        return 1 if failed else 0


def read(name: str) -> dict:
    path = RAW / name
    if not path.exists():
        raise SystemExit(f"HIBA: nyers fajl nem talalhato: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    led = Ledger()

    # ---------------- 3.1 egy-kubitos Zeno ---------------- #
    d = read("qpu_zeno_results_dbo63b5t7fqc73akk78g.json")
    active_counts = d["active_counts"]
    n_active = sum(active_counts.values())
    # a mert qubit a bitstring elso karaktere (a nyers fajlban igy szerepel)
    k_active = sum(v for k, v in active_counts.items() if k[0] == "1")
    passive = d["passive_counts"]
    n_passive = sum(passive.values())
    k_passive = passive["1"]

    led.close("1-kubit aktiv P", 0.9720, k_active / n_active)
    led.close("1-kubit passziv P", 0.5010, k_passive / n_passive)
    led.close("1-kubit delta P", 0.4710, (k_active - k_passive) / n_active)
    lo, hi = wilson(k_active, n_active)
    led.close("1-kubit aktiv CI also", 0.9598, lo, tol=1e-4)
    led.close("1-kubit aktiv CI felso", 0.9806, hi, tol=1e-4)
    lo, hi = wilson(k_passive, n_passive)
    led.close("1-kubit passziv CI also", 0.4701, lo, tol=1e-4)
    led.close("1-kubit passziv CI felso", 0.5319, hi, tol=1e-4)
    lo, hi = newcombe_wald(k_active, n_active, k_passive, n_passive)
    led.close("1-kubit delta CI also", 0.4384, lo, tol=1e-4)
    led.close("1-kubit delta CI felso", 0.5036, hi, tol=1e-4)
    z_u, p_u = two_prop(k_active, n_active, k_passive, n_passive, pooled=False)
    z_p, p_p = two_prop(k_active, n_active, k_passive, n_passive, pooled=True)
    led.close("1-kubit z (unpooled)", 28.29, z_u, tol=5e-3)
    led.close("1-kubit z (pooled)", 23.91, z_p, tol=5e-3)
    led.check("1-kubit p < 1e-15", "< 1e-15", f"unpooled {p_u:.2e}, pooled {p_p:.2e}",
              p_u < 1e-15 and p_p < 1e-15)

    # ---------------- 3.2 Bell paritas ---------------- #
    b = read("qpu_multiqubit_zeno_results_dbo6lqgou4as73b5jdag.json")
    k_b_act = b["active_counts"]["00"]
    n_b_act = sum(b["active_counts"].values())
    k_b_pass = b["passive_counts"]["00"]
    n_b_pass = sum(b["passive_counts"].values())
    led.close("Bell aktiv P", 0.3360, k_b_act / n_b_act)
    led.close("Bell passziv P", 0.1090, k_b_pass / n_b_pass)
    lo, hi = wilson(k_b_act, n_b_act)
    led.close("Bell aktiv CI also", 0.3074, lo, tol=1e-4)
    led.close("Bell aktiv CI felso", 0.3659, hi, tol=1e-4)
    lo, hi = wilson(k_b_pass, n_b_pass)
    led.close("Bell passziv CI also", 0.0912, lo, tol=1e-4)
    led.close("Bell passziv CI felso", 0.1298, hi, tol=1e-4)
    lo, hi = newcombe_wald(k_b_act, n_b_act, k_b_pass, n_b_pass)
    led.close("Bell delta CI also", 0.1919, lo, tol=1e-4)
    led.close("Bell delta CI felso", 0.2621, hi, tol=1e-4)
    z_u, p_u = two_prop(k_b_act, n_b_act, k_b_pass, n_b_pass, pooled=False)
    z_p, p_p = two_prop(k_b_act, n_b_act, k_b_pass, n_b_pass, pooled=True)
    led.close("Bell z (unpooled)", 12.69, z_u, tol=5e-3)
    led.close("Bell z (pooled)", 12.20, z_p, tol=5e-3)
    led.close("Bell p (unpooled)", 7.1e-37, p_u, tol=5e-38)
    led.close("Bell p (pooled)", 3.0e-34, p_p, tol=5e-35)

    # ---------------- 3.3 GHZ GME witness ---------------- #
    g = read("qpu_gme_witness_results_dbo6t18qtr0c73ae383g.json")
    A, P = g["active_results"], g["passive_results"]
    for key, pub in (("p000", 0.512), ("p111", 0.273), ("population", 0.3925),
                     ("exp_xxx", -0.050), ("exp_xyy", 0.104), ("exp_yxy", -0.004),
                     ("exp_yyx", 0.060), ("coherence_re_rho", -0.02625),
                     ("fidelity", 0.36625)):
        led.close(f"GHZ aktiv {key}", pub, A[key], tol=1e-4)
    for key, pub in (("p000", 0.138), ("p111", 0.119), ("population", 0.1285),
                     ("exp_xxx", 0.894), ("exp_xyy", 0.004), ("exp_yxy", -0.012),
                     ("exp_yyx", 0.004), ("coherence_re_rho", 0.11225),
                     ("fidelity", 0.24075)):
        led.close(f"GHZ passziv {key}", pub, P[key], tol=1e-4)
    # a fidelitas a komponensekből is osszerakható
    f_act = (A["p000"] + A["p111"]) / 2 + (A["exp_xxx"] - A["exp_xyy"] - A["exp_yxy"] - A["exp_yyx"]) / 8
    f_pass = (P["p000"] + P["p111"]) / 2 + (P["exp_xxx"] - P["exp_xyy"] - P["exp_yxy"] - P["exp_yyx"]) / 8
    led.close("GHZ F aktiv (komponensekből)", 0.36625, f_act, tol=1e-5)
    led.close("GHZ F passziv (komponensekből)", 0.24075, f_pass, tol=1e-5)
    led.close("GHZ delta F", 0.1255, f_act - f_pass, tol=1e-5)
    led.check("GHZ GME nem igazolható (F<=50%)", "False", f"{f_act:.4%}", f_act <= 0.5)
    # a z-score a propagalt CI-ből
    se_a = (2.00 / Z) / 100
    se_p = (1.94 / Z) / 100
    se_d = math.sqrt(se_a ** 2 + se_p ** 2)
    z_ghz = (f_act - f_pass) / se_d
    p_ghz = math.erfc(abs(z_ghz) / math.sqrt(2))
    led.close("GHZ z", 8.83, z_ghz, tol=5e-3)
    led.close("GHZ p", 1.1e-18, p_ghz, tol=5e-20)

    # ---------------- 3.4 Aer szimulacio ---------------- #
    aer = {r["cycles"]: r for r in read("aer_verification_results.json")["results"]}
    for cycles, pub_p, pub_a, pub_d in (
        (5, 0.1515, 0.9900, 0.8385),
        (10, 0.4970, 0.9935, 0.4965),
        (20, 0.0065, 0.9890, 0.9825),
        (30, 0.4970, 0.9895, 0.4925),
    ):
        r = aer[cycles]
        led.close(f"Aer N={cycles} passziv", pub_p, r["passive_fidelity"], tol=1e-4)
        led.close(f"Aer N={cycles} aktiv", pub_a, r["active_fidelity"], tol=1e-4)
        led.close(f"Aer N={cycles} delta", pub_d, r["fidelity_delta"], tol=1e-4)

    return led.report()


if __name__ == "__main__":
    sys.exit(main())
