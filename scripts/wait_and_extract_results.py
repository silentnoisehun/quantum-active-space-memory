#!/usr/bin/env python3
"""
wait_and_extract_results.py: Waits for the physical QPU job to complete on ibm_marrakesh,
extracts bitstring counts, calculates Zeno retention vs Passive control fidelity,
and saves the benchmark report.
"""

import json
import time
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
RAW_DIR = REPO / "measurement_raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

from qiskit_ibm_runtime import QiskitRuntimeService

JOB_ID = "dbo63b5t7fqc73akk78g"
KEY_FILE = Path(r"C:\Users\mater\Downloads\apikey (2) (1).json")

def monitor_job():
    print("=" * 82)
    print(f"MONITORING PHYSICAL QPU JOB: {JOB_ID} ON IBM_MARRAKESH")
    print("=" * 82)
    
    token = json.loads(KEY_FILE.read_text(encoding="utf-8"))["apikey"]
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token, instance="auto")
    job = service.job(JOB_ID)
    
    start_time = time.time()
    
    while True:
        status = job.status()
        elapsed = time.time() - start_time
        print(f"[{elapsed:5.1f}s] Job Status: {status}")
        
        if status in ["DONE", "COMPLETED"]:
            print("\n>>> QPU JOB COMPLETED SUCCESSFULLY! <<<")
            break
        elif status in ["ERROR", "CANCELLED"]:
            print(f"\nJob terminated with status: {status}")
            sys.exit(1)
            
        time.sleep(10)
        
    print("\nRetrieving SamplerV2 Results from ibm_marrakesh...")
    result = job.result()
    
    # Pub 0 is Active Zeno circuit, Pub 1 is Passive Control circuit
    pub_active = result[0]
    pub_passive = result[1]
    
    # Extract bit counts
    # For active circuit, classical register is 'c'
    counts_active = pub_active.data.c.get_counts()
    # For passive circuit, classical register is 'c_final'
    counts_passive = pub_passive.data.c_final.get_counts()
    
    total_active_shots = sum(counts_active.values())
    total_passive_shots = sum(counts_passive.values())
    
    # Active Zeno: terminal bit is the highest index (leftmost bit in bitstring)
    # Target state was |1>
    active_ones = sum(cnt for bitstr, cnt in counts_active.items() if bitstr[0] == '1')
    active_fidelity = active_ones / total_active_shots
    
    # Passive Control: single bit c_final
    passive_ones = counts_passive.get('1', 0)
    passive_fidelity = passive_ones / total_passive_shots
    
    delta = active_fidelity - passive_fidelity
    
    print("-" * 82)
    print("PHYSICAL HARDWARE EXPERIMENTAL RESULTS (IBM_MARRAKESH 156-QUBIT HERON):")
    print(f"  Active Zeno Dynamic Arm Fidelity   : {active_fidelity:6.2%} ({active_ones}/{total_active_shots} shots retained |1>)")
    print(f"  Passive Unmonitored Arm Fidelity   : {passive_fidelity:6.2%} ({passive_ones}/{total_passive_shots} shots retained |1>)")
    print(f"  NET ZENO PROTECTION DELTA          : +{delta:6.2%}")
    print("-" * 82)
    
    is_confirmed = (delta > 0.15)
    verdict = (
        "CONFIRMED ON PHYSICAL QUANTUM HARDWARE: Active Quantum Zeno dynamic feedforward "
        f"stabilizes the transmon state, yielding a +{delta:.1%} protection advantage over passive free decay."
        if is_confirmed else "UNCONFIRMED: Delta below threshold."
    )
    print(f"VERDICT: {verdict}")
    print("=" * 82)
    
    output_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "job_id": JOB_ID,
        "backend": "ibm_marrakesh",
        "active_fidelity": active_fidelity,
        "passive_fidelity": passive_fidelity,
        "zeno_delta": delta,
        "active_counts": counts_active,
        "passive_counts": counts_passive,
        "verdict": verdict
    }
    
    out_file = RAW_DIR / f"qpu_zeno_results_{JOB_ID}.json"
    out_file.write_text(json.dumps(output_data, indent=2), encoding="utf-8")
    print(f"Experimental report saved to: {out_file}")

if __name__ == "__main__":
    monitor_job()
