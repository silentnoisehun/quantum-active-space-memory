#!/usr/bin/env python3
"""
ghz3_gme_witness_builder.py: Builds 3-Qubit GHZ state circuits with 4 Tomographic Witness Bases:
1. ZZZ (computational basis population: P_000, P_111)
2. XXX (H on all data qubits)
3. XYY (H on q0, Sdag+H on q1, q2)
4. YXY (Sdag+H on q0, H on q1, Sdag+H on q2)
5. YYX (Sdag+H on q0, q1, H on q2)

Calculates:
F_GHZ = (P_000 + P_111)/2 + 1/8 * (<XXX> - <XYY> - <YXY> - <YYX>)
GME confirmed if F_GHZ > 0.50.
"""

import math
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

BASES = ["ZZZ", "XXX", "XYY", "YXY", "YYX"]

def apply_basis_rotation(qc, qr, basis):
    """
    Rotates measurement basis from standard Z to the target Pauli basis.
    """
    for i, pauli in enumerate(basis):
        if pauli == "X":
            qc.h(qr[i])
        elif pauli == "Y":
            qc.sdg(qr[i])
            qc.h(qr[i])
        elif pauli == "Z":
            pass

def build_ghz3_witness_circuits(cycles=3, theta=0.15 * math.pi, is_active=True):
    """
    Builds the 5 witness circuits (ZZZ, XXX, XYY, YXY, YYX) for either Active or Passive condition.
    """
    circuits = {}
    
    for basis in BASES:
        qr_data = QuantumRegister(3, name="q")
        if is_active:
            qr_anc = QuantumRegister(2, name="a")
            cr_syn0 = ClassicalRegister(cycles, name="c_syn0")
            cr_syn1 = ClassicalRegister(cycles, name="c_syn1")
            cr_final = ClassicalRegister(3, name="c_final")
            qc = QuantumCircuit(qr_data, qr_anc, cr_syn0, cr_syn1, cr_final, name=f"ghz3_act_{basis}_N{cycles}")
        else:
            cr_final = ClassicalRegister(3, name="c_final")
            qc = QuantumCircuit(qr_data, cr_final, name=f"ghz3_pass_{basis}_N{cycles}")
            
        # 1. State preparation: |GHZ_3> = (|000> + |111>) / sqrt(2)
        qc.h(qr_data[0])
        qc.cx(qr_data[0], qr_data[1])
        qc.cx(qr_data[1], qr_data[2])
        
        # 2. Cycles of Perturbation & Zeno (if active)
        for step in range(cycles):
            qc.rx(theta, qr_data[0])
            qc.rx(theta, qr_data[1])
            qc.rx(theta, qr_data[2])
            
            if is_active:
                # S1 (Z0*Z1) on ancilla 0
                qc.reset(qr_anc[0])
                qc.cx(qr_data[0], qr_anc[0])
                qc.cx(qr_data[1], qr_anc[0])
                qc.measure(qr_anc[0], cr_syn0[step])
                
                # S2 (Z1*Z2) on ancilla 1
                qc.reset(qr_anc[1])
                qc.cx(qr_data[1], qr_anc[1])
                qc.cx(qr_data[2], qr_anc[1])
                qc.measure(qr_anc[1], cr_syn1[step])
                
                # Dynamic Feedforward
                with qc.if_test((cr_syn0[step], 1)):
                    qc.x(qr_data[0])
                with qc.if_test((cr_syn1[step], 1)):
                    qc.x(qr_data[2])
                    
        # 3. Apply Tomographic Basis Rotation
        apply_basis_rotation(qc, qr_data, basis)
        
        # 4. Terminal Measurement
        qc.measure(qr_data[0], cr_final[0])
        qc.measure(qr_data[1], cr_final[1])
        qc.measure(qr_data[2], cr_final[2])
        
        circuits[basis] = qc
        
    return circuits

if __name__ == "__main__":
    print("Testing GHZ3 Witness Builder...")
    act_circs = build_ghz3_witness_circuits(cycles=2, is_active=True)
    pass_circs = build_ghz3_witness_circuits(cycles=2, is_active=False)
    for b in BASES:
        print(f"Basis {b:3s} | Active ops: {act_circs[b].count_ops()} | Passive ops: {pass_circs[b].count_ops()}")
    print("Circuit suite generated successfully!")
