#!/usr/bin/env python3
"""
zeno_circuit_builder.py: Constructs Active Quantum Zeno vs Passive Control Dynamic Circuits for IBM QPU.
Compatible with Qiskit 2.x and OpenQASM 3 Dynamic Circuits.
"""

import math
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def build_active_zeno_circuit(cycles=10, theta=0.15 * math.pi):
    """
    Builds an Active Quantum Zeno circuit with mid-circuit measurement
    and real-time feedforward restoration using Qiskit dynamic circuits.
    """
    qr = QuantumRegister(1, name="q")
    cr = ClassicalRegister(cycles + 1, name="c")
    qc = QuantumCircuit(qr, cr, name=f"active_zeno_N{cycles}")
    
    # 1. Prepare target state |1>
    qc.x(qr[0])
    
    # 2. Repeated Active Zeno Cycles
    for step in range(cycles):
        # Environmental / perturbation rotation
        qc.rx(theta, qr[0])
        
        # Mid-circuit readout (Zeno projection)
        qc.measure(qr[0], cr[step])
        
        # Dynamic feedforward correction: if collapsed to |0>, flip back to |1>
        with qc.if_test((cr[step], 0)):
            qc.x(qr[0])
            
    # 3. Final readout
    qc.measure(qr[0], cr[cycles])
    return qc

def build_passive_control_circuit(cycles=10, theta=0.15 * math.pi):
    """
    Builds a Passive Control circuit with identical perturbations
    but NO mid-circuit measurement and NO feedforward.
    """
    qr = QuantumRegister(1, name="q")
    cr = ClassicalRegister(1, name="c_final")
    qc = QuantumCircuit(qr, cr, name=f"passive_control_N{cycles}")
    
    # 1. Prepare target state |1>
    qc.x(qr[0])
    
    # 2. Identical Perturbations without active Zeno observation
    for _ in range(cycles):
        qc.rx(theta, qr[0])
        
    # 3. Terminal readout
    qc.measure(qr[0], cr[0])
    return qc

if __name__ == "__main__":
    print("Testing Dynamic Circuit Builder...")
    act_circ = build_active_zeno_circuit(cycles=5)
    pass_circ = build_passive_control_circuit(cycles=5)
    print(f"Active Circuit depth: {act_circ.depth()}, ops: {act_circ.count_ops()}")
    print(f"Passive Circuit depth: {pass_circ.depth()}, ops: {pass_circ.count_ops()}")
    print("Circuit construction successful!")
