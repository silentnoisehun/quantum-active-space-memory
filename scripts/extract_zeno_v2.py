#!/usr/bin/env python3
"""
extract_zeno_v2.py — a qpu_zeno_v2.py job elemzese, prereg-kapuval

Harom mod:
  --job <job_id>                IBM-rol lekeri (token kell)
  --from-counts <file.json>     offline: {"active": {...}, "passive": {...},
                                "cal_1": {...}, "cal_0": {...}}  (Aer vagy mentett adat)
  --demo                        beepitett szintetikus adat (a kod tesztelesehez)

Kimenet: analysis.json + report.txt, benne a prereg dontes ES a readout-korrigalt ertek.
"""
import argparse, json, math, sys, time
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "measurement_raw"


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def bit_positions(counts, nbits):
    """Qiskit: a bitstring bal szelso karaktere = a legmagasabb indexu klasszikus bit.
    A c[cycles] (vegso meres) tehat a bal szelso karakter.
    A tarolt 'active_counts' a teljes c regiszter -> karakter i = c[cycles - i]."""
    n = sum(counts.values())
    return [sum(v for k, v in counts.items() if k[i] == "1") / n for i in range(nbits)]


def analyse(d):
    act, pas = d["active"], d["passive"]
    cal1, cal0 = d["cal_1"], d["cal_0"]

    n_act = sum(act.values()); n_pas = sum(pas.values())
    L = len(next(iter(act)))
    pos = bit_positions(act, L)
    final = pos[0]                       # bal szelso karakter = c[cycles] = VEGSO meres
    mid = sum(pos[1:]) / (L - 1)         # c[cycles-1] .. c[0]

    p_passive = pas.get("1", 0) / n_pas

    # readout hibak UGYANEBBOL a jobbol
    e1 = cal1.get("0", 0) / sum(cal1.values())      # p(0|1)
    e0 = cal0.get("1", 0) / sum(cal0.values())      # p(1|0)
    ceiling = 1 - e1
    # inverzio: p_obs = q(1-e1) + (1-q)e0
    q_corr = (final - e0) / (1 - e0 - e1) if abs(1 - e0 - e1) > 1e-9 else float("nan")

    from scipy.stats import binomtest
    pbinom = binomtest(int(round(final * n_act)), n_act, p_passive, alternative="greater").pvalue
    delta = final - p_passive

    prereg = {
        "delta_gt_0.30": bool(delta > 0.30),
        "N_ge_20": bool((L - 1) >= 20),
        "p_lt_1e-6": bool(pbinom < 1e-6),
    }
    prereg["PASSED"] = all(prereg.values())

    flags = []
    if final > ceiling + 1e-9:
        flags.append(
            f"KRITIKUS: a vegso meres ({final:.4f}) a readout-plafon FOLOTT van "
            f"({ceiling:.4f} = 1 - p(0|1) = 1 - {e1:.4f}). Ilyen jobban mert kalibracioval "
            f"ez fizikailag nem lehetseges -> a job adata vagy a regiszter-kiosztas ellenorzendo.")
    if abs(final - mid) > 0.10:
        flags.append(f"FIGYELEM: vegso ({final:.4f}) - kozbulso atlag ({mid:.4f}) = "
                     f"{final-mid:+.4f}; elmeleti maximum +{1-math.cos(0.15*math.pi/2)**2:.4f}")
    if not (0.0 <= q_corr <= 1.0):
        flags.append(f"FIGYELEM: a readout-korrigalt q = {q_corr:.4f} kiesik [0,1]-bol -> "
                     f"a kalibracios karok nem fedik a Zeno-kar readoutjat.")

    return {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cycles": L - 1, "shots_active": n_act, "shots_passive": n_pas,
        "P_final": float(final), "P_final_ci95_wilson": wilson(int(round(final * n_act)), n_act),
        "P_mid_mean": float(mid), "mid_minus_final_gap": final - mid,
        "P_passive": float(p_passive), "P_passive_ci95": wilson(pas.get("1", 0), n_pas),
        "delta": float(delta), "delta_ci95": [wilson(int(round(final*n_act)), n_act)[0] - wilson(pas.get("1",0), n_pas)[1],
                                       wilson(int(round(final*n_act)), n_act)[1] - wilson(pas.get("1",0), n_pas)[0]],
        "p_one_sided_binomial": float(pbinom),
        "readout": {"p_0_given_1": float(e1), "p_1_given_0": float(e0), "ceiling_given_cal": float(ceiling),
                    "corrected_q": float(q_corr),
                    "corrected_q_ci": [wilson(int(round(final*n_act)), n_act)[0],
                                       wilson(int(round(final*n_act)), n_act)[1]]},
        "per_bit_P1": [float(x) for x in pos],
        "prereg_gate": prereg,
        "verdict": "PREREG TELJESULT" if prereg["PASSED"] else "PREREG NEM TELJESULT",
        "flags": flags,
    }


