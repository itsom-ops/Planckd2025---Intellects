from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT
from qiskit_aer.primitives import Sampler
from qiskit.quantum_info import Statevector
import numpy as np
import matplotlib.pyplot as plt

# The shift_adder function is correct for a controlled QFT-based adder.

def shift_adder(qc, pos_qubits, coin_qubit, is_subtract=False):
    """
    Applies a +1 (or -1) shift to the position register, controlled by the coin qubit.
    Uses the QFT-based addition/subtraction principle.
    """
    N = len(pos_qubits)
    # Suppress deprecation warnings for clarity in final output
    import warnings
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    
    qc.append(QFT(N), pos_qubits)
    for j in range(N):
        # The shift magnitude is 2^(N-1-j) which corresponds to an angle
        angle = np.pi / (2**(N - 1 - j)) 
        if is_subtract:
            angle *= -1
        qc.cp(angle, coin_qubit, pos_qubits[j])
    qc.append(QFT(N).inverse(), pos_qubits)
    return qc

def one_step_quantum_walk(qc, pos_qubits, coin_qubit, N_pos):
    """Applies one step of the Hadamard Coin DTQW."""
    # 1. Coin Operation (Hadamard on coin qubit)
    qc.h(coin_qubit)
    qc.barrier()
    
    # 2. Controlled Shift (Step +1 if coin is |0>, Step -1 if coin is |1>)
    # The default coin state after H is |0> *then* |1> is where we want the shift to happen.
    # In standard convention: |0> -> +1 shift, |1> -> -1 shift.
    
    # Controlled +1 shift (controlled by |0> state, which is default for cp)
    qc = shift_adder(qc, pos_qubits, coin_qubit, is_subtract=False)
    qc.barrier()
    
    # Controlled -1 shift (controlled by |1> state, achieved by adding X gates)
    qc.x(coin_qubit) # Flip control to |1>
    qc = shift_adder(qc, pos_qubits, coin_qubit, is_subtract=True)
    qc.x(coin_qubit) # Flip control back
    qc.barrier()
    return qc

def compute_rms_qwalk(max_steps=5, N_pos=5):
    coin_qubit = 0
    pos_qubits = list(range(1, N_pos + 1))
    N_total = N_pos + 1
    
    # Map binary position (0 to 2^N_pos - 1) to signed position (-2^(N-1) to 2^(N-1) - 1)
    pos_map = {}
    for i in range(2**N_pos):
        pos_map[i] = i if i < 2**(N_pos - 1) else i - 2**N_pos
        
    rms_results = []
    
    # --- FIX 1: Initializing the state to |+> \otimes |0> ---
    qc_init = QuantumCircuit(N_total)
    qc_init.h(coin_qubit)
    state = Statevector(qc_init) 
    # -----------------------------------------------------------

    print("----------------------------------------------------------------------")
    print(f"Quantum Walk Position Amplitudes (N_pos={N_pos})")
    print("----------------------------------------------------------------------")
    print("Step (t) | Positions with Amplitude > 0.01")
    print("----------------------------------------------------------------------")

    for t in range(1, max_steps + 1):
        qc_step = QuantumCircuit(N_total)
        # Apply the single step walk operator to the current state
        qc_step = one_step_quantum_walk(qc_step, pos_qubits, coin_qubit, N_pos)
        state = state.evolve(qc_step)
        
        # Calculate probabilities of the position register only
        probabilities = state.probabilities_dict(qargs=pos_qubits)
        msd = 0
        active_positions = {}
        
        for pos_int, prob in probabilities.items():
            x = pos_map.get(pos_int, 0)
            msd += float(x)**2 * prob # Mean Squared Displacement
            
            if prob > 0.01:
                active_positions[x] = prob
                
        rms_t = np.sqrt(msd) # Root Mean Squared Displacement
        rms_results.append(rms_t)
        
        sorted_pos = sorted(active_positions.items(), key=lambda item: item[1], reverse=True)
        amp_str = ", ".join([f"x={p} ({100*prob:.1f}%)" for p, prob in sorted_pos[:5]])
        print(f"  {t:2}        | {amp_str}")

    print("----------------------------------------------------------------------")
    steps_array = np.arange(1, max_steps + 1)
    
    # Theoretical results for comparison
    classical_rms = np.sqrt(steps_array)
    quantum_rms_linear = steps_array * (1 / np.sqrt(2)) # Ballistic scaling factor is roughly 1/sqrt(2)

    # Plotting for visualization
    plt.figure(figsize=(10, 6))
    plt.plot(steps_array, rms_results, label='Simulated Quantum Walk RMS (σ_{RMS} ∝ N)', color='purple', linewidth=3)
    plt.plot(steps_array, classical_rms, 'r--', label='Theoretical Classical RMS (σ_{RMS} ∝ √N)', linewidth=2, alpha=0.7)
    plt.plot(steps_array, quantum_rms_linear, 'g-.', label='Theoretical Ballistic Scaling (∝ N)', linewidth=1.5, alpha=0.9)
    plt.xlabel('Number of Steps (N)', fontsize=12)
    plt.ylabel('RMS Displacement (σ_{RMS})', fontsize=12)
    plt.title('Problem 2: Quantum vs. Classical Walk Spreading', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, which='major', linestyle='-', alpha=0.5)
    plt.minorticks_on()
    plt.show()
    return steps_array, rms_results

# Execute the corrected function
steps_N, rms_sigma_q = compute_rms_qwalk(max_steps=5, N_pos=5)

print("\n--- Summary of RMS Displacement ---")
print("-" * 35)
print("Steps (N) | Quantum RMS (σᵣₘₛ)")
print("-" * 35)
for N, rms_q in zip(steps_N, rms_sigma_q):
    print(f"{N:9} | {rms_q:28.4f}")
print("-" * 35)
