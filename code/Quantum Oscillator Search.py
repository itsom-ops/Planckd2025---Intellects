import numpy as np
import matplotlib.pyplot as plt

def create_operators(N_max):
    H_size = 2 * N_max
    H = 1/np.sqrt(2) * np.array([[1, 1], [1, -1]])
    C_total = np.kron(np.eye(N_max), H)
    S = np.zeros((H_size, H_size), dtype=complex)
    for n in range(N_max):
        if n + 1 < N_max:
            idx_in_0 = 2 * n
            idx_out_0 = 2 * (n + 1)
            S[idx_out_0, idx_in_0] = np.sqrt(n + 1)
        if n - 1 >= 0:
            idx_in_1 = 2 * n + 1
            idx_out_1 = 2 * (n - 1) + 1
            S[idx_out_1, idx_in_1] = np.sqrt(n)
    U_step = S @ C_total
    return U_step, N_max

def phase_potential(N_max, alpha, phi_type='linear'):
    U_V = np.eye(2 * N_max, dtype=complex)
    for n in range(N_max):
        if phi_type == 'linear':
            phi_n = alpha * n
        elif phi_type == 'quadratic':
            phi_n = alpha * n**2
        else:
            phi_n = 0
        U_V[2 * n, 2 * n] = np.exp(1j * phi_n)
        U_V[2 * n + 1, 2 * n + 1] = np.exp(1j * phi_n)
    return U_V

def simulate_qho_walk(U_step, N_max, T_max, potential_type=None, alpha=0):
    H_size = 2 * N_max
    psi = np.zeros(H_size, dtype=complex)
    psi[0] = 1.0
    U_V = phase_potential(N_max, alpha, potential_type)
    U_total = U_step @ U_V
    P_nt = np.zeros((T_max + 1, N_max))
    RMS_t = np.zeros(T_max + 1)
    P_nt[0, 0] = 1.0
    for t in range(1, T_max + 1):
        psi = U_total @ psi
        msd = 0
        for n in range(N_max):
            prob_n = np.abs(psi[2 * n])**2 + np.abs(psi[2 * n + 1])**2
            P_nt[t, n] = prob_n
            msd += n**2 * prob_n
        RMS_t[t] = np.sqrt(msd)
    return P_nt, RMS_t

N_MAX = 15
T_MAX = 15
ALPHA = 1.0
U_step_base, _ = create_operators(N_MAX)
P_base, RMS_base = simulate_qho_walk(U_step_base, N_MAX, T_MAX, potential_type=None)
P_linear, RMS_linear = simulate_qho_walk(U_step_base, N_MAX, T_MAX, potential_type='linear', alpha=ALPHA)
P_quad, RMS_quad = simulate_qho_walk(U_step_base, N_MAX, T_MAX, potential_type='quadratic', alpha=ALPHA)

print("--- Problem 4: Quantum Oscillator Walk Amplitudes (t=1, 2, 3) ---")
psi_1 = U_step_base @ np.array([1.] + [0.] * (2*N_MAX - 1))
psi_2 = U_step_base @ psi_1
psi_3 = U_step_base @ psi_2

def print_dominant_state(psi, t):
    indices = np.where(np.abs(psi)**2 > 0.01)[0]
    states = [f"|{idx//2}, {idx%2}> ({np.abs(psi[idx])**2:.2f})" for idx in indices]
    print(f"t={t}: P(n, t) -> {', '.join([f'n={n} ({P_base[t, n]:.2f})' for n in range(N_MAX) if P_base[t, n] > 0.01])}")

print_dominant_state(psi_1, 1)
print_dominant_state(psi_2, 2)
print_dominant_state(psi_3, 3)
print("-" * 60)

steps = np.arange(T_MAX + 1)
CRW_RMS = np.sqrt(steps)

print("\n--- RMS Energy Level Scaling Comparison (Task c & d) ---")
print("Steps (t) | QW Base RMS | CRW Diffusive (sqrt(t)) | QW Quad. Potential RMS")
print("-" * 100)
for t in range(1, T_MAX + 1):
    print(f"{t:9} | {RMS_base[t]:11.4f} | {CRW_RMS[t]:25.4f} | {RMS_quad[t]:44.4f}")
print("-" * 100)

fig, axes = plt.subplots(1, 2, figsize=(18, 6))
im = axes[0].imshow(P_base.T, aspect='auto', origin='lower', extent=[0, T_MAX, 0, N_MAX-1], cmap='viridis')
axes[0].set_title('Probability Distribution P(n, t) (Base QW)', fontsize=14)
axes[0].set_xlabel('Time Steps (t)', fontsize=12)
axes[0].set_ylabel('Energy Level (n)', fontsize=12)
fig.colorbar(im, ax=axes[0], label='Probability P(n, t)')
axes[1].plot(steps, RMS_base, 'b-', label='QW Base (∝ t, Ballistic)', linewidth=3)
axes[1].plot(steps, RMS_linear, 'g--', label='QW Linear Phase (φ(n) = n)', linewidth=2)
axes[1].plot(steps, RMS_quad, 'r-.', label='QW Quadratic Phase (φ(n) = n^2)', linewidth=2)
axes[1].plot(steps, CRW_RMS, 'k:', label='CRW (∝ sqrt(t), Diffusive)', linewidth=2)
axes[1].set_title('QW RMS Spreading vs. Phase Potential', fontsize=14)
axes[1].set_xlabel('Time Steps (t)', fontsize=12)
axes[1].set_ylabel('RMS Energy Level (sqrt(sum n^2 P(n, t)))', fontsize=12)
axes[1].legend(fontsize=11)
axes[1].grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.show()
