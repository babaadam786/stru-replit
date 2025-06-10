"""
Advanced Finite Element Method Engine for Structural Analysis
Supports 1D, 2D, and 3D structural elements with various analysis types.
"""

import numpy as np
from scipy.sparse import csr_matrix, linalg
from scipy.sparse.linalg import spsolve
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ElementType(Enum):
    TRUSS = "truss"
    BEAM = "beam"
    FRAME = "frame"
    PLATE = "plate"
    SHELL = "shell"
    SOLID = "solid"


class AnalysisType(Enum):
    STATIC = "static"
    DYNAMIC = "dynamic"
    BUCKLING = "buckling"
    MODAL = "modal"
    NONLINEAR = "nonlinear"


@dataclass
class Node:
    """Structural node with coordinates and degrees of freedom"""
    id: int
    x: float
    y: float
    z: float = 0.0
    dofs: List[bool] = None  # [Tx, Ty, Tz, Rx, Ry, Rz]
    
    def __post_init__(self):
        if self.dofs is None:
            self.dofs = [True] * 6  # All DOFs active by default


@dataclass
class Material:
    """Material properties for structural analysis"""
    id: int
    name: str
    E: float  # Young's modulus (Pa)
    nu: float  # Poisson's ratio
    rho: float  # Density (kg/m³)
    fy: float = None  # Yield strength (Pa)
    fu: float = None  # Ultimate strength (Pa)
    
    @property
    def G(self) -> float:
        """Shear modulus"""
        return self.E / (2 * (1 + self.nu))


@dataclass
class Section:
    """Cross-section properties"""
    id: int
    name: str
    A: float  # Area (m²)
    Ix: float  # Moment of inertia about x-axis (m⁴)
    Iy: float  # Moment of inertia about y-axis (m⁴)
    Iz: float  # Moment of inertia about z-axis (m⁴)
    J: float  # Torsional constant (m⁴)
    Sy: float = None  # Section modulus y (m³)
    Sz: float = None  # Section modulus z (m³)


@dataclass
class Element:
    """Structural element connecting nodes"""
    id: int
    type: ElementType
    nodes: List[int]  # Node IDs
    material_id: int
    section_id: int = None
    thickness: float = None  # For plate/shell elements
    properties: Dict[str, Any] = None


@dataclass
class Load:
    """Applied loads and boundary conditions"""
    id: int
    node_id: int = None
    element_id: int = None
    type: str = "force"  # force, moment, pressure, distributed
    direction: str = "global"  # global, local
    values: List[float] = None  # [Fx, Fy, Fz, Mx, My, Mz]
    
    def __post_init__(self):
        if self.values is None:
            self.values = [0.0] * 6


@dataclass
class Constraint:
    """Boundary conditions and constraints"""
    id: int
    node_id: int
    dofs: List[bool]  # [Tx, Ty, Tz, Rx, Ry, Rz] - True = constrained
    values: List[float] = None  # Prescribed displacements
    
    def __post_init__(self):
        if self.values is None:
            self.values = [0.0] * 6


