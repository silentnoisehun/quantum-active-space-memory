#!/usr/bin/env python3
"""
aer_predict.py — ELORE megadja, mit josol a tankonyvi QM a v2 futas negy karjara.

Ez a fajl a prereg-eloterjesztes szama: a futas ELOTT rögziti, mit varunk.
Ha a meres ettol elter, akkor van mit ertelmezni; ha nem ter el, a kapu zart.

Futtatas: python aer_predict.py   ->  prediction.json + kiiras
"""
import json, math
from pathlib import Path

from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError

import qpu_zeno_v2 as Z

N = 20
SHOTS = 4000

# a v1.3.1-ben publikalt kalibracio (q0, ibm_marrakesh, 2026-11-08)
E1 = 0.0547   # p(0|1)
E0 = 0.0078   # p(1|0)
T1_US, T2_US = 373.22, 35.05

nm = NoiseModel()
nm.add_all_qubit_quantum_error(depolarizing_error(2e-4, 1), ["rx"])
nm.add_all_qubit_quantum_error(depolarizing_error(1e-3, 1), ["x"])
nm.add_all_qubit_quantum_error(depolarizing_error(3e-4, 1), ["id"])
nm.add_all_qubit_readout_error(ReadoutError([[1 - E0, E0], [E1, 1 - E1]]))

sim = AerSimulator(noise_model=nm, seed_simulator=20261109)


def run(qc, shots=SHOTS):
    t = transpile(qc, sim, optimization_level=1)
    return sim.run(t, shots=shots).result().get_counts()


out = {"scenario": "ibm_marrakesh q0, 2026-11-08 kalibracio, depolarizing + readout modell",
       "assumptions": {"p_0_given_1": E1, "p_1_given_0": E0, "T1_us": T1_US, "T2_us": T2_US,
                       "gate_err_rx": 2e-4, "gate_err_x": 1e-3, "shots": SHOTS},
       "cycles": N}

c = run(Z.active_zeno(N)); n = sum(c.values()); L = N + 1
pos = [sum(v for k, v in c.items() if k[L - 1 - i] == "1") / n for i in range(L)]
p = run(Z.passive(N)); c1 = run(Z.cal_1()); c0 = run(Z.cal_0())

out["predicted"] = {
    "active_final_P1": pos[0],
    "active_mid_mean_P1": sum(pos[1:]) / (L - 1),
    "active_per_bit_P1": pos,
    "passive_P1": p.get("1", 0) / sum(p.values()),
    "cal_1_P1": c1.get("1", 0) / sum(c1.values()),
    "cal_0_P1": c0.get("1", 0) / sum(c0.values()),
}
out["predicted"]["delta"] = out["predicted"]["active_final_P1"] - out["predicted"]["passive_P1"]
out["predicted"]["readout_ceiling"] = out["predicted"]["cal_1_P1"]  # empirikus plafon = cal_1 arms P(1)

# ideális (zaj nelkul) referencia
out["ideal"] = {
    "mid_each_bit": math.cos(0.15 * math.pi / 2) ** 2,
    "final": 1.0,
    "passive": math.cos(N * 0.15 * math.pi / 2) ** 2,
    "note": "a vegso bit idealisan 1.0, mert a korrekcio utan mérunk",
}

# kvota-becsles: csak a meresek ideje
readout_us = 2.684
lamp = N * (readout_us + 0.06 + 0.30) + readout_us
out["qpu_cost_estimate_s"] = round(4 * SHOTS * lamp / 2 / 1e6, 2)   # durva felso becsles

Path(__file__).resolve().parent.parent.joinpath("prediction.json").write_text(
    json.dumps(out, indent=2))

print(json.dumps(out, indent=2))
print("\nEzt a fajlt tedd a prereg melle, MIELOTT barmi fut.")
