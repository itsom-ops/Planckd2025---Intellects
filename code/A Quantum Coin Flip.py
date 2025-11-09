from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector
import numpy as np

def problem_1_simple_quantum_walk(num_steps=5):
    """
    Simulates Bob's walk using the Pauli-X gate as the coin.
    Position is tracked by a single qubit (0 or 1).
    """
    qc = QuantumCircuit(2, 1)
    coin_qubit = 0
    pos_qubit = 1

    print("----------------------------------------------------------------------")
    print("Problem 1: Path of the X-Coin Walk (Deterministic)")
    print("----------------------------------------------------------------------")
    print("Step (t) | Position (x) | Final State | Action")
    print("----------------------------------------------------------------------")

    state = Statevector.from_int(0, 2**2)

    for t in range(1, num_steps + 1):
        qc_step = QuantumCircuit(2)
        qc_step.x(coin_qubit)
        qc_step.cx(coin_qubit, pos_qubit)
        state = state.evolve(qc_step)

        prob_0_0 = state.probabilities()[0]
        prob_0_1 = state.probabilities()[1]
        prob_1_0 = state.probabilities()[2]
        prob_1_1 = state.probabilities()[3]

        if np.isclose(prob_0_0 + prob_1_0, 1.0):
            current_x = 0
        elif np.isclose(prob_0_1 + prob_1_1, 1.0):
            current_x = 1
        else:
            current_x = "Superposition/Error"

        action = "Right (+1)" if np.isclose(state.probabilities()[1] + state.probabilities()[3], 1.0) else "Left (-1)"

        state_vector = state.data[-1]
        print(f"   {t:2}      | {current_x:10} | {state_vector:11} | {action:8}")

    print("----------------------------------------------------------------------")
    print("\nObservation:")
    print("The walk path is a deterministic oscillation between x=0 and x=1.")
    print("This happens because the Pauli-X gate simply flips the coin at every step,")
    print("meaning the step direction is forced to alternate: Right, Left, Right, Left, ...")

problem_1_simple_quantum_walk(num_steps=5)
