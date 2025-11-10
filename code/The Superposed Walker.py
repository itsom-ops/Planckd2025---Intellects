from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, Operator
from qiskit.circuit.library import UnitaryGate
import numpy as np
import matplotlib.pyplot as plt



def make_shift_operator(N_pos=2, direction=+1):
    """Create a 2^N x 2^N unitary that shifts |x> → |x+direction mod 2^N|."""
    dim = 2**N_pos
    U = np.zeros((dim, dim), dtype=complex)
    for i in range(dim):
        j = (i + direction) % dim
        U[j, i] = 1.0
    return UnitaryGate(U, label=f"Shift_{'R' if direction>0 else 'L'}")



def one_step_walk(qc, coin, pos, U_plus_gate, U_minus_gate):
    qc.h(coin)
    qc.barrier()
    # move left if |0>
    qc.x(coin)
    qc.append(U_minus_gate.control(1), [coin] + pos)
    qc.x(coin)
    # move right if |1>
    qc.append(U_plus_gate.control(1), [coin] + pos)
    qc.barrier()
    return qc


# --- main simulation ---
def superposed_walker(steps=3, N_pos=2):
    coin = 0
    pos = [1, 2]
    N_total = 3

    U_plus = make_shift_operator(N_pos, +1)
    U_minus = make_shift_operator(N_pos, -1)

    # binary → signed position mapping
    pos_map = {i: i if i < 2**(N_pos - 1) else i - 2**N_pos for i in range(2**N_pos)}

    # initial |x=0>⊗|0>
    qc_init = QuantumCircuit(N_total)
    state = Statevector.from_label('000')  # position=00, coin=0
    rms = []

    print("Step | Position probabilities (>1%)")
    print("-----------------------------------------")

    for t in range(1, steps + 1):
        qc = QuantumCircuit(N_total)
        qc = one_step_walk(qc, coin, pos, U_plus, U_minus)
        state = state.evolve(qc)

        # marginal probabilities on position qubits only
        probs = state.probabilities_dict(qargs=pos)
        msd = 0.0
        shown = []
        for bitstr, p in probs.items():
            idx = int(bitstr, 2)
            x = pos_map[idx]
            msd += x**2 * p
            if p > 0.01:
                shown.append(f"x={x} ({100*p:.1f}%)")

        print(f" {t:2d}  | {', '.join(shown)}")
        rms.append(np.sqrt(msd))

    # plot RMS vs t
    tvals = np.arange(1, steps + 1)
    plt.plot(tvals, rms, 'o-', label='Quantum RMS σ(t)')
    plt.plot(tvals, np.sqrt(tvals), 'r--', label='Classical √t')
    plt.xlabel('Steps (t)')
    plt.ylabel('RMS displacement σ')
    plt.title('Superposed Walker: Quantum vs Classical Spread')
    plt.legend()
    plt.grid(True)
    plt.show()

    print("\nRMS displacement:")
    for t, val in zip(tvals, rms):
        print(f"t={t}: σ={val:.4f}")
    return rms



superposed_walker(steps=3)
