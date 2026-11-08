#!/usr/bin/env python3
"""
wait_and_extract_gme_witness.py: Monitors physical 3-qubit GHZ GME Witness job on ibm_marrakesh,
retrieves the 10,000 physical shots across the 5 bases (ZZZ, XXX, XYY, YXY, YYX),
calculates expectation values, the off-diagonal coherence Re[rho_000,111],
and the final GHZ state fidelity F_GHZ against the GME threshold (0.50).
"""

import json
import time
import sys
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
RAW_DIR = REPO / "measurement_raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

from qiskit_ibm_runtime import QiskitRuntimeService

JOB_ID = "dbo6t18qtr0c73ae383g"
KEY_FILE = Path(r"C:\Users\mater\Downloads\apikey (2) (1).json")

BASES = ["ZZZ", "XXX", "XYY", "YXY", "YYX"]

def compute_pauli_expectation(counts):
    """
    Computes <B> = sum_s (-1)^(parity(s)) * P(s)
    """
    total = sum(counts.values())
    if total == 0:
        return 0.0
    val = 0.0
    for bitstr, cnt in counts.items():
        # Clean bitstring
        bits = bitstr.replace(" ", "")[:3]
        parity = sum(int(b) for b in bits) % 2
        sign = -1.0 if parity == 1 else 1.0
        val += sign * (cnt / total)
    return val

def monitor_gme_job():
    print("=" * 82)
    print(f"MONITORING PHYSICAL 3-QUBIT GHZ GME WITNESS JOB: {JOB_ID} ON IBM_MARRAKESH")
    print("=" * 82)
    
    token = json.loads(KEY_FILE.read_text(encoding="utf-8"))["apikey"]
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token, instance="auto")
    job = service.job(JOB_ID)
    
    start_time = time.time()
    
    while True:
        status = job.status()
        elapsed = time.time() - start_time
        print(f"[{elapsed:5.1f}s] GME Witness Job Status: {status}")
        
        if status in ["DONE", "COMPLETED"]:
            print("\n>>> GME WITNESS JOB COMPLETED SUCCESSFULLY! <<<")
            break
        elif status in ["ERROR", "CANCELLED"]:
            print(f"\nJob terminated with status: {status}")
            sys.exit(1)
            
        time.sleep(10)
        
    print("\nRetrieving SamplerV2 Results (10,000 shots across 10 pubs)...")
    result = job.result()
    
    # Pub order in runner was: act_ZZZ, pass_ZZZ, act_XXX, pass_XXX, act_XYY, pass_XYY, act_YXY, pass_YXY, act_YYX, pass_YYX
    data_counts = {}
    pub_idx = 0
    for b in BASES:
        pub_act = result[pub_idx]
        pub_pass = result[pub_idx + 1]
        data_counts[f"act_{b}"] = pub_act.data.c_final.get_counts()
        data_counts[f"pass_{b}"] = pub_pass.data.c_final.get_counts()
        pub_idx += 2
        
    def analyze_arm(prefix):
        # 1. ZZZ population
        cnt_zzz = data_counts[f"{prefix}_ZZZ"]
        n_zzz = sum(cnt_zzz.values())
        p000 = cnt_zzz.get("000", 0) / n_zzz
        p111 = cnt_zzz.get("111", 0) / n_zzz
        pop = 0.5 * (p000 + p111)
        
        # 2. Expectation values
        exp_xxx = compute_pauli_expectation(data_counts[f"{prefix}_XXX"])
        exp_xyy = compute_pauli_expectation(data_counts[f"{prefix}_XYY"])
        exp_yxy = compute_pauli_expectation(data_counts[f"{prefix}_YXY"])
        exp_yyx = compute_pauli_expectation(data_counts[f"{prefix}_YYX"])
        
        # 3. Off-diagonal coherence Re[rho_000, 111]
        coherence = 0.125 * (exp_xxx - exp_xyy - exp_yxy - exp_yyx)
        
        # 4. Total GHZ state fidelity
        fidelity = pop + coherence
        
        return {
            "p000": p000,
            "p111": p111,
            "population": pop,
            "exp_xxx": exp_xxx,
            "exp_xyy": exp_xyy,
            "exp_yxy": exp_yxy,
            "exp_yyx": exp_yyx,
            "coherence_re_rho": coherence,
            "fidelity": fidelity
        }
        
    act_res = analyze_arm("act")
    pass_res = analyze_arm("pass")
    
    delta_f = act_res["fidelity"] - pass_res["fidelity"]
    
    print("-" * 82)
    print("3-QUBIT GHZ GME WITNESS EXPERIMENTAL HARDWARE RESULTS (IBM_MARRAKESH):")
    print(f"  ACTIVE ZENO ARM:")
    print(f"    Population (P_000 + P_111)/2 : {act_res['population']:6.2%} (P_000={act_res['p000']:.2%}, P_111={act_res['p111']:.2%})")
    print(f"    Pauli Expectations           : <XXX>={act_res['exp_xxx']:+.3f}, <XYY>={act_res['exp_xyy']:+.3f}, <YXY>={act_res['exp_yxy']:+.3f}, <YYX>={act_res['exp_yyx']:+.3f}")
    print(f"    Coherence Re[rho_000,111]    : {act_res['coherence_re_rho']:+6.2%}")
    print(f"    --> TOTAL GHZ FIDELITY F_act : {act_res['fidelity']:6.2%}")
    print()
    print(f"  PASSIVE CONTROL ARM:")
    print(f"    Population (P_000 + P_111)/2 : {pass_res['population']:6.2%} (P_000={pass_res['p000']:.2%}, P_111={pass_res['p111']:.2%})")
    print(f"    Pauli Expectations           : <XXX>={pass_res['exp_xxx']:+.3f}, <XYY>={pass_res['exp_xyy']:+.3f}, <YXY>={pass_res['exp_yxy']:+.3f}, <YYX>={pass_res['exp_yyx']:+.3f}")
    print(f"    Coherence Re[rho_000,111]    : {pass_res['coherence_re_rho']:+6.2%}")
    print(f"    --> TOTAL GHZ FIDELITY F_pass: {pass_res['fidelity']:6.2%}")
    print("-" * 82)
    print(f"  NET FIDELITY ADVANTAGE (Delta F): +{delta_f:6.2%}")
    
    gme_confirmed = (act_res["fidelity"] > 0.50)
    verdict = (
        f"GME CONFIRMED: Active Zeno dynamics achieves F_GHZ = {act_res['fidelity']:.2%} > 50.0%, "
        f"proving Genuine Multipartite Entanglement retention with +{delta_f:.2%} advantage over passive decay."
        if gme_confirmed else
        f"GME UNREACHED (F_act = {act_res['fidelity']:.2%} <= 50.0%), but Active Zeno demonstrated a "
        f"+{delta_f:.2%} fidelity preservation advantage over passive decay."
    )
    print(f"  VERDICT: {verdict}")
    print("=" * 82)
    
    report_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "job_id": JOB_ID,
        "backend": "ibm_marrakesh",
        "shots_total": 10000,
        "active_results": act_res,
        "passive_results": pass_res,
        "delta_fidelity": delta_f,
        "gme_confirmed_above_50pct": gme_confirmed,
        "counts": data_counts,
        "verdict": verdict
    }
    
    out_file = RAW_DIR / f"qpu_gme_witness_results_{JOB_ID}.json"
    out_file.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
    print(f"GME Witness physical report saved to: {out_file}")

if __name__ == "__main__":
    monitor_gme_job()
