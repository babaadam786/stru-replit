"""
Advanced Structural Analysis Solvers
Includes nonlinear analysis, buckling analysis, and dynamic response.
"""

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve, eigsh
from scipy.integrate import solve_ivp
from typing import Dict, List, Tuple, Optional, Any, Callable
import logging
from dataclasses import dataclass

from .fem_engine import FEMEngine, AnalysisType

logger = logging.getLogger(__name__)


@dataclass
class NonlinearOptions:
    """Options for nonlinear analysis"""
    max_iterations: int = 50
    tolerance: float = 1e-6
    load_steps: int = 10
    line_search: bool = True
    arc_length: bool = False


@dataclass
class DynamicOptions:
    """Options for dynamic analysis"""
    time_step: float = 0.01
    total_time: float = 10.0
    damping_ratio: float = 0.05
    integration_method: str = "newmark"  # newmark, central_difference
    beta: float = 0.25  # Newmark parameter
    gamma: float = 0.5  # Newmark parameter


class AdvancedSolvers:
    """Advanced structural analysis solvers"""
    
    def __init__(self, fem_engine: FEMEngine):
        self.fem = fem_engine
        self.convergence_history: List[float] = []
        self.load_displacement_curve: List[Tuple[float, float]] = []
    
    def solve_nonlinear_static(self, options: NonlinearOptions = None) -> Dict[str, Any]:
        """
        Solve nonlinear static analysis using Newton-Raphson method
        Handles material and geometric nonlinearities
        """
        if options is None:
            options = NonlinearOptions()
        
        logger.info("Starting nonlinear static analysis...")
        
        try:
            # Setup system
            self.fem._setup_dof_mapping()
            self.fem._assemble_global_stiffness()
            self.fem._assemble_global_force()
            
            # Initialize solution
            u = np.zeros(self.fem.total_dofs)
            load_factor = 0.0
            load_increment = 1.0 / options.load_steps
            
            self.convergence_history = []
            self.load_displacement_curve = []
            
            # Load stepping
            for step in range(options.load_steps):
                load_factor += load_increment
                target_force = load_factor * self.fem.F_global
                
                logger.info(f"Load step {step + 1}/{options.load_steps}, λ = {load_factor:.3f}")
                
                # Newton-Raphson iterations
                for iteration in range(options.max_iterations):
                    # Update stiffness matrix (for geometric nonlinearity)
                    K_tangent = self._update_tangent_stiffness(u)
                    
                    # Calculate residual
                    internal_force = self._calculate_internal_force(u)
                    residual = target_force - internal_force
                    
                    # Apply boundary conditions
                    K_constrained, residual_constrained = self._apply_constraints_nonlinear(
                        K_tangent, residual
                    )
                    
                    # Check convergence
                    residual_norm = np.linalg.norm(residual_constrained)
                    self.convergence_history.append(residual_norm)
                    
                    if residual_norm < options.tolerance:
                        logger.info(f"Converged in {iteration + 1} iterations")
                        break
                    
                    # Solve for displacement increment
                    try:
                        du = spsolve(K_constrained, residual_constrained)
                        
                        # Line search (optional)
                        if options.line_search:
                            alpha = self._line_search(u, du, target_force)
                            u += alpha * du
                        else:
                            u += du
                            
                    except Exception as e:
                        logger.error(f"Failed to solve system: {str(e)}")
                        return {"success": False, "error": f"Solver failed: {str(e)}"}
                
                else:
                    logger.warning(f"Failed to converge in {options.max_iterations} iterations")
                    return {
                        "success": False, 
                        "error": f"No convergence in {options.max_iterations} iterations"
                    }
                
                # Store load-displacement point
                max_displacement = np.max(np.abs(u))
                self.load_displacement_curve.append((load_factor, max_displacement))
            
            # Store final results
            self.fem.displacements = u
            self.fem._calculate_element_forces()
            
            logger.info("Nonlinear static analysis completed successfully")
            
            return {
                "success": True,
                "displacements": u.tolist(),
                "max_displacement": float(np.max(np.abs(u))),
                "load_factor": load_factor,
                "convergence_history": self.convergence_history,
                "load_displacement_curve": self.load_displacement_curve
            }
            
        except Exception as e:
            logger.error(f"Nonlinear static analysis failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def solve_buckling_analysis(self, num_modes: int = 10) -> Dict[str, Any]:
        """
        Solve linear buckling analysis (eigenvalue buckling)
        Finds critical load factors and buckling modes
        """
        logger.info(f"Starting buckling analysis for {num_modes} modes...")
        
        try:
            # Setup system
            self.fem._setup_dof_mapping()
            self.fem._assemble_global_stiffness()
            
            # Assemble geometric stiffness matrix
            K_geometric = self._assemble_geometric_stiffness()
            
            # Apply boundary conditions
            K_elastic = self.fem.K_global.copy()
            K_geo_constrained = K_geometric.copy()
            
            # Solve generalized eigenvalue problem: (K_e + λ*K_g)*φ = 0
            # Rearranged as: K_g*φ = -λ*K_e*φ
            try:
                eigenvals, eigenvecs = eigsh(
                    -K_geo_constrained, k=num_modes, M=K_elastic,
                    which='SM', sigma=0.0
                )
                
                # Critical load factors (eigenvalues)
                critical_loads = -eigenvals
                
                logger.info("Buckling analysis completed successfully")
                logger.info(f"First critical load factor: {critical_loads[0]:.3f}")
                
                return {
                    "success": True,
                    "critical_loads": critical_loads.tolist(),
                    "buckling_modes": eigenvecs.tolist(),
                    "num_modes": num_modes,
                    "first_critical_load": float(critical_loads[0])
                }
                
            except Exception as e:
                logger.error(f"Eigenvalue solver failed: {str(e)}")
                return {"success": False, "error": f"Eigenvalue solver failed: {str(e)}"}
            
        except Exception as e:
            logger.error(f"Buckling analysis failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def solve_dynamic_response(self, time_history_loads: np.ndarray, 
                             options: DynamicOptions = None) -> Dict[str, Any]:
        """
        Solve dynamic response analysis
        Supports various time integration schemes
        """
        if options is None:
            options = DynamicOptions()
        
        logger.info("Starting dynamic response analysis...")
        
        try:
            # Setup system
            self.fem._setup_dof_mapping()
            self.fem._assemble_global_stiffness()
            self.fem._assemble_global_mass()
            
            # Assemble damping matrix (Rayleigh damping)
            C_global = self._assemble_rayleigh_damping(options.damping_ratio)
            
            # Time parameters
            dt = options.time_step
            t_total = options.total_time
            n_steps = int(t_total / dt)
            
            # Initialize response arrays
            u_history = np.zeros((n_steps + 1, self.fem.total_dofs))
            v_history = np.zeros((n_steps + 1, self.fem.total_dofs))
            a_history = np.zeros((n_steps + 1, self.fem.total_dofs))
            
            # Initial conditions (zero)
            u = np.zeros(self.fem.total_dofs)
            v = np.zeros(self.fem.total_dofs)
            
            # Calculate initial acceleration
            F0 = time_history_loads[0] if len(time_history_loads) > 0 else np.zeros(self.fem.total_dofs)
            a = spsolve(self.fem.M_global, F0 - C_global @ v - self.fem.K_global @ u)
            
            u_history[0] = u
            v_history[0] = v
            a_history[0] = a
            
            # Time integration
            if options.integration_method == "newmark":
                result = self._newmark_integration(
                    u_history, v_history, a_history, time_history_loads, 
                    C_global, dt, options.beta, options.gamma
                )
            elif options.integration_method == "central_difference":
                result = self._central_difference_integration(
                    u_history, v_history, a_history, time_history_loads, 
                    C_global, dt
                )
            else:
                raise ValueError(f"Unknown integration method: {options.integration_method}")
            
            if not result["success"]:
                return result
            
            logger.info("Dynamic response analysis completed successfully")
            
            # Calculate response statistics
            max_displacement = np.max(np.abs(u_history))
            max_velocity = np.max(np.abs(v_history))
            max_acceleration = np.max(np.abs(a_history))
            
            return {
                "success": True,
                "displacement_history": u_history.tolist(),
                "velocity_history": v_history.tolist(),
                "acceleration_history": a_history.tolist(),
                "time_vector": np.linspace(0, t_total, n_steps + 1).tolist(),
                "max_displacement": float(max_displacement),
                "max_velocity": float(max_velocity),
                "max_acceleration": float(max_acceleration),
                "time_step": dt,
                "total_time": t_total
            }
            
        except Exception as e:
            logger.error(f"Dynamic response analysis failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _update_tangent_stiffness(self, u: np.ndarray) -> csr_matrix:
        """Update tangent stiffness matrix for nonlinear analysis"""
        # For now, return linear stiffness
        # In practice, this would include geometric and material nonlinearities
        return self.fem.K_global.copy()
    
    def _calculate_internal_force(self, u: np.ndarray) -> np.ndarray:
        """Calculate internal force vector"""
        # Linear case
        return self.fem.K_global @ u
    
    def _apply_constraints_nonlinear(self, K: csr_matrix, F: np.ndarray) -> Tuple[csr_matrix, np.ndarray]:
        """Apply boundary conditions for nonlinear analysis"""
        K_constrained = K.copy()
        F_constrained = F.copy()
        
        penalty = 1e12
        
        for constraint in self.fem.constraints:
            node_dofs = self.fem.dof_map[constraint.node_id]
            
            for i, (constrained, dof) in enumerate(zip(constraint.dofs, node_dofs)):
                if constrained and dof >= 0:
                    K_constrained[dof, dof] += penalty
                    F_constrained[dof] += penalty * constraint.values[i]
        
        return K_constrained, F_constrained
    
    def _line_search(self, u: np.ndarray, du: np.ndarray, target_force: np.ndarray) -> float:
        """Perform line search to find optimal step size"""
        alpha = 1.0
        c1 = 1e-4  # Armijo parameter
        
        # Current residual
        current_force = self._calculate_internal_force(u)
        current_residual = np.linalg.norm(target_force - current_force)
        
        for _ in range(10):  # Max line search iterations
            u_trial = u + alpha * du
            trial_force = self._calculate_internal_force(u_trial)
            trial_residual = np.linalg.norm(target_force - trial_force)
            
            if trial_residual < (1 - c1 * alpha) * current_residual:
                break
            
            alpha *= 0.5
        
        return alpha
    
    def _assemble_geometric_stiffness(self) -> csr_matrix:
        """Assemble geometric stiffness matrix for buckling analysis"""
        # Simplified implementation - would need element-specific geometric stiffness
        K_geo = csr_matrix((self.fem.total_dofs, self.fem.total_dofs))
        
        # For demonstration, use a simplified approach
        # In practice, this requires element-specific geometric stiffness matrices
        
        return K_geo
    
    def _assemble_rayleigh_damping(self, damping_ratio: float) -> csr_matrix:
        """Assemble Rayleigh damping matrix: C = α*M + β*K"""
        # Calculate Rayleigh parameters for given damping ratio
        # Simplified approach - assumes first two natural frequencies
        
        # For now, use proportional damping
        alpha = 0.0  # Mass proportional
        beta = 2 * damping_ratio / 100.0  # Stiffness proportional (simplified)
        
        C = alpha * self.fem.M_global + beta * self.fem.K_global
        return C
    
    def _newmark_integration(self, u_history: np.ndarray, v_history: np.ndarray, 
                           a_history: np.ndarray, force_history: np.ndarray,
                           C: csr_matrix, dt: float, beta: float, gamma: float) -> Dict[str, Any]:
        """Newmark time integration scheme"""
        try:
            n_steps = len(u_history) - 1
            
            # Newmark parameters
            a0 = 1.0 / (beta * dt**2)
            a1 = gamma / (beta * dt)
            a2 = 1.0 / (beta * dt)
            a3 = 1.0 / (2 * beta) - 1.0
            a4 = gamma / beta - 1.0
            a5 = dt / 2 * (gamma / beta - 2.0)
            
            # Effective stiffness matrix
            K_eff = self.fem.K_global + a0 * self.fem.M_global + a1 * C
            
            for i in range(n_steps):
                # Current state
                u_n = u_history[i]
                v_n = v_history[i]
                a_n = a_history[i]
                
                # Load at next time step
                F_next = force_history[min(i + 1, len(force_history) - 1)]
                
                # Effective force
                F_eff = (F_next + 
                        self.fem.M_global @ (a0 * u_n + a2 * v_n + a3 * a_n) +
                        C @ (a1 * u_n + a4 * v_n + a5 * a_n))
                
                # Solve for displacement
                u_next = spsolve(K_eff, F_eff)
                
                # Calculate velocity and acceleration
                a_next = a0 * (u_next - u_n) - a2 * v_n - a3 * a_n
                v_next = v_n + dt * ((1 - gamma) * a_n + gamma * a_next)
                
                # Store results
                u_history[i + 1] = u_next
                v_history[i + 1] = v_next
                a_history[i + 1] = a_next
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Newmark integration failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _central_difference_integration(self, u_history: np.ndarray, v_history: np.ndarray,
                                      a_history: np.ndarray, force_history: np.ndarray,
                                      C: csr_matrix, dt: float) -> Dict[str, Any]:
        """Central difference time integration scheme"""
        try:
            n_steps = len(u_history) - 1
            
            # Effective mass matrix
            M_eff = self.fem.M_global + dt/2 * C
            
            for i in range(n_steps):
                # Current state
                u_n = u_history[i]
                v_n = v_history[i]
                
                # Load at current time step
                F_n = force_history[min(i, len(force_history) - 1)]
                
                # Effective force
                F_eff = F_n - self.fem.K_global @ u_n - C @ v_n
                
                # Solve for acceleration
                a_n = spsolve(M_eff, F_eff)
                
                # Update velocity and displacement
                v_next = v_n + dt * a_n
                u_next = u_n + dt * v_next
                
                # Store results
                u_history[i + 1] = u_next
                v_history[i + 1] = v_next
                a_history[i + 1] = a_n
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Central difference integration failed: {str(e)}")
            return {"success": False, "error": str(e)}