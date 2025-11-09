import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import fractional_matrix_power

def simulate_walks(N, T, x_start, x_target):
    P = np.zeros((N, N))
    for i in range(N):
        P[i, (i - 1) % N] = 0.5
        P[i, (i + 1) % N] = 0.5
    pi_0 = np.zeros(N)
    pi_0[x_start] = 1.0
    pi_T = np.linalg.matrix_power(P, T) @ pi_0
    P_CRW_target = pi_T[x_target]
    H_size = 2 * N
    H = 1/np.sqrt(2) * np.array([[1, 1], [1, -1]])
    C_total = np.kron(np.eye(N), H)
    S = np.zeros((H_size, H_size), dtype=complex)
    for x in range(N):
        idx_in = 2 * x
        idx_out = 2 * ((x - 1) % N)
        S[idx_out, idx_in] = 1.0
        idx_in = 2 * x + 1
        idx_out = 2 * ((x + 1) % N) + 1
        S[idx_out, idx_in] = 1.0
    U = S @ C_total
    psi_0 = np.zeros(H_size, dtype=complex)
    psi_0[2 * x_start] = 1.0
    U_T = np.linalg.matrix_power(U, T)
    psi_T = U_T @ psi_0
    prob_0 = np.abs(psi_T[2 * x_target])**2
    prob_1 = np.abs(psi_T[2 * x_target + 1])**2
    P_QW_target = prob_0 + prob_1
    return P_CRW_target, P_QW_target

N_NODES = 8
STEPS = 15
START_NODE = 0
TARGET_NODE = 4
P_CRW, P_QW = simulate_walks(N_NODES, STEPS, START_NODE, TARGET_NODE)
steps_range = np.arange(1, STEPS + 1)
p_crw_history = []
p_qw_history = []
for t in steps_range:
    p_crw, p_qw = simulate_walks(N_NODES, t, START_NODE, TARGET_NODE)
    p_crw_history.append(p_crw)
    p_qw_history.append(p_qw)
plt.figure(figsize=(10, 6))
plt.plot(steps_range, p_crw_history, 'r--', label='Classical Random Walk', linewidth=2)
plt.plot(steps_range, p_qw_history, 'b-', label='Quantum Walk (Hadamard Coin)', linewidth=3)
plt.xlabel('Number of Steps (T)', fontsize=12)
plt.ylabel(f'Success Probability at Node {TARGET_NODE}', fontsize=12)
plt.title(f'Target Probability on C{N_NODES} Graph (Start={START_NODE})', fontsize=14)
plt.legend(fontsize=11)
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()
print(f"\n--- Simulation Results (N={N_NODES}, T={STEPS}, Target={TARGET_NODE}) ---")
print("Classical Random Walk Success Probability: P_CRW(t=4) = {:.4f}".format(P_CRW))
print("Quantum Walk Success Probability: P_QW(t=4) = {:.4f}".format(P_QW))
print("-" * 75)
