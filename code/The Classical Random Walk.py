import numpy as np
import matplotlib.pyplot as plt

def classical_random_walk_rms(max_steps=100, num_walks=10000):
    """
    Simulates a 1D classical random walk, computes the RMS displacement,
    and plots it against the theoretical sqrt(N) scaling.
    
    Args:
        max_steps (int): The maximum number of steps for the walk.
        num_walks (int): The number of independent walks to average over (for statistical accuracy).
    
    Returns:
        tuple: (steps_array, rms_displacement), the computed data points.
    """

    steps = np.random.choice([-1, 1], size=(num_walks, max_steps))
    positions = np.cumsum(steps, axis=1)
    mean_sq_displacement = np.mean(positions**2, axis=0)
    rms_displacement = np.sqrt(mean_sq_displacement)
    steps_array = np.arange(1, max_steps + 1)

    plt.figure(figsize=(10, 6))
    plt.plot(steps_array, rms_displacement, label='Simulated RMS Displacement', color='#1f77b4', linewidth=2)
    plt.plot(steps_array, np.sqrt(steps_array), 'r--', label='Theoretical sqrt(N) Scaling', linewidth=2.5, alpha=0.7)
    plt.xlabel('Number of Steps (N)', fontsize=12)
    plt.ylabel('RMS Displacement (σₘₛ)', fontsize=12)
    plt.title(f'Problem 0: Classical Random Walk Scaling (Averaged over {num_walks} walks)', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, which='major', linestyle='-', alpha=0.5)
    plt.grid(True, which='minor', linestyle=':', alpha=0.3)
    plt.minorticks_on()
    plt.show()

    return steps_array, rms_displacement

steps_N, rms_sigma = classical_random_walk_rms(max_steps=100, num_walks=10000)

print(f"\nSimulation Complete (N={steps_N[-1]}, Walks={10000})")
print("-" * 65)
print("Steps (N) | Simulated σₘₛ            | Theoretical √N")
print("-" * 65)
for N, rms in zip(steps_N[::10] - 1, rms_sigma[::10]):
    print(f"{N+1:9} | {rms:22.4f} | {np.sqrt(N+1):14.4f}")
print("-" * 65)
