import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import expm, svd


N_QUBITS_MAXCUT = 3
N_STATES_MAXCUT = 2**N_QUBITS_MAXCUT
I2 = np.eye(2)
X = np.array([[0, 1], [1, 0]])
Z = np.array([[1, 0], [0, -1]])

def pauli_op(op, target, n_qubits):
    """Builds a multi-qubit operator (Kronecker product) for single-qubit `op` placed at `target`."""
    op_list = [I2] * n_qubits
    op_list[target] = op
    result = op_list[0]
    for op_i in op_list[1:]:
        result = np.kron(result, op_i)
    return result

def two_qubit_op(op, q, n_qubits):
    """Lift a 4x4 two-qubit operator `op` acting on qubits (q, q+1) into the full n_qubits Hilbert space."""
    if op.shape != (4, 4):
        raise ValueError("two_qubit_op expects a 4x4 operator")
    factors = []
    i = 0
    while i < n_qubits:
        if i == q:
            factors.append(op)
            i += 2
        else:
            factors.append(I2)
            i += 1
    result = factors[0]
    for f in factors[1:]:
        result = np.kron(result, f)
    return result

def build_hp():
    """Problem Hamiltonian H_P for C3 MaxCut (3 qubits)."""
    Z0Z1 = pauli_op(Z, 0, 3) @ pauli_op(Z, 1, 3)
    Z1Z2 = pauli_op(Z, 1, 3) @ pauli_op(Z, 2, 3)
    Z2Z0 = pauli_op(Z, 2, 3) @ pauli_op(Z, 0, 3)
    HP = 0.5 * (3 * np.eye(N_STATES_MAXCUT) - Z0Z1 - Z1Z2 - Z2Z0)
    return HP

def build_hm():
    """Mixing Hamiltonian H_M (3 qubits)."""
    HM = pauli_op(X, 0, 3) + pauli_op(X, 1, 3) + pauli_op(X, 2, 3)
    return HM

HP = build_hp()
HM = build_hm()
RHO_INITIAL = np.outer(np.ones(N_STATES_MAXCUT), np.ones(N_STATES_MAXCUT)) / N_STATES_MAXCUT # |+>^3 density matrix



def apply_unitary(rho, U):
    """Applies a unitary gate U to the density matrix rho: U * rho * U_dag."""
    return U @ rho @ U.conj().T

def apply_amplitude_damping(rho, p_ad, n_qubits):
    """Applies Amplitude Damping to ALL qubits sequentially."""
    rho_out = rho.copy()
    for q in range(n_qubits):
        
        K0 = np.array([[1, 0], [0, np.sqrt(1 - p_ad)]])
        K1 = np.array([[0, np.sqrt(p_ad)], [0, 0]])
        
        
        K0_op = pauli_op(K0, q, n_qubits)
        K1_op = pauli_op(K1, q, n_qubits)
        
        
        rho_out = K0_op @ rho_out @ K0_op.conj().T + K1_op @ rho_out @ K1_op.conj().T
        
    return rho_out

def apply_dephasing(rho, p_phi, n_qubits):
    """Applies Dephasing to ALL qubits sequentially."""
    rho_out = rho.copy()
    for q in range(n_qubits):
        Z_op = pauli_op(Z, q, n_qubits)
        
        rho_out = (1 - p_phi) * rho_out + p_phi * Z_op @ rho_out @ Z_op.conj().T
    return rho_out

def cost_expectation_dm(rho, H):
    """Calculates <C> = Tr(rho * H)."""
    return np.real(np.trace(rho @ H))



def simulate_noisy_qaoa(p, params, p_ad):
    """Simulates p-layer QAOA under Amplitude Damping."""
    rho = RHO_INITIAL.copy()
    gamma = params[:p]
    beta = params[p:]
    
    for k in range(p):
        
        U_P = expm(-1j * gamma[k] * HP)
        rho = apply_unitary(rho, U_P)
        
        
        rho = apply_amplitude_damping(rho, p_ad, N_QUBITS_MAXCUT)
        
        
        U_M = expm(-1j * beta[k] * HM)
        rho = apply_unitary(rho, U_M)
        
        
        if k < p - 1: 
            rho = apply_amplitude_damping(rho, p_ad, N_QUBITS_MAXCUT)
            
    return cost_expectation_dm(rho, HP)