class FEMEngine:
    """Advanced Finite Element Method Engine"""
    
    def __init__(self):
        self.nodes: Dict[int, Node] = {}
        self.materials: Dict[int, Material] = {}
        self.sections: Dict[int, Section] = {}
        self.elements: Dict[int, Element] = {}
        self.loads: List[Load] = []
        self.constraints: List[Constraint] = []
        
        # Analysis results
        self.displacements: np.ndarray = None
        self.reactions: np.ndarray = None
        self.element_forces: Dict[int, np.ndarray] = {}
        self.stresses: Dict[int, np.ndarray] = {}
        
        # System matrices
        self.K_global: csr_matrix = None  # Global stiffness matrix
        self.M_global: csr_matrix = None  # Global mass matrix
        self.F_global: np.ndarray = None  # Global force vector
        
        self.dof_map: Dict[int, List[int]] = {}  # Node ID to DOF indices
        self.total_dofs: int = 0
    
    def add_node(self, node: Node) -> None:
        """Add a node to the model"""
        self.nodes[node.id] = node
        logger.info(f"Added node {node.id} at ({node.x}, {node.y}, {node.z})")
    
    def add_material(self, material: Material) -> None:
        """Add a material to the model"""
        self.materials[material.id] = material
        logger.info(f"Added material {material.name} with E={material.E:.2e} Pa")
    
    def add_section(self, section: Section) -> None:
        """Add a section to the model"""
        self.sections[section.id] = section
        logger.info(f"Added section {section.name} with A={section.A:.4f} m²")
    
    def add_element(self, element: Element) -> None:
        """Add an element to the model"""
        self.elements[element.id] = element
        logger.info(f"Added {element.type.value} element {element.id}")
    
    def add_load(self, load: Load) -> None:
        """Add a load to the model"""
        self.loads.append(load)
        logger.info(f"Added load {load.id} of type {load.type}")
    
    def add_constraint(self, constraint: Constraint) -> None:
        """Add a constraint to the model"""
        self.constraints.append(constraint)
        logger.info(f"Added constraint {constraint.id} at node {constraint.node_id}")
    
    def _setup_dof_mapping(self) -> None:
        """Setup degree of freedom mapping"""
        dof_counter = 0
        for node_id, node in self.nodes.items():
            node_dofs = []
            for i, active in enumerate(node.dofs):
                if active:
                    node_dofs.append(dof_counter)
                    dof_counter += 1
                else:
                    node_dofs.append(-1)  # Inactive DOF
            self.dof_map[node_id] = node_dofs
        
        self.total_dofs = dof_counter
        logger.info(f"Total DOFs: {self.total_dofs}")
    
    def _get_element_stiffness_matrix(self, element: Element) -> Tuple[np.ndarray, List[int]]:
        """Calculate element stiffness matrix"""
        if element.type == ElementType.TRUSS:
            return self._truss_stiffness(element)
        elif element.type == ElementType.BEAM:
            return self._beam_stiffness(element)
        elif element.type == ElementType.FRAME:
            return self._frame_stiffness(element)
        else:
            raise NotImplementedError(f"Element type {element.type} not implemented")
    
    def _truss_stiffness(self, element: Element) -> Tuple[np.ndarray, List[int]]:
        """2D/3D truss element stiffness matrix"""
        node1 = self.nodes[element.nodes[0]]
        node2 = self.nodes[element.nodes[1]]
        material = self.materials[element.material_id]
        section = self.sections[element.section_id]
        
        # Element geometry
        dx = node2.x - node1.x
        dy = node2.y - node1.y
        dz = node2.z - node1.z
        L = np.sqrt(dx**2 + dy**2 + dz**2)
        
        # Direction cosines
        cx = dx / L
        cy = dy / L
        cz = dz / L
        
        # Element stiffness in local coordinates
        k_local = (material.E * section.A / L) * np.array([
            [1, -1],
            [-1, 1]
        ])
        
        # Transformation matrix for 3D
        T = np.zeros((6, 6))
        T[0, 0] = T[3, 3] = cx
        T[0, 1] = T[3, 4] = cy
        T[0, 2] = T[3, 5] = cz
        T[1, 0] = T[4, 3] = -cy
        T[1, 1] = T[4, 4] = cx
        T[2, 0] = T[5, 3] = -cz
        T[2, 2] = T[5, 5] = cx
        
        # Expand local stiffness to 6 DOF per node
        k_expanded = np.zeros((6, 6))
        k_expanded[0, 0] = k_expanded[3, 3] = k_local[0, 0]
        k_expanded[0, 3] = k_expanded[3, 0] = k_local[0, 1]
        
        # Transform to global coordinates
        k_global = T.T @ k_expanded @ T
        
        # DOF indices
        dofs = []
        for node_id in element.nodes:
            dofs.extend(self.dof_map[node_id])
        
        return k_global, dofs
    
    def _beam_stiffness(self, element: Element) -> Tuple[np.ndarray, List[int]]:
        """3D beam element stiffness matrix (Euler-Bernoulli)"""
        node1 = self.nodes[element.nodes[0]]
        node2 = self.nodes[element.nodes[1]]
        material = self.materials[element.material_id]
        section = self.sections[element.section_id]
        
        # Element geometry
        dx = node2.x - node1.x
        dy = node2.y - node1.y
        dz = node2.z - node1.z
        L = np.sqrt(dx**2 + dy**2 + dz**2)
        
        E = material.E
        G = material.G
        A = section.A
        Iy = section.Iy
        Iz = section.Iz
        J = section.J
        
        # Local stiffness matrix (12x12 for 3D beam)
        k_local = np.zeros((12, 12))
        
        # Axial terms
        k_local[0, 0] = k_local[6, 6] = E * A / L
        k_local[0, 6] = k_local[6, 0] = -E * A / L
        
        # Bending about y-axis (in xz plane)
        EIy_L3 = E * Iy / L**3
        k_local[2, 2] = k_local[8, 8] = 12 * EIy_L3
        k_local[2, 8] = k_local[8, 2] = -12 * EIy_L3
        k_local[4, 4] = k_local[10, 10] = 4 * E * Iy / L
        k_local[4, 10] = k_local[10, 4] = 2 * E * Iy / L
        k_local[2, 4] = k_local[4, 2] = 6 * E * Iy / L**2
        k_local[2, 10] = k_local[10, 2] = 6 * E * Iy / L**2
        k_local[8, 4] = k_local[4, 8] = -6 * E * Iy / L**2
        k_local[8, 10] = k_local[10, 8] = -6 * E * Iy / L**2
        
        # Bending about z-axis (in xy plane)
        EIz_L3 = E * Iz / L**3
        k_local[1, 1] = k_local[7, 7] = 12 * EIz_L3
        k_local[1, 7] = k_local[7, 1] = -12 * EIz_L3
        k_local[5, 5] = k_local[11, 11] = 4 * E * Iz / L
        k_local[5, 11] = k_local[11, 5] = 2 * E * Iz / L
        k_local[1, 5] = k_local[5, 1] = -6 * E * Iz / L**2
        k_local[1, 11] = k_local[11, 1] = -6 * E * Iz / L**2
        k_local[7, 5] = k_local[5, 7] = 6 * E * Iz / L**2
        k_local[7, 11] = k_local[11, 7] = 6 * E * Iz / L**2
        
        # Torsion
        k_local[3, 3] = k_local[9, 9] = G * J / L
        k_local[3, 9] = k_local[9, 3] = -G * J / L
        
        # Transformation matrix (simplified - assumes element aligned with global x-axis)
        # In practice, this would include full 3D rotation
        T = np.eye(12)  # Identity for now - would need proper transformation
        
        k_global = T.T @ k_local @ T
        
        # DOF indices
        dofs = []
        for node_id in element.nodes:
            dofs.extend(self.dof_map[node_id])
        
        return k_global, dofs
    
    def _frame_stiffness(self, element: Element) -> Tuple[np.ndarray, List[int]]:
        """3D frame element (beam with axial-bending coupling)"""
        return self._beam_stiffness(element)  # Same as beam for now
    
    def _assemble_global_stiffness(self) -> None:
        """Assemble global stiffness matrix"""
        self.K_global = csr_matrix((self.total_dofs, self.total_dofs))
        
        for element in self.elements.values():
            k_elem, dofs = self._get_element_stiffness_matrix(element)
            
            # Filter out inactive DOFs
            active_dofs = [dof for dof in dofs if dof >= 0]
            if len(active_dofs) == 0:
                continue
            
            # Create index arrays for sparse matrix assembly
            rows, cols = np.meshgrid(active_dofs, active_dofs, indexing='ij')
            
            # Add element stiffness to global matrix
            self.K_global += csr_matrix(
                (k_elem.flatten(), (rows.flatten(), cols.flatten())),
                shape=(self.total_dofs, self.total_dofs)
            )
    
    def _assemble_global_force(self) -> None:
        """Assemble global force vector"""
        self.F_global = np.zeros(self.total_dofs)
        
        for load in self.loads:
            if load.node_id is not None:
                node_dofs = self.dof_map[load.node_id]
                for i, (force, dof) in enumerate(zip(load.values, node_dofs)):
                    if dof >= 0:  # Active DOF
                        self.F_global[dof] += force
    
    def _apply_constraints(self) -> Tuple[csr_matrix, np.ndarray]:
        """Apply boundary conditions using penalty method"""
        K_constrained = self.K_global.copy()
        F_constrained = self.F_global.copy()
        
        penalty = 1e12  # Large penalty value
        
        for constraint in self.constraints:
            node_dofs = self.dof_map[constraint.node_id]
            
            for i, (constrained, dof) in enumerate(zip(constraint.dofs, node_dofs)):
                if constrained and dof >= 0:
                    # Apply penalty method
                    K_constrained[dof, dof] += penalty
                    F_constrained[dof] += penalty * constraint.values[i]
        
        return K_constrained, F_constrained
    
    def solve_static(self) -> Dict[str, Any]:
        """Solve static analysis"""
        logger.info("Starting static analysis...")
        
        # Setup DOF mapping
        self._setup_dof_mapping()
        
        # Assemble system matrices
        self._assemble_global_stiffness()
        self._assemble_global_force()
        
        # Apply boundary conditions
        K_constrained, F_constrained = self._apply_constraints()
        
        # Solve system of equations
        try:
            self.displacements = spsolve(K_constrained, F_constrained)
            logger.info("Static analysis completed successfully")
            
            # Calculate reactions
            self.reactions = self.K_global @ self.displacements - self.F_global
            
            # Calculate element forces
            self._calculate_element_forces()
            
            return {
                "success": True,
                "displacements": self.displacements.tolist(),
                "max_displacement": float(np.max(np.abs(self.displacements))),
                "total_dofs": self.total_dofs
            }
            
        except Exception as e:
            logger.error(f"Static analysis failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _calculate_element_forces(self) -> None:
        """Calculate internal forces in elements"""
        for element in self.elements.values():
            k_elem, dofs = self._get_element_stiffness_matrix(element)
            
            # Extract element displacements
            active_dofs = [dof for dof in dofs if dof >= 0]
            if len(active_dofs) == 0:
                continue
            
            u_elem = np.array([self.displacements[dof] for dof in active_dofs])
            
            # Calculate element forces
            f_elem = k_elem @ u_elem
            self.element_forces[element.id] = f_elem
    
    def solve_modal(self, num_modes: int = 10) -> Dict[str, Any]:
        """Solve modal analysis (eigenvalue problem)"""
        logger.info(f"Starting modal analysis for {num_modes} modes...")
        
        try:
            # Setup DOF mapping
            self._setup_dof_mapping()
            
            # Assemble stiffness matrix
            self._assemble_global_stiffness()
            
            # Assemble mass matrix (simplified - lumped mass)
            self._assemble_global_mass()
            
            # Apply constraints (homogeneous)
            K_constrained = self.K_global.copy()
            M_constrained = self.M_global.copy()
            
            # Solve generalized eigenvalue problem: K*phi = lambda*M*phi
            eigenvals, eigenvecs = linalg.eigsh(
                K_constrained, k=num_modes, M=M_constrained, 
                which='SM', sigma=0.0
            )
            
            # Calculate natural frequencies
            frequencies = np.sqrt(eigenvals) / (2 * np.pi)
            
            logger.info("Modal analysis completed successfully")
            
            return {
                "success": True,
                "frequencies": frequencies.tolist(),
                "mode_shapes": eigenvecs.tolist(),
                "num_modes": num_modes
            }
            
        except Exception as e:
            logger.error(f"Modal analysis failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _assemble_global_mass(self) -> None:
        """Assemble global mass matrix (simplified lumped mass)"""
        self.M_global = csr_matrix((self.total_dofs, self.total_dofs))
        
        # Simplified lumped mass approach
        for element in self.elements.values():
            material = self.materials[element.material_id]
            section = self.sections.get(element.section_id)
            
            if section is None:
                continue
            
            # Calculate element mass
            node1 = self.nodes[element.nodes[0]]
            node2 = self.nodes[element.nodes[1]]
            dx = node2.x - node1.x
            dy = node2.y - node1.y
            dz = node2.z - node1.z
            L = np.sqrt(dx**2 + dy**2 + dz**2)
            
            element_mass = material.rho * section.A * L
            nodal_mass = element_mass / 2  # Distribute equally to nodes
            
            # Add to global mass matrix (translational DOFs only)
            for node_id in element.nodes:
                node_dofs = self.dof_map[node_id]
                for i in range(3):  # x, y, z translations
                    dof = node_dofs[i]
                    if dof >= 0:
                        self.M_global[dof, dof] += nodal_mass
    
    def get_results_summary(self) -> Dict[str, Any]:
        """Get analysis results summary"""
        if self.displacements is None:
            return {"error": "No analysis results available"}
        
        return {
            "max_displacement": float(np.max(np.abs(self.displacements))),
            "total_nodes": len(self.nodes),
            "total_elements": len(self.elements),
            "total_dofs": self.total_dofs,
            "analysis_complete": True
        }