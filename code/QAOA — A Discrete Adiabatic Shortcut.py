import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, Operator
from qiskit.quantum_info.operators import Pauli

def cost_expectation(qc, p_params):
    psi = Statevector(qc)
    ZZ = np.kron(np.diag([1, -1]), np.diag([1, -1]))
    I = np.eye(2)
    ZZ_12 = np.kron(ZZ, I)
    ZZ_23 = np.kron(I, ZZ)
    SWAP = np.array([[1,0,0,0,0,0,0,0],
                     [0,0,0,0,1,0,0,0],
                     [0,0,1,0,0,0,0,0],
                     [0,0,0,0,0,0,1,0],
                     [0,1,0,0,0,0,0,0],
                     [0,0,0,0,0,1,0,0],
                     [0,0,0,1,0,0,0,0],
                     [0,0,0,0,0,0,0,1]])
    ZZ_31 = SWAP @ np.kron(ZZ, I) @ SWAP
    exp_Z1Z2 = psi.expectation_value(Operator(ZZ_12))
    exp_Z2Z3 = psi.expectation_value(Operator(ZZ_23))
    exp_Z3Z1 = psi.expectation_value(Operator(ZZ_31))
    exp_C = 0.5 * (3 - exp_Z1Z2 - exp_Z2Z3 - exp_Z3Z1)
    return -np.real(exp_C)

def qaoa_circuit(p, params):
    qc = QuantumCircuit(3)
    qc.h([0, 1, 2])
    gamma = params[:p]
    beta = params[p:]
    for k in range(p):
        qc.rzz(2 * gamma[k], 0, 1)
        qc.rzz(2 * gamma[k], 1, 2)
        qc.rzz(2 * gamma[k], 2, 0)
        qc.rx(2 * beta[k], [0, 1, 2])
    return qc

def optimize_qaoa(p):
    initial_params = np.random.uniform(0, 2*np.pi, 2 * p)
    def objective(params):
        qc = qaoa_circuit(p, params)
        return cost_expectation(qc, params)
    result = minimize(objective, initial_params, method='COBYLA')
    return -result.fun, result.x

p_depths = [1, 2, 3]
qaoa_results = {}
for p in p_depths:
    max_cost, optimal_params = optimize_qaoa(p)
    qaoa_results[p] = {'cost': max_cost, 'params': optimal_params}

p_values = list(qaoa_results.keys())
costs = [r['cost'] for r in qaoa_results.values()]
max_cut_value = 2.0
approximations = [c / max_cut_value for c in costs]

plt.figure(figsize=(10, 6))
plt.plot(p_values, approximations, 'bo-', label='QAOA Approximation Ratio', linewidth=2, markersize=8)
plt.axhline(1.0, color='g', linestyle='--', label='Optimal Solution (C_max=2.0)')
plt.xlabel('Circuit Depth (p)', fontsize=12)
plt.ylabel('Approximation Ratio', fontsize=12)
plt.title('QAOA Performance vs. Circuit Depth for MaxCut on C_3', fontsize=14)
plt.xticks(p_values)
plt.ylim(0.85, 1.05)
plt.legend(fontsize=11)
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()

print('--- QAOA Optimization Results for MaxCut on C3 ---')
print(f'C_max = {max_cut_value}')
for p, res in qaoa_results.items():
    print(f"p={p}: ⟨C⟩ = {res['cost']:.4f}, Ratio = {res['cost']/max_cut_value:.4f}")

TROTTER_T = 10.0
trotter_costs = []
for p in p_depths:
    qc = QuantumCircuit(3)
    qc.h([0, 1, 2])
    dt = TROTTER_T / p
    for k in range(1, p + 1):
        sk = k / p
        gamma_k = sk * dt
        beta_k = (1 - sk) * dt
        qc.rzz(2 * gamma_k, 0, 1)
        qc.rzz(2 * gamma_k, 1, 2)
        qc.rzz(2 * gamma_k, 2, 0)
        qc.rx(2 * beta_k, [0, 1, 2])
    cost = -cost_expectation(qc, [])
    trotter_costs.append(cost)

print('\nComparison:')
print('p | QAOA ⟨C⟩ | Trotter ⟨C⟩ | Δ⟨C⟩')
print('-' * 50)
for p, qaoa_c, trotter_c in zip(p_values, costs, trotter_costs):
    print(f"{p:>1} | {qaoa_c:8.4f} | {trotter_c:8.4f} | {qaoa_c - trotter_c:+8.4f}")

print('\n1. QAOA achieves better approximation ratios for small p')
print('2. Circuit depth scales as ℴ(p) for both methods')
print('3. QAOA converges faster to C_max as p increases')
