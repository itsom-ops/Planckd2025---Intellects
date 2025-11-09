# ⚛️ Planckd2025 - Quantum Algorithm Track: *The Intellects*

This repository documents the analysis and simulation work completed for the **Quantum Algorithm Track**, spanning **classical random walks**, **quantum search**, **variational optimization (QAOA)**, and the **dynamics of open quantum systems**.

---

## 🚀 Project Overview

The project follows a comprehensive journey from **fundamental classical exploration** to **advanced quantum algorithms** operating under **realistic noise models**.  
The goal is to **numerically demonstrate and analyze** the performance advantages, theoretical limitations, and practical robustness of core quantum computing techniques.

All code and simulation results are contained within the `code.ipynb` Jupyter Notebook.

---

## 📁 Repository Structure

├── code.ipynb # Main Jupyter Notebook containing all code (Problems 0–8)
├── README.md # This overview file
└── outputs/ # Directory for generated plots and result data (e.g., performance curves)


---

## ✨ Phase I: Classical and Quantum Walk Dynamics *(Problems 0–3)*

This phase establishes the **fundamental quadratic speedup** achieved by leveraging **quantum interference** in a walk mechanism.

### **Key Metric:** Root-Mean-Squared (RMS) Displacement (σ)

| Algorithm | Scaling Law | Complexity Implication |
|------------|-------------|-------------------------|
| **Problem 0: Classical Random Walk (CRW)** |  $$\sigma(t) \propto \sqrt{t}$$ | Diffusive spreading. Time required to reach distance $x$ scales as $T \propto x^2$. |
| **Problems 1–3: Quantum Walk (QW)** |  $$\sigma(t) \propto t$$ | Ballistic spreading. Time required to reach distance $x$ scales as $T \propto x$. |

The **Quantum Walk** thus provides a **quadratic speedup**  
$$
\mathcal{O}(t) \text{ vs. } \mathcal{O}(\sqrt{t})
$$  
in spatial spreading — a critical resource for later search algorithms.

---

## ✨ Phase II: Quantum Search and Amplitude Amplification *(Problems 4–5)*

This section demonstrates how the **speedup of quantum mechanics** is applied to solve the **unstructured search problem**.

### **Problem 4: Quantum Search (Grover’s Algorithm)**

Grover’s Algorithm is the **optimal quantum solution** for searching an unstructured database of $N$ items.

| Search Type | Classical Best | Quantum (Grover’s) |
|--------------|----------------|--------------------|
| **Unstructured Search** | $\mathcal{O}(N)$ | $\mathcal{O}(\sqrt{N})$ |

---

### **Problem 5: Quantum Amplitude Amplification (QAA)**

QAA generalizes Grover’s algorithm.  
For a state with initial target amplitude $A_0 = \sin(\theta)$,  
QAA boosts it to:

$$
A_k = \sin((2k+1)\theta)
$$

**Iterations Required:**

$$
k \approx \mathcal{O}\left( \frac{1}{\sin(\theta)} \right)
$$

---

## ✨ Phase III: Quantum Optimization and Variational Methods *(Problems 6–7)*

This phase explores two contrasting methods for solving optimization problems.

---

### **Problem 6: Adiabatic Quantum Computing (AQC)**

AQC’s runtime is fundamentally limited by the **minimum energy difference** between the ground state and first excited state, known as the **spectral gap** ($\Delta_{\min}$).

**Runtime Constraint:**

$$
T \propto \frac{1}{\Delta_{\min}^2}
$$

**Implication:**  
If the spectral gap is **exponentially small**, AQC requires **exponentially long time**, losing the quantum advantage.

---

### **Problem 7: QAOA — A Discrete Adiabatic Shortcut**

QAOA can be viewed as the **first-order Trotterized discretization** of AQC.

**Trotterization Link:**

$$
\gamma_k = s_k \Delta t \quad \text{and} \quad \beta_k = (1 - s_k) \Delta t
$$

where $s_k$ is the schedule parameter and $\Delta t$ is the time step.

**MaxCut ($C_3$) Results:**  
The variationally optimized QAOA achieved $C_{\max} = 2.0$ even at low depths ($p = 1, 2$),  
significantly outperforming the fixed linear Trotter schedule.

**Conclusion:**  
QAOA serves as a **non-linear, efficient shortcut**, not strictly constrained by the adiabatic path’s spectral gap.

---

## ✨ Phase IV: Open Quantum Systems and Robustness *(Problem 8)*

This phase addresses the **practical implementation** of quantum algorithms by simulating **noise** and **measurement effects**.

---

### **1. QAOA Robustness under Amplitude Damping ($p_{AD}$)**

**Finding:**  
Shallow QAOA ($p = 1$) proved significantly **more robust** than deeper circuits ($p = 2$).

**Conclusion:**  
Algorithm fidelity **degrades exponentially** with the number of noisy gates.  
In the **NISQ era**, minimizing **circuit depth** is the most effective form of **noise mitigation**.

---

### **2. Measurement-Induced Entanglement**

Simulating a 1D chain under alternating **unitary** and **random measurements** (with probability $p_m$) revealed a **phase transition** in entanglement growth.

| Regime | Entanglement Scaling | Physical Interpretation |
|---------|----------------------|--------------------------|
| **Volume-Law Phase ($p_m \approx 0$)** | $S \propto L$ | Entanglement grows proportionally to subsystem length. |
| **Area-Law Phase ($p_m \approx 1$)** | $S \propto 1$ | Entanglement saturates to a constant value. |

**Physics Insight:**  
This demonstrates the **competition** between:
- *Entanglement generation* (unitary evolution), and  
- *Entanglement destruction* (measurement-induced collapse).

---

### **3. Adaptive Correction and the Quantum Zeno Effect (QZE)**

**Strategy:**  
Implement a **classical feedback loop** — measure an error-prone qubit, apply a corrective gate.

**Result:**  
The adaptive strategy improved **algorithm fidelity** under **dephasing noise**.

**QZE Relationship:**  
This effect works by harnessing the **Quantum Zeno Effect** —  
frequent measurements **freeze** the state’s dynamics and **prevent noise spreading**, allowing the classical controller to **steer** the system back toward the high-fidelity subspace.

---

## 💻 Dependencies

To replicate the simulations in `code.ipynb`, install the following Python packages:

```bash
pip install numpy matplotlib scipy
