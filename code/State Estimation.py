import numpy as np
from typing import Dict, List, Tuple
import sys
import io



# Pauli Matrices
I = np.array([[1, 0], [0, 1]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
PAULI_MAP = {'I': I, 'X': X, 'Y': Y, 'Z': Z}

# All 16 two-qubit product operators (for linear inversion reconstruction)
PAULI_OPS = {}
for p1 in ['I', 'X', 'Y', 'Z']:
    for p0 in ['I', 'X', 'Y', 'Z']:
        op_name = p1 + p0
        PAULI_OPS[op_name] = np.kron(PAULI_MAP[p1], PAULI_MAP[p0])


H = (1/np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)        # X-Basis
S_DAG_H = (1/np.sqrt(2)) * np.array([[1, -1j], [1, 1j]], dtype=complex) # Y-Basis (R_y(-pi/2))
UNITARY_MAP = {'I': I, 'X': H, 'Y': S_DAG_H, 'Z': I}

# --- 2. Core QST Functions ---

def get_product_unitary(op_name: str) -> np.ndarray:
    """Gets the two-qubit basis change unitary U = U1 kron U0."""
    u1 = UNITARY_MAP[op_name[0]]
    u0 = UNITARY_MAP[op_name[1]]
    return np.kron(u1, u0)

def simulate_measurement(rho: np.ndarray, basis_unitary: np.ndarray, shots: int) -> Dict[str, int]:
    """
    Simulates measurement counts for a state rho in the rotated computational basis.
    """
    # Rotated state: rho_rotated = U * rho * U^\dagger
    rho_rotated = basis_unitary @ rho @ basis_unitary.conj().T
    probabilities = np.diag(rho_rotated).real.copy()
    
    # Handle numerical noise and normalize
    probabilities[probabilities < -1e-9] = 0
    probabilities /= np.sum(probabilities)

    # Use a faster, non-qiskit-dependent way to draw random counts
    outcomes = np.random.multinomial(shots, probabilities)
    
    return {
        '00': outcomes[0], 
        '01': outcomes[1], 
        '10': outcomes[2], 
        '11': outcomes[3]
    }

def reconstruct_rho(exp_values: Dict[str, complex]) -> np.ndarray:
    """Reconstructs the density matrix rho from 16 Pauli expectation values (Linear Inversion)."""
    rho_est = np.zeros((4, 4), dtype=complex)
    for op_name, op in PAULI_OPS.items():
        if op_name in exp_values:
            rho_est += exp_values[op_name] * op
    # Normalization factor for two qubits (1/2^2 = 1/4)
    return (1/4) * rho_est

def pure_state_projection(rho_est: np.ndarray) -> np.ndarray:
    """Finds the estimated pure state vector |psi> (MLE projection) as the principal eigenvector."""
    # 1. Ensure the matrix is Hermitian for eigh stability
    rho_est = (rho_est + rho_est.conj().T) / 2
    
    # 2. Find Eigenvalues and Eigenvectors
    eigenvalues, eigenvectors = np.linalg.eigh(rho_est)
    
    # 3. Identify the principal eigenvector (largest eigenvalue)
    max_index = np.argmax(eigenvalues.real)
    psi_hat = eigenvectors[:, max_index]
    
    # 4. Global Phase Fix: Force the first non-zero element to be real and positive
    first_non_zero_index = np.where(np.abs(psi_hat) > 1e-9)[0]
    if len(first_non_zero_index) > 0:
        idx = first_non_zero_index[0]
        # Calculate phase factor to make the component real and positive
        phase_factor = psi_hat[idx] / np.abs(psi_hat[idx])
        psi_hat = psi_hat / phase_factor
        
    # 5. Normalize (should be near 1 already, but for safety)
    psi_hat /= np.linalg.norm(psi_hat)
    
    return psi_hat.flatten()



def solve_qst_problem(tests_data: List[List[complex]], total_shots: int = 500) -> List[List[complex]]:
    """
    Performs Two-Qubit PST for multiple pure states.
    """
    

    MEASUREMENT_BASES = ['XX', 'XY', 'XZ', 'YX', 'YY', 'YZ', 'ZX', 'ZY', 'ZZ']
    shots_per_basis = int(total_shots / len(MEASUREMENT_BASES))
    
    estimated_states = []

    for coeffs_true in tests_data:
        psi_true = np.array(coeffs_true, dtype=complex).reshape(4, 1)
        rho_true = psi_true @ psi_true.conj().T
        
        # Initialize all 16 expectation values
        all_exp_values = {'II': 1.0}
        
       
        for basis in MEASUREMENT_BASES:
            unitary = get_product_unitary(basis)
            counts = simulate_measurement(rho_true, unitary, shots_per_basis)
            
            C_00, C_01, C_10, C_11 = counts.get('00', 0), counts.get('01', 0), counts.get('10', 0), counts.get('11', 0)
            N = shots_per_basis
            
          
            all_exp_values[basis] = (C_00 + C_11 - C_01 - C_10) / N
            

            P1 = basis[0]
            if P1 != 'I' and P1+'I' not in all_exp_values:
                all_exp_values[P1+'I'] = (C_00 + C_01 - C_10 - C_11) / N
                
           
            P0 = basis[1]
            if P0 != 'I' and 'I'+P0 not in all_exp_values:
                all_exp_values['I'+P0] = (C_00 - C_01 + C_10 - C_11) / N

    
        rho_est = reconstruct_rho(all_exp_values)
        psi_hat = pure_state_projection(rho_est)
        
        estimated_states.append(psi_hat.tolist())

    return estimated_states



def parse_and_run():
    """Reads from the specified format, runs the solver, and prints results."""
    

    simulated_file_content = """2
0.7071067811865476 0 0 0.7071067811865476
0.5 0.5 0+0.5j 0.5"""
    
    tests_data = []
    
    try:
        lines = simulated_file_content.strip().split('\n')
        if not lines:
            return
            
        num_tests = int(lines[0].strip())

        for line in lines[1:num_tests + 1]:
            parts = line.split()
            coeffs = []
            for part in parts:
                
                try:
                    coeffs.append(complex(part.replace(' ', ''))) 
                except ValueError:
                    
                    try:
                        coeffs.append(complex(float(part.replace(' ', ''))))
                    except ValueError:
                        print(f"Warning: Failed to parse coefficient '{part}'. Using 0+0j.", file=sys.stderr)
                        coeffs.append(complex(0.0))
                    
            if len(coeffs) == 4:
                tests_data.append(coeffs)
            
    except Exception as e:
        print(f"Error reading/parsing simulated input: {e}", file=sys.stderr)
        return
        

    estimated_results = solve_qst_problem(tests_data, total_shots=500)

    
    print(str(len(estimated_results)))
    
    
    for coeffs_hat in estimated_results:
       
        output_line = " ".join([f"{c.real:.10f}+{c.imag:.10f}j" for c in coeffs_hat])
        print(output_line)


parse_and_run()
