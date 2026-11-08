#!/usr/bin/env python3
"""
multiqubit_hardware_runner.py: Submits 2-qubit Bell state active Zeno vs passive control
circuits to physical IBM Quantum Heron processor (ibm_marrakesh).
Uses initial_layout=[0, 2, 1] where q0=0, q1=2 are data qubits and a0=1 is the middle ancilla.
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
from multiqubit_zeno_builder import build_multiqubit_active_zeno_circuit, build_multiqubit_passive_circuit

KEY_FILE = Path(r"C:\Users\mater\Downloads\apikey (2) (1).json")

def get_service():
    if KEY_FILE.exists():
        token = json.loads(KEY_FILE.read_text(encoding="utf-8"))["apikey"]
        return QiskitRuntimeService(channel="ibm_quantum_platform", token=token, instance="auto")
    return QiskitRuntimeService(channel="ibm_quantum_platform", instance="auto")

def run_multiqubit_hardware(backend_name="ibm_marrakesh", cycles=4, shots=1000):
    print("=" * 82)
    print("PHYSICAL HARDWARE RUNNER: 2-QUBIT BELL STATE ACTIVE ZENO ON IBM QPU")
    print("=" * 82)
    
    service = get_service()
    backend = service.backend(backend_name)
    print(f"Target Hardware Backend: {backend.name} (Qubits: {backend.num_qubits})")
    print(f"Coupling topology: Physical Qubits [0, 1, 2] -> Data: Q0, Q2 | Ancilla: Q1")
    
    # 1. Build circuits
    print(f"Building 2-Qubit Active Zeno vs Passive Circuits (Cycles N = {cycles})...")
    act_qc = build_multiqubit_active_zeno_circuit(cycles=cycles)
    pass_qc = build_multiqubit_passive_circuit(cycles=cycles)
    
    # 2. Transpile for target QPU
    print("Transpiling for hardware native basis gates & topology...")
    # Active circuit uses 3 qubits: q0=0, q1=2, a0=1
    pm_act = generate_preset_pass_manager(backend=backend, optimization_level=1, initial_layout=[0, 2, 1])
    # Passive circuit uses 2 data qubits: q0=0, q1=2
    pm_pass = generate_preset_pass_manager(backend=backend, optimization_level=1, initial_layout=[0, 2])
    
    act_isa = pm_act.run(act_qc)
    pass_isa = pm_pass.run(pass_qc)
    
    print(f"Active ISA depth: {act_isa.depth()}, ops: {act_isa.count_ops()}")
    print(f"Passive ISA depth: {pass_isa.depth()}, ops: {pass_isa.count_ops()}")
    
    # 3. Submit SamplerV2 Job
    print(f"Submitting Multi-Qubit Job to {backend.name} (Shots = {shots})...")
    sampler = SamplerV2(mode=backend)
    job = sampler.run([act_isa, pass_isa], shots=shots)
    job_id = job.job_id()
    print(f"Multi-Qubit Job successfully queued! Job ID: {job_id}")
    
    manifest = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "experiment": "2_qubit_entangled_bell_state_zeno",
        "backend": backend.name,
        "physical_qubits": {"data_q0": 0, "data_q1": 2, "ancilla_a0": 1},
        "job_id": job_id,
        "cycles": cycles,
        "shots": shots,
        "status": "QUEUED"
    }
    
    out_file = RAW_DIR / f"qpu_multiqubit_zeno_job_{job_id}.json"
    out_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Job manifest recorded to: {out_file}")
    return job_id

if __name__ == "__main__":
    import traceback
    try:
        run_multiqubit_hardware(backend_name="ibm_marrakesh", cycles=4, shots=1000)
    except Exception as e:
        print(f"\nExecution note: {e}")
        traceback.print_exc()
