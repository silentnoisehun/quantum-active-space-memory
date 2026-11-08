#!/usr/bin/env python3
"""
ghz3_gme_hardware_runner.py: Submits 5-basis GME Entanglement Witness circuits (Active Zeno vs Passive)
to physical IBM Quantum Heron processor (ibm_marrakesh).
"""

import os
import sys
import json
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
RAW_DIR = REPO / "measurement_raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(HERE))

from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from ghz3_gme_witness_builder import build_ghz3_witness_circuits, BASES

KEY_FILE = Path(r"C:\Users\mater\Downloads\apikey (2) (1).json")

def get_service():
    token = json.loads(KEY_FILE.read_text(encoding="utf-8"))["apikey"]
    return QiskitRuntimeService(channel="ibm_quantum_platform", token=token, instance="auto")

def run_gme_experiment(backend_name="ibm_marrakesh", cycles=3, shots=1000):
    print("=" * 82)
    print("PHYSICAL HARDWARE RUNNER: 3-QUBIT GHZ GME WITNESS ON IBM_MARRAKESH")
    print("=" * 82)
    
    service = get_service()
    backend = service.backend(backend_name)
    print(f"Target Hardware Backend: {backend.name} (Qubits: {backend.num_qubits})")
    print(f"Topology: Physical Qubits [0, 1, 2, 3, 4] -> Data: [0, 2, 4] | Ancillas: [1, 3]")
    
    # 1. Build circuits for all 5 bases
    print(f"Building GHZ3 Witness Circuits (5 bases x 2 arms, Cycles N = {cycles})...")
    act_circs = build_ghz3_witness_circuits(cycles=cycles, is_active=True)
    pass_circs = build_ghz3_witness_circuits(cycles=cycles, is_active=False)
    
    # 2. Transpile for target QPU
    print("Transpiling for hardware native basis gates & 5-qubit topology...")
    pm_act = generate_preset_pass_manager(backend=backend, optimization_level=1, initial_layout=[0, 2, 4, 1, 3])
    pm_pass = generate_preset_pass_manager(backend=backend, optimization_level=1, initial_layout=[0, 2, 4])
    
    transpiled_pubs = []
    metadata_bases = []
    
    for b in BASES:
        act_isa = pm_act.run(act_circs[b])
        pass_isa = pm_pass.run(pass_circs[b])
        transpiled_pubs.append(act_isa)
        metadata_bases.append(f"act_{b}")
        transpiled_pubs.append(pass_isa)
        metadata_bases.append(f"pass_{b}")
        
    print(f"Transpiled {len(transpiled_pubs)} circuits for QPU execution.")
    
    # 3. Submit SamplerV2 Job
    print(f"Submitting GME Witness Job to {backend.name} (Shots = {shots} per pub, Total Shots = {len(transpiled_pubs)*shots})...")
    sampler = SamplerV2(mode=backend)
    job = sampler.run(transpiled_pubs, shots=shots)
    job_id = job.job_id()
    print(f"GME Witness Job successfully queued! Job ID: {job_id}")
    
    manifest = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "experiment": "3_qubit_ghz_gme_witness_zeno",
        "backend": backend.name,
        "physical_qubits": {"data": [0, 2, 4], "ancillas": [1, 3]},
        "job_id": job_id,
        "cycles": cycles,
        "shots_per_pub": shots,
        "bases_order": metadata_bases,
        "status": "QUEUED"
    }
    
    out_file = RAW_DIR / f"qpu_gme_witness_job_{job_id}.json"
    out_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Job manifest recorded to: {out_file}")
    return job_id

if __name__ == "__main__":
    import traceback
    try:
        run_gme_experiment(backend_name="ibm_marrakesh", cycles=3, shots=1000)
    except Exception as e:
        print(f"\nExecution note: {e}")
        traceback.print_exc()
