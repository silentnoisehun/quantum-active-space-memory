#!/usr/bin/env python3
"""
qpu_zeno_v2.py — ASM korrekciós futás (prereg-konform, N=20, readout-kalibráció ugyanabban a jobban)

Miért kell újrafuttatni:
  1. A PREREGISTRATION-active_space_memory.md 3. pontja: dF > 0.30  N >= 20 ciklusnal.
     A v1.3.1 futas N=10-zel ment -> a sajat kapu nem teljesult.
  2. A 97.20% a megadott kalibracioval (p(0|1)=5.47%) aritmetikailag lehetetlen:
     a vegso meres egy idealis |1>-et mer, plafon = 1-0.0547 = 94.53%.
     -> readout-kalibracio UGYANABBAN a jobban, kozvetlenul a Zeno-karok utan.

Négy pub, EGY jobban (a kvota szempontjabol ez a legjobb):
  pub0  active_zeno  N=20 ciklus, kozbulso meresek + if_test feedforward
  pub1  passive      N=20 ciklus, kozbulso meres nelkul
  pub2  cal_1        X -> azonnali meres            (p(1|1) merese)
  pub3  cal_0        idle -> azonnali meres          (p(1|0) merese)

A kalibracios karok ugyanabban a jobban futnak, ugyanazon a qubiten, ugyanabban a
masodpercben -> nincs "calibration drift" kifogas.

Hasznalat:
  python qpu_zeno_v2.py --dry-run                 # csak build + hash, nincs kulcs
  python qpu_zeno_v2.py --submit                  # EZ KULD BE (token kell)
  python qpu_zeno_v2.py --submit --backend ibm_kingston
"""
import argparse, hashlib, json, math, os, sys, time
from pathlib import Path

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

THETA = 0.15 * math.pi
RAW = Path(__file__).resolve().parent.parent / "measurement_raw"
RAW.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------- circuitok
def active_zeno(cycles: int, theta: float = THETA):
    qr = QuantumRegister(1, "q")
    cr = ClassicalRegister(cycles + 1, "c")     # c[0..cycles-1] kozbulso, c[cycles] vegso
    qc = QuantumCircuit(qr, cr, name=f"active_zeno_N{cycles}")
    qc.x(qr[0])
    for s in range(cycles):
        qc.rx(theta, qr[0])
        qc.measure(qr[0], cr[s])
        with qc.if_test((cr[s], 0)):
            qc.x(qr[0])
    qc.measure(qr[0], cr[cycles])
    return qc


def passive(cycles: int, theta: float = THETA):
    qr = QuantumRegister(1, "q")
    cr = ClassicalRegister(1, "c_final")
    qc = QuantumCircuit(qr, cr, name=f"passive_N{cycles}")
    qc.x(qr[0])
    for _ in range(cycles):
        qc.rx(theta, qr[0])
    qc.measure(qr[0], cr[0])
    return qc


def cal_1():
    qr = QuantumRegister(1, "q"); cr = ClassicalRegister(1, "c_cal")
    qc = QuantumCircuit(qr, cr, name="cal_1")
    qc.x(qr[0]); qc.measure(qr[0], cr[0])
    return qc


def cal_0():
    qr = QuantumRegister(1, "q"); cr = ClassicalRegister(1, "c_cal")
    qc = QuantumCircuit(qr, cr, name="cal_0")
    qc.measure(qr[0], cr[0])
    return qc


def circuit_hashes(n: int):
    h = {}
    for name, qc in [("active", active_zeno(n)), ("passive", passive(n)),
                     ("cal_1", cal_1()), ("cal_0", cal_0())]:
        blob = json.dumps(qc.qasm(), sort_keys=True).encode()
        h[name] = hashlib.sha256(blob).hexdigest()
    return h


# ---------------------------------------------------------------- service
def get_service(key_filename="apikey.json"):
    from qiskit_ibm_runtime import QiskitRuntimeService
    cands = []
    if os.environ.get("IBM_API_KEY_FILE"):
        cands.append(Path(os.environ["IBM_API_KEY_FILE"]))
    home = Path(os.path.expanduser("~")) / "Downloads"
    cands += [home / key_filename, Path.cwd() / key_filename]
    for p in cands:
        if p.exists():
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                tok = d.get("apikey") or d.get("token")
                if tok:
                    return QiskitRuntimeService(channel="ibm_quantum_platform",
                                                token=tok, instance=d.get("instance", "auto"))
            except Exception:
                pass
    return QiskitRuntimeService(channel="ibm_quantum_platform", instance="auto")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--cycles", type=int, default=20)
    ap.add_argument("--shots", type=int, default=2000)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--submit", action="store_true")
    a = ap.parse_args()

    if a.cycles < 20:
        sys.exit("A prereg N >= 20 ciklust ker. Ne csokkentsd.")

    circuits = {"active": active_zeno(a.cycles), "passive": passive(a.cycles),
                "cal_1": cal_1(), "cal_0": cal_0()}
    hashes = circuit_hashes(a.cycles)
    manifest = {
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "backend": a.backend, "cycles": a.cycles, "shots": a.shots,
        "theta": THETA, "circuit_sha256": hashes,
        "prereg": "docs/PREREGISTRATION-AMENDMENT-zeno-N20.md",
        "pubs": {"0": "active", "1": "passive", "2": "cal_1", "3": "cal_0"},
        "note": "cal_1/cal_0 ugyanabban a jobban -> readout-kalibracio a futas pillanataban",
    }
    print(json.dumps(manifest, indent=2))

    if a.dry_run or not a.submit:
        p = RAW / f"zeno_v2_manifest_dry_{int(time.time())}.json"
        p.write_text(json.dumps(manifest, indent=2))
        print(f"\n[dry-run] manifest: {p}\nBekuldeshez: --submit")
        return

    from qiskit_ibm_runtime import SamplerV2
    svc = get_service()
    backend = svc.backend(a.backend)
    print(f"backend: {backend.name} ({backend.num_qubits} qubit)")

    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    isa = {k: pm.run(v) for k, v in circuits.items()}

    sampler = SamplerV2(mode=backend)
    job = sampler.run([isa["active"], isa["passive"], isa["cal_1"], isa["cal_0"]],
                      shots=a.shots)
    jid = job.job_id()
    manifest.update(job_id=jid, status="QUEUED")
    out = RAW / f"zeno_v2_job_{jid}.json"
    out.write_text(json.dumps(manifest, indent=2))
    print(f"\nJOB ID: {jid}\nmanifest: {out}\n\nKovetkezo: python extract_zeno_v2.py --job {jid}")


if __name__ == "__main__":
    main()
