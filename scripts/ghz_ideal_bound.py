#!/usr/bin/env python3
"""
ghz_ideal_bound.py — a GHZ-karok ZAJ NELKULI hatarértékei

Ez a fajl a v1.3.2 legfontosabb új szama: megmutatja, mit tenne a protokoll
TOKELETES meres es korrekcio mellett. Ha a meres ettol messze van, akkor a
veszteseg implementacios, nem elvi.

Eredmeny (N=3, R_x(0.15pi) mindharom qubiten, ciklusonkent):
  passive:  F = 0.2684   <- ezt a meres 0.2408-cal reprodukalja
  active:   F = 1.0000   <- ezt a meres 0.3663-cal NEM reprodukalja

MIERT 1.0 az aktív kar? Mert a harom qubites ismetlesi kod (repetition code)
a |GHZ3> allapotra PONTOSAN zar: minden Pauli-X hiba-szektor, a ket paritas-
meres utan, ugyanabba a |GHZ3>-ba korrigalhato, mert X(x)X(x)X = X^3 ~ stabilizer
a GHZ-n (X^3|GHZ> = |GHZ>). Igy a ZZ-hurok NEM rontja el a faziskoherenciat
elvileg — a meresi veszteseg az ancilla-meres, a 26 CZ-kapu es a 16.1 us
mid-circuit T2-dephasing hibajabol jon.

Futtatas: python ghz_ideal_bound.py
"""
import math
import numpy as np

TH = 0.15 * math.pi
I2 = np.eye(2)
RX = np.array([[math.cos(TH / 2), -1j * math.sin(TH / 2)],
               [-1j * math.sin(TH / 2), math.cos(TH / 2)]])
H = np.array([[1, 1], [1, -1]]) / math.sqrt(2)
SD = np.array([[1, 0], [0, 1j]])
U3 = np.kron(np.kron(RX, RX), RX)


def op3(a, b, c):
    return np.kron(np.kron(a, b), c)


def kron_list(ops):
    M = np.eye(1)
    for o in ops:
        M = np.kron(M, o)
    return M


Z = np.diag([1, -1])
X = np.array([[0, 1], [1, 0]])


def parity_projectors(i, j):
    zs = [Z if q in (i, j) else I2 for q in range(3)]
    M = kron_list(zs)
    P = (np.eye(8) + M) / 2
    return P, np.eye(8) - P


P51, P51m = parity_projectors(0, 1)
P52, P52m = parity_projectors(1, 2)
X0 = kron_list([X, I2, I2])
X2 = kron_list([I2, I2, X])


def ghz_rho():
    g = np.zeros(8, complex)
    g[0] = g[7] = 1 / math.sqrt(2)
    return np.outer(g, g.conj())


def basis_matrix(s):
    return kron_list([{'X': H, 'Y': H @ SD, 'Z': I2}[c] for c in s])


PARITY = np.array([(-1) ** bin(i).count('1') for i in range(8)])


def components(rho):
    p = np.real(np.diag(rho))
    pop = (p[0] + p[7]) / 2
    es = {}
    for s in ("XXX", "XYY", "YXY", "YYX"):
        B = basis_matrix(s)
        d = np.real(np.diag(B @ rho @ B.conj().T))
        es[s] = float(np.dot(PARITY, d))
    coh = (es["XXX"] - es["XYY"] - es["YXY"] - es["YYX"]) / 8
    return pop, coh, pop + coh, es


def run_passive(n):
    rho = ghz_rho()
    for _ in range(n):
        rho = U3 @ rho @ U3.conj().T
    return rho


def run_active(n):
    """Idealis ZZ-szindroma-meres + X-korrekcio ciklusonkent (ancilla hibak nelkul)."""
    rho = ghz_rho()
    for _ in range(n):
        rho = U3 @ rho @ U3.conj().T
        rho = P51 @ rho @ P51.conj().T + X0 @ (P51m @ rho @ P51m.conj().T) @ X0.conj().T
        rho = P52 @ rho @ P52.conj().T + X2 @ (P52m @ rho @ P52m.conj().T) @ X2.conj().T
    return rho


MEASURED = {
    ("passive", 3): dict(pop=0.1285, coh=0.11225, F=0.24075,
                         eXX=0.894, eXYY=0.004, eYXY=-0.012, eYYX=0.004),
    ("active", 3): dict(pop=0.3925, coh=-0.02625, F=0.36625,
                        eXX=-0.050, eXYY=0.104, eYXY=-0.004, eYYX=0.060),
}

print("GHZ3 karok — ZAJ NELKULI hatar (R_x(0.15pi), idealis ZZ-meres + korrekcio)")
print("=" * 86)
print(f"{'N':>3} {'arm':>8} {'pop':>8} {'coh':>9} {'F_ideal':>9}   {'F_measured':>10} {'gap':>8}")
for n in (3, 4):
    for arm, fn in (("passive", run_passive), ("active", run_active)):
        pop, coh, F, es = components(fn(n))
        m = MEASURED.get((arm, n))
        if m:
            print(f"{n:>3} {arm:>8} {pop:8.4f} {coh:+9.4f} {F:9.4f}   {m['F']:10.4f} {m['F']-F:+8.4f}")
        else:
            print(f"{n:>3} {arm:>8} {pop:8.4f} {coh:+9.4f} {F:9.4f}   {'-':>10} {'-':>8}")

print()
print("Reszletek (N=3):")
for arm, fn in (("passive", run_passive), ("active", run_active)):
    pop, coh, F, es = components(fn(3))
    print(f"  {arm:>8}: pop={pop:.4f} coh={coh:+.4f} F={F:.4f} | "
          f"<XXX>={es['XXX']:+.3f} <XYY>={es['XYY']:+.3f} "
          f"<YXY>={es['YXY']:+.3f} <YYX>={es['YYX']:+.3f}")

print()
print("ERTELMEZES")
print("  passzív: ideal 0.2684 vs mert 0.2408 -> a kar a tankonyvi joslatot adja (zajjal).")
print("  aktív  : ideal 1.0000 vs mert 0.3663 -> a veszteseg IMPLEMENTACIOS.")
print("  Kovetkezmeny: a v1.3.1 azon allitasa, hogy a ZZ-hurok 'fundamentalisan'")
print("  elrontja a faziskoherenciat, es hogy ehhez 'transzverzalis stabilizer kell',")
print("  a zaj nelkuli szamitas szerint NEM all: a ZZ-hurok idealisan pontosan tartja")
print("  a GHZ-t. Amit javitani kell: ancilla-meres hibaja, CZ-szam (26), es a")
print("  16.1 us mid-circuit readout alatti T2-dephasing (a T2 = 35.05 us 46%-a).")
