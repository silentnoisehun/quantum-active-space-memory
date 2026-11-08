#!/usr/bin/env python3
"""
ghz3_zeno_builder.py: Builds 3-Qubit Entangled GHZ State (|GHZ> = (|000> + |111>)/sqrt(2))
Active Quantum Zeno Protection Circuit using 2 interleaved ancilla qubits (5 physical qubits total).

Architecture on ibm_marrakesh:
- Physical layout: [0, 1, 2, 3, 4]
- Data Qubits: Q0 (q0), Q2 (q1), Q4 (q2)
- Ancilla Qubits: Q1 (a0 measures Z0*Z1), Q3 (a1 measures Z1*Z2)
- Target Entangled State: |GHZ_3> = (|000> + |111>) / sqrt(2)
- Perturbations: Simultaneous Rx(theta) rotations on all 3 data qubits
- Active Zeno: Interleaved non-destructive parity stabilizers S1 = Z0*Z1, S2 = Z1*Z2 + FPGA feedforward
- Final Verification: GHZ-basis inversion where outcome '000' confirms entanglement retention.
"""

import math
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def build_ghz3_active_zeno_circuit(cycles=3, theta=0.15 * math.pi):
    qr_data = QuantumRegister(3, name="q")
    qr_anc = QuantumRegister(2, name="a")
    cr_syn0 = ClassicalRegister(cycles, name="c_syn0")
    cr_syn1 = ClassicalRegister(cycles, name="c_syn1")
    cr_final = ClassicalRegister(3, name="c_final")
    
    qc = QuantumCircuit(qr_data, qr_anc, cr_syn0, cr_syn1, cr_final, name=f"ghz3_active_zeno_N{cycles}")
    
    # 1. Prepare GHZ state: (|000> + |111>) / sqrt(2)
    qc.h(qr_data[0])
    qc.cx(qr_data[0], qr_data[1])
    qc.cx(qr_data[1], qr_data[2])
    
    # 2. Repeated Active Parity Zeno Cycles
    for step in range(cycles):
        # Environmental perturbations on data qubits
        qc.rx(theta, qr_data[0])
        qc.rx(theta, qr_data[1])
        qc.rx(theta, qr_data[2])
        
        # Stabilizer S1 (Z0*Z1) on ancilla 0
        qc.reset(qr_anc[0])
        qc.cx(qr_data[0], qr_anc[0])
        qc.cx(qr_data[1], qr_anc[0])
        qc.measure(qr_anc[0], cr_syn0[step])
        
        # Stabilizer S2 (Z1*Z2) on ancilla 1
        qc.reset(qr_anc[1])
        qc.cx(qr_data[1], qr_anc[1])
        qc.cx(qr_data[2], qr_anc[1])
        qc.measure(qr_anc[1], cr_syn1[step])
        
        # Dynamic feedforward restoration:
        # If S1 flipped, correct q0
        with qc.if_test((cr_syn0[step], 1)):
            qc.x(qr_data[0])
        # If S2 flipped, correct q2
        with qc.if_test((cr_syn1[step], 1)):
            qc.x(qr_data[2])
            
    # 3. GHZ-basis inversion to verify target state retention (targets |000>)
    qc.cx(qr_data[1], qr_data[2])
    qc.cx(qr_data[0], qr_data[1])
    qc.h(qr_data[0])
    qc.measure(qr_data[0], cr_final[0])
    qc.measure(qr_data[1], cr_final[1])
    qc.measure(qr_data[2], cr_final[2])
    
    return qc

def build_ghz3_passive_circuit(cycles=3, theta=0.15 * math.pi):
    qr_data = QuantumRegister(3, name="q")
    cr_final = ClassicalRegister(3, name="c_final")
    
    qc = QuantumCircuit(qr_data, cr_final, name=f"ghz3_passive_control_N{cycles}")
    
    # 1. Prepare GHZ state: (|000> + |111>) / sqrt(2)
    qc.h(qr_data[0])
    qc.cx(qr_data[0], qr_data[1])
    qc.cx(qr_data[1], qr_data[2])
    
    # 2. Identical perturbations without active Zeno monitoring
    for _ in range(cycles):
        qc.rx(theta, qr_data[0])
        qc.rx(theta, qr_data[1])
        qc.rx(theta, qr_data[2])
        
    # 3. GHZ-basis inversion
    qc.cx(qr_data[1], qr_data[2])
    qc.cx(qr_data[0], qr_data[1])
    qc.h(qr_data[0])
    qc.measure(qr_data[0], cr_final[0])
    qc.measure(qr_data[1], cr_final[1])
    qc.measure(qr_data[2], cr_final[2])
    
    return qc

if __name__ == "__main__":
    print("Testing 3-Qubit GHZ State Circuit Builder...")
    act_qc = build_ghz3_active_zeno_circuit(cycles=2)
    pass_qc = build_ghz3_passive_circuit(cycles=2)
    print(f"Active GHZ3 Circuit depth: {act_qc.depth()}, ops: {act_qc.count_ops()}")
    print(f"Passive GHZ3 Circuit depth: {pass_qc.depth()}, ops: {pass_qc.count_ops()}")
    print("3-Qubit GHZ Dynamic Circuit construction successful!")
