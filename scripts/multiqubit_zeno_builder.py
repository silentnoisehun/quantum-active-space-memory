#!/usr/bin/env python3
"""
multiqubit_zeno_builder.py: Builds 2-Qubit Entangled Bell State (|Phi+>) Active Quantum Zeno Protection Circuits.

Architecture:
- Data Qubits: q0, q1
- Ancilla Qubit: a0 (connected between q0 and q1 for non-destructive parity syndrome readout)
- Target Entangled State: |Phi+> = (|00> + |11>) / sqrt(2)
- Perturbation: Simultaneous phase/bit perturbations Rx(theta) on data qubits
- Active Zeno Arm: Ancilla measures ZZ parity stabilizer P_ZZ = Z1 * Z2 via:
    q0 --*----------
         |
    q1 --|-----*----
         |     |
    a0 --X--*--X-- [Measure c_step] -> if c_step == 1: X(q0) [Dynamic restoration]
- Final Verification: Bell-basis inversion (CX(q0, q1) -> H(q0) -> Measure) where |00> indicates |Phi+> preservation.
"""

import math
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def build_multiqubit_active_zeno_circuit(cycles=5, theta=0.15 * math.pi):
    """
    Builds a 2-qubit Bell state active Zeno circuit using an ancilla parity syndrome.
    """
    qr_data = QuantumRegister(2, name="q")
    qr_anc = QuantumRegister(1, name="a")
    cr_syndrome = ClassicalRegister(cycles, name="c_syn")
    cr_final = ClassicalRegister(2, name="c_final")
    
    qc = QuantumCircuit(qr_data, qr_anc, cr_syndrome, cr_final, name=f"bell_active_zeno_N{cycles}")
    
    # 1. State preparation: Create Bell state |Phi+> = (|00> + |11>) / sqrt(2)
    qc.h(qr_data[0])
    qc.cx(qr_data[0], qr_data[1])
    
    # 2. Repeated Active Parity Zeno Cycles
    for step in range(cycles):
        # Environmental / perturbation rotation on data qubits
        qc.rx(theta, qr_data[0])
        qc.rx(theta, qr_data[1])
        
        # Non-destructive ZZ stabilizer parity measurement via ancilla
        qc.reset(qr_anc[0])
        qc.cx(qr_data[0], qr_anc[0])
        qc.cx(qr_data[1], qr_anc[0])
        qc.measure(qr_anc[0], cr_syndrome[step])
        
        # Dynamic feedforward: if parity is odd (c_syn == 1), apply corrective X on q0
        with qc.if_test((cr_syndrome[step], 1)):
            qc.x(qr_data[0])
            
    # 3. Bell-basis terminal readout
    # Invert Bell-state circuit: CX(q0, q1) -> H(q0)
    # Target state |Phi+> transforms back to |00>
    qc.cx(qr_data[0], qr_data[1])
    qc.h(qr_data[0])
    qc.measure(qr_data[0], cr_final[0])
    qc.measure(qr_data[1], cr_final[1])
    
    return qc

def build_multiqubit_passive_circuit(cycles=5, theta=0.15 * math.pi):
    """
    Builds a 2-qubit Bell state passive control circuit with identical perturbations
    without intermediate stabilizer measurement and without feedforward.
    """
    qr_data = QuantumRegister(2, name="q")
    cr_final = ClassicalRegister(2, name="c_final")
    
    qc = QuantumCircuit(qr_data, cr_final, name=f"bell_passive_control_N{cycles}")
    
    # 1. State preparation: Create Bell state |Phi+>
    qc.h(qr_data[0])
    qc.cx(qr_data[0], qr_data[1])
    
    # 2. Identical perturbations without active Zeno monitoring
    for _ in range(cycles):
        qc.rx(theta, qr_data[0])
        qc.rx(theta, qr_data[1])
        
    # 3. Bell-basis terminal readout (targets |00>)
    qc.cx(qr_data[0], qr_data[1])
    qc.h(qr_data[0])
    qc.measure(qr_data[0], cr_final[0])
    qc.measure(qr_data[1], cr_final[1])
    
    return qc

if __name__ == "__main__":
    print("Testing Multi-Qubit Bell State Dynamic Circuit Builder...")
    act_qc = build_multiqubit_active_zeno_circuit(cycles=3)
    pass_qc = build_multiqubit_passive_circuit(cycles=3)
    print(f"Active Circuit depth: {act_qc.depth()}, ops: {act_qc.count_ops()}")
    print(f"Passive Circuit depth: {pass_qc.depth()}, ops: {pass_qc.count_ops()}")
    print("Multi-Qubit Circuit construction successful!")
