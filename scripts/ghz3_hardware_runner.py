#!/usr/bin/env python3
"""
ghz3_hardware_runner.py: Submits 3-qubit entangled GHZ state active Zeno vs passive control
circuits to physical IBM Quantum Heron processor (ibm_marrakesh).
Uses 5 physical qubits: Data = [0, 2, 4], Ancillas = [1, 3].
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
from ghz3_zeno_builder import build_ghz3_active_zeno_circuit, build_ghz3_passive_circuit

KEY_FILE = Path(r"C:\Users\mater\Downloads\apikey (2) (1).json")

def get_service():
    token = json.loads(KEY_FILE.read_text(encoding="utf-8"))["apikey"]
    return QiskitRuntimeService(channel="ibm_quantum_platform", token=token, instance="auto")

def run_ghz3_hardware(backend_name="ibm_marrakesh", cycles=3, shots=1000):
    print("=" * 82)
    print("PHYSICAL HARDWARE RUNNER: 3-QUBIT GHZ STATE ACTIVE ZENO ON IBM QPU (5 QUBITS)")
    print("=" * 82)
    
    service = get_service()
    backend = service.backend(backend_name)
    print(f"Target Hardware Backend: {backend.name} (Qubits: {backend.num_qubits})")
    print(f"Topology: Physical Qubits [0, 1, 2, 3, 4] -> Data: [0, 2, 4] | Ancillas: [1, 3]")
    
    # 1. Build circuits
    print(f"Building 3-Qubit GHZ Active Zeno vs Passive Circuits (Cycles N = {cycles})...")
    act_qc = build_ghz3_active_zeno_circuit(cycles=cycles)
    pass_qc = build_ghz3_passive_circuit(cycles=cycles)
    
    # 2. Transpile for target QPU
    print("Transpiling for hardware native basis gates & 5-qubit topology...")
    # Active: 3 data + 2 ancillas -> layout maps to [0, 2, 4, 1, 3]
    pm_act = generate_preset_pass_manager(backend=backend, optimization_level=1, initial_layout=[0, 2, 4, 1, 3])
    # Passive: 3 data -> layout maps to [0, 2, 4]
    pm_pass = generate_preset_pass_manager(backend=backend, optimization_level=1, initial_layout=[0, 2, 4])
    
    act_isa = pm_act.run(act_qc)
    pass_isa = pm_pass.run(pass_qc)
    
    print(f"Active GHZ3 ISA depth: {act_isa.depth()}, ops: {act_isa.count_ops()}")
    print(f"Passive GHZ3 ISA depth: {pass_isa.depth()}, ops: {pass_isa.count_ops()}")
    
    # 3. Submit SamplerV2 Job
    print(f"Submitting 3-Qubit GHZ Job to {backend.name} (Shots = {shots})...")
    sampler = SamplerV2(mode=backend)
    job = sampler.run([act_isa, pass_isa], shots=shots)
    job_id = job.job_id()
    print(f"3-Qubit GHZ Job successfully queued! Job ID: {job_id}")
    
    manifest = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "experiment": "3_qubit_entangled_ghz_zeno",
        "backend": backend.name,
        "physical_qubits": {"data": [0, 2, 4], "ancillas": [1, 3]},
        "job_id": job_id,
        "cycles": cycles,
        "shots": shots,
        "status": "QUEUED"
    }
    
    out_file = RAW_DIR / f"qpu_ghz3_zeno_job_{job_id}.json"
    out_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Job manifest recorded to: {out_file}")
    return job_id

if __name__ == "__main__":
    import traceback
    try:
        run_ghz3_hardware(backend_name="ibm_marrakesh", cycles=3, shots=1000)
    except Exception as e:
        print(f"\nExecution note: {e}")
        traceback.print_exc()