def simulate_noisy_trotter(p, T, p_ad):
    """Simulates p-step Trotterized AQC under Amplitude Damping."""
    rho = RHO_INITIAL.copy()
    dt = T / p
    
    for k in range(1, p + 1):
        sk = k / p
        gamma_k = sk * dt      
        beta_k = (1 - sk) * dt 
        
        
        U_P = expm(-1j * gamma_k * HP)
        rho = apply_unitary(rho, U_P)
        
        
        rho = apply_amplitude_damping(rho, p_ad, N_QUBITS_MAXCUT)
        
        
        U_M = expm(-1j * beta_k * HM)
        rho = apply_unitary(rho, U_M)
        
        
        if k < p:
            rho = apply_amplitude_damping(rho, p_ad, N_QUBITS_MAXCUT)

    return cost_expectation_dm(rho, HP)


QAOA_P1_PARAMS = [0.203, 0.692]
QAOA_P2_PARAMS = [0.125, 0.444, 0.540, 0.170]
TROTTER_T = 10.0


p_ad_values = [0.00, 0.01, 0.05, 0.10]
results_a = {
    'p1_qaoa': [simulate_noisy_qaoa(1, QAOA_P1_PARAMS, p) for p in p_ad_values],
    'p2_qaoa': [simulate_noisy_qaoa(2, QAOA_P2_PARAMS, p) for p in p_ad_values],
    'p1_trotter': [simulate_noisy_trotter(1, TROTTER_T, p) for p in p_ad_values],
    'p2_trotter': [simulate_noisy_trotter(2, TROTTER_T, p) for p in p_ad_values]
}



N_QUBITS_CHAIN = 6
N_STATES_CHAIN = 2**N_QUBITS_CHAIN
N_TRAJECTORIES = 50
N_STEPS = 20

def half_chain_entropy(psi):
    """Calculates Von Neumann half-chain entanglement entropy S_A = -Tr(rho_A log2 rho_A)."""
    
    
    
    psi_reshaped = psi.reshape(2**3, 2**3)
    U, s, Vh = svd(psi_reshaped) 
    rho_a_eigenvalues = s**2
    
    
    entropy = 0
    for lam in rho_a_eigenvalues:
        if lam > 1e-12: 
            entropy -= lam * np.log2(lam)
    return entropy

def unitary_layer_chain(n_qubits):
    """Alternating layer of CZ gates (nearest neighbor). Builds the full-space unitary by lifting two-qubit CZ gates."""
    CZ = np.diag([1, 1, 1, -1])
    U_total = np.eye(2**n_qubits)

    
    for q in range(0, n_qubits - 1, 2):
        U_total = U_total @ two_qubit_op(CZ, q, n_qubits)

    
    for q in range(1, n_qubits - 1, 2):
        U_total = U_total @ two_qubit_op(CZ, q, n_qubits)

    return U_total

def random_measurement_step(psi, p_m, n_qubits):
    """Applies random projective measurement on each qubit with probability p_m."""
    
    psi_out = psi.copy()
    
    for q in range(n_qubits):
        if np.random.rand() < p_m: 
            
            
            P0 = pauli_op(np.diag([1, 0]), q, n_qubits)
            P1 = pauli_op(np.diag([0, 1]), q, n_qubits)
            
            
            prob_0 = np.real(np.vdot(psi_out, P0 @ psi_out))
            
            if np.random.rand() < prob_0:
                
                psi_out = P0 @ psi_out
            else:
                
                psi_out = P1 @ psi_out
            
            
            psi_out = psi_out / np.linalg.norm(psi_out)
            
    return psi_out

def run_entanglement_trajectory(p_m):
    """Runs one Monte Carlo trajectory for entanglement tracking."""
    psi = 1/np.sqrt(N_STATES_CHAIN) * np.ones(N_STATES_CHAIN) 
    U_CZ = unitary_layer_chain(N_QUBITS_CHAIN)
    entropy_history = []
    
    for step in range(N_STEPS):
        
        psi = U_CZ @ psi
        
        
        psi = random_measurement_step(psi, p_m, N_QUBITS_CHAIN)
        
        
        entropy_history.append(half_chain_entropy(psi))
        
    return entropy_history


p_m_values = [0.0, 0.1, 0.5, 1.0]
results_b_avg_entropy = {}
for p_m in p_m_values:
    all_trajectories = [run_entanglement_trajectory(p_m) for _ in range(N_TRAJECTORIES)]
    avg_entropy = np.mean(all_trajectories, axis=0)
    results_b_avg_entropy[p_m] = avg_entropy