def get_counts(a):
    if a.from_counts:
        return json.loads(Path(a.from_counts).read_text())
    if a.demo:
        # realis szintetikus adat: N=20, ~3% readout-hiba, ~95% halo
        import random; random.seed(11)
        n = 2000
        def sample(p1, n=n, f=0.045):
            c = {}
            for _ in range(n):
                b = 1 if random.random() < p1 else 0
                if random.random() < f: b ^= 1
                c[str(b)] = c.get(str(b), 0) + 1
            return c
        return {"active": {format(i, "021b"): max(1, int(2000 * math.exp(-abs(i - 380) / 90))) for i in range(21)} if False else None}
    from qiskit_ibm_runtime import QiskitRuntimeService
    import os
    api_key = os.environ.get("QISKIT_IBM_RUNTIME_API_KEY") or os.environ.get("IBM_API_KEY")
    crn = 'crn:v1:bluemix:public:quantum-computing:us-east:a/850d7f5ad80c4beab980d2b4bdec250d:38cf48ed-daeb-4efb-b709-c8c25dbbbc7a::'
    if api_key:
        svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=api_key, instance=crn)
    else:
        svc = QiskitRuntimeService(channel="ibm_quantum_platform", instance="auto")
    res = svc.job(a.job).result()
    return {"active": res[0].data.c.get_counts(),
            "passive": res[1].data.c_final.get_counts(),
            "cal_1": res[2].data.c_cal.get_counts(),
            "cal_0": res[3].data.c_cal.get_counts()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job"); ap.add_argument("--from-counts"); ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    if not (a.job or a.from_counts or a.demo):
        sys.exit("adj meg --job / --from-counts / --demo valamit")
    d = get_counts(a)
    if d is None:
        sys.exit("demo adat nem elerheto, hasznald --from-counts")

    r = analyse(d)
    tag = a.job or "local"
    out = RAW / f"zeno_v2_analysis_{tag}.json"
    out.write_text(json.dumps(r, indent=2, ensure_ascii=False))

    txt = [
        f"ASM v2 elemzes  ({r['cycles']} ciklus, {r['shots_active']} + {r['shots_passive']} loves)",
        "=" * 78,
        f"  vegso P(|1>)        = {r['P_final']:.4f}   95% CI {r['P_final_ci95_wilson'][0]:.4f}-{r['P_final_ci95_wilson'][1]:.4f}",
        f"  kozbulso atlag      = {r['P_mid_mean']:.4f}",
        f"  passziv P(|1>)      = {r['P_passive']:.4f}",
        f"  delta               = {r['delta']:+.4f}",
        f"  egyoldalu p         = {r['p_one_sided_binomial']:.3e}",
        "",
        f"  readout p(0|1)      = {r['readout']['p_0_given_1']:.4f}  (ugyanebbol a jobbol)",
        f"  readout p(1|0)      = {r['readout']['p_1_given_0']:.4f}",
        f"  plafon              = {r['readout']['ceiling_given_cal']:.4f}",
        f"  korrigalt q         = {r['readout']['corrected_q']:.4f}",
        "",
        f"  PREREG: {r['verdict']}",
        f"    delta>0.30: {r['prereg_gate']['delta_gt_0.30']}   "
        f"N>=20: {r['prereg_gate']['N_ge_20']}   p<1e-6: {r['prereg_gate']['p_lt_1e-6']}",
    ]
    if r["flags"]:
        txt += ["", "  FLAGEK:"] + [f"   - {f}" for f in r["flags"]]
    rep = RAW / f"zeno_v2_report_{tag}.txt"
    rep.write_text("\n".join(txt))
    print("\n".join(txt))
    print(f"\n-> {out}\n-> {rep}")


if __name__ == "__main__":
    main()
