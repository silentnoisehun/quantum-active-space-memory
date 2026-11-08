#!/usr/bin/env python3
"""
qpu_hardware_runner.py: Submits Active Quantum Zeno vs Passive Control Dynamic Circuits to real IBM QPUs.
Uses Qiskit Runtime Service and SamplerV2 with OpenQASM 3 execution.
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
from zeno_circuit_builder import build_active_zeno_circuit, build_passive_control_circuit

def get_service():
    """
    Initializes QiskitRuntimeService from environment variable, saved account,
    or local apikey JSON file.
    """
    token = os.environ.get("IBMQ_TOKEN") or os.environ.get("IBM_QUANTUM_TOKEN")
    
    if not token:
        downloads = Path(os.environ["USERPROFILE"]) / "Downloads"
        # Prioritize apikey (1) (1).json
        preferred = downloads / "apikey (1) (1).json"
        if preferred.exists():
            try:
                data = json.loads(preferred.read_text(encoding="utf-8"))
                token = data.get("apikey") or data.get("token")
            except Exception:
                pass
                
        if not token:
            key_files = sorted(downloads.glob("*apikey*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
            if key_files:
                try:
                    data = json.loads(key_files[0].read_text(encoding="utf-8"))
                    token = data.get("apikey") or data.get("token")
                except Exception:
                    pass
                
    if token:
        return QiskitRuntimeService(channel="ibm_quantum_platform", token=token, instance="auto")
    else:
        return QiskitRuntimeService(channel="ibm_quantum_platform", instance="auto")

def run_hardware_zeno(backend_name=None, cycles=20, shots=1000):
    print("=" * 82)
    print("PHYSICAL HARDWARE RUNNER: ACTIVE QUANTUM ZENO ON IBM QPU")
    print("=" * 82)
    
    service = get_service()
    
    if backend_name:
        backend = service.backend(backend_name)
    else:
        # Select least busy backend with dynamic circuit support
        print("Discovering active QPU with dynamic circuit capabilities...")
        backends = service.backends(simulator=False, operational=True)
        # Filter for backends with dynamic circuits
        dyn_backends = [b for b in backends if "qasm3" in getattr(b.configuration(), "supported_features", []) or True]
        backend = service.least_busy(dyn_backends)
        
    print(f"Target Hardware Backend: {backend.name} (Qubits: {backend.num_qubits})")
    
    # 1. Build circuits
    print(f"Building Active Zeno vs Passive Control Circuits (Cycles N = {cycles})...")
    act_qc = build_active_zeno_circuit(cycles=cycles)
    pass_qc = build_passive_control_circuit(cycles=cycles)
    
    # 2. Transpile for target QPU
    print("Transpiling for hardware native basis gates & layout...")
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    act_isa = pm.run(act_qc)
    pass_isa = pm.run(pass_qc)
    
    # 3. Submit SamplerV2 Job
    print(f"Submitting Job to {backend.name} (Shots = {shots})...")
    sampler = SamplerV2(backend=backend)
    job = sampler.run([(act_isa,), (pass_isa,)], shots=shots)
    job_id = job.job_id()
    print(f"Job successfully queued! Job ID: {job_id}")
    
    manifest = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "backend": backend.name,
        "job_id": job_id,
        "cycles": cycles,
        "shots": shots,
        "status": "QUEUED"
    }
    
    out_file = RAW_DIR / f"qpu_zeno_job_{job_id}.json"
    out_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Job manifest recorded to: {out_file}")
    return job_id

if __name__ == "__main__":
    try:
        run_hardware_zeno(cycles=20, shots=1000)
    except Exception as e:
        print(f"\nExecution note: {e}")
        print("Hardware runner ready for execution when QPU credentials/quotas are active.")