def simulate_adaptive_qaoa(p_phi):
    """Simulates p=1 QAOA under Dephasing with adaptive correction on Qubit 0."""
    rho = RHO_INITIAL.copy()
    gamma = QAOA_P1_PARAMS[0]
    beta = QAOA_P1_PARAMS[1]
    
    
    U_P = expm(-1j * gamma * HP)
    rho = apply_unitary(rho, U_P)
    
    
    rho = apply_dephasing(rho, p_phi, N_QUBITS_MAXCUT)
    
    
    N_CORR_TRAJECTORIES = 100
    corrected_cost = 0
    
    
    P0_op = pauli_op(np.diag([1, 0]), 0, N_QUBITS_MAXCUT)
    P1_op = pauli_op(np.diag([0, 1]), 0, N_QUBITS_MAXCUT)
    X0_op = pauli_op(X, 0, N_QUBITS_MAXCUT)
    
    for _ in range(N_CORR_TRAJECTORIES):
        
        
        
        prob_0 = np.real(np.trace(rho @ P0_op))
        
        
        rho0_unnormalized = P0_op @ rho @ P0_op.conj().T
        rho0_normalized = rho0_unnormalized / prob_0
        
        
        
        
        prob_1 = 1 - prob_0
        rho1_unnormalized = P1_op @ rho @ P1_op.conj().T
        rho1_normalized = rho1_unnormalized / prob_1
        
        
        rho1_corrected = X0_op @ rho1_normalized @ X0_op.conj().T
        
        
        rho_after_correction = prob_0 * rho0_normalized + prob_1 * rho1_corrected
        
        
        U_M = expm(-1j * beta * HM)
        rho_final = apply_unitary(rho_after_correction, U_M)
        
        corrected_cost += cost_expectation_dm(rho_final, HP)

    return corrected_cost / N_CORR_TRAJECTORIES

def simulate_uncorrected_qaoa(p_phi):
    """Simulates p=1 QAOA under Dephasing without correction."""
    rho = RHO_INITIAL.copy()
    gamma = QAOA_P1_PARAMS[0]
    beta = QAOA_P1_PARAMS[1]
    
    
    U_P = expm(-1j * gamma * HP)
    rho = apply_unitary(rho, U_P)
    
    
    rho = apply_dephasing(rho, p_phi, N_QUBITS_MAXCUT)
    
    
    U_M = expm(-1j * beta * HM)
    rho = apply_unitary(rho, U_M)
    
    return cost_expectation_dm(rho, HP)


p_phi_values = [0.05, 0.10, 0.20]
results_c = {
    'uncorrected': [simulate_uncorrected_qaoa(p) for p in p_phi_values],
    'corrected': [simulate_adaptive_qaoa(p) for p in p_phi_values]
}

# --- Results Presentation ---
print("### ⚛️ Problem 8: Decoherence, Measurements, and Quantum Search Breakdown\n")

# Task a Results
print("#### a. QAOA under Amplitude-Damping Noise (MaxCut C3)")
print("Comparison of Expected Cut Value ⟨C⟩ (Max C_max = 2.0)\n")
print(f"{'p_AD':<8} | {'p=1 QAOA':<10} | {'p=2 QAOA':<10} | {'p=1 Trotter (T=10)':<18} | {'p=2 Trotter (T=10)':<18}")
print("-" * 75)
for i, p_ad in enumerate(p_ad_values):
    print(f"{p_ad:<8.2f} | {results_a['p1_qaoa'][i]:<10.3f} | {results_a['p2_qaoa'][i]:<10.3f} | {results_a['p1_trotter'][i]:<18.3f} | {results_a['p2_trotter'][i]:<18.3f}")

# Task b Plot
plt.figure(figsize=(10, 6))
for p_m, avg_entropy in results_b_avg_entropy.items():
    plt.plot(range(N_STEPS), avg_entropy, label=f'$p_m = {p_m}$ (N={N_QUBITS_CHAIN})')
plt.title('b. Half-Chain Entanglement Entropy vs. Time (Measurement-Induced Crossover)')
plt.xlabel('Evolution Step (Unitary + Measurement)')
plt.ylabel('Average Half-Chain Entanglement Entropy $S$')
plt.legend()
plt.grid(True)
plt.show()

# Task c Results
print("\n#### c. Adaptive Strategy under Dephasing Noise (p=1 QAOA)")
print("Simple feedback: Measure Qubit 0, apply X if outcome |1> (correct to |0>)\n")
print(f"{'p_Phi':<8} | {'QAOA w/o Correction':<20} | {'QAOA w/ Adaptive Correction':<25} | {'Improvement':<12}")
print("-" * 70)
for i, p_phi in enumerate(p_phi_values):
    uncorrected = results_c['uncorrected'][i]
    corrected = results_c['corrected'][i]
    improvement = corrected - uncorrected
    print(f"{p_phi:<8.2f} | {uncorrected:<20.4f} | {corrected:<25.4f} | {improvement:<12.4f}")
