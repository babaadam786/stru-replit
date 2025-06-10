"""
Analysis API endpoints for structural analysis operations
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from ..core.fem_engine import FEMEngine, Node, Material, Section, Element, Load, Constraint, ElementType
from ..core.solvers import AdvancedSolvers, NonlinearOptions, DynamicOptions

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for API
class NodeModel(BaseModel):
    id: int
    x: float
    y: float
    z: float = 0.0
    dofs: List[bool] = [True] * 6

class MaterialModel(BaseModel):
    id: int
    name: str
    E: float
    nu: float
    rho: float
    fy: Optional[float] = None
    fu: Optional[float] = None

class SectionModel(BaseModel):
    id: int
    name: str
    A: float
    Ix: float
    Iy: float
    Iz: float
    J: float

class ElementModel(BaseModel):
    id: int
    type: str
    nodes: List[int]
    material_id: int
    section_id: Optional[int] = None

class LoadModel(BaseModel):
    id: int
    node_id: Optional[int] = None
    element_id: Optional[int] = None
    type: str = "force"
    direction: str = "global"
    values: List[float] = [0.0] * 6

class ConstraintModel(BaseModel):
    id: int
    node_id: int
    dofs: List[bool]
    values: List[float] = [0.0] * 6

class StructuralModel(BaseModel):
    nodes: List[NodeModel]
    materials: List[MaterialModel]
    sections: List[SectionModel]
    elements: List[ElementModel]
    loads: List[LoadModel]
    constraints: List[ConstraintModel]

class AnalysisRequest(BaseModel):
    model: StructuralModel
    analysis_type: str = "static"
    options: Optional[Dict[str, Any]] = None

class AnalysisResponse(BaseModel):
    success: bool
    analysis_id: str
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

# Global storage for analysis results (in production, use database)
analysis_results: Dict[str, Dict[str, Any]] = {}

@router.post("/static", response_model=AnalysisResponse)
async def run_static_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Run static structural analysis"""
    try:
        analysis_id = f"static_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Create FEM engine and build model
        engine = FEMEngine()
        await build_model(engine, request.model)
        
        # Run static analysis
        result = engine.solve_static()
        
        # Store results
        analysis_results[analysis_id] = {
            "type": "static",
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "model_summary": {
                "nodes": len(request.model.nodes),
                "elements": len(request.model.elements),
                "materials": len(request.model.materials)
            }
        }
        
        return AnalysisResponse(
            success=result["success"],
            analysis_id=analysis_id,
            results=result,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Static analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/modal", response_model=AnalysisResponse)
async def run_modal_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Run modal analysis (natural frequencies and mode shapes)"""
    try:
        analysis_id = f"modal_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Create FEM engine and build model
        engine = FEMEngine()
        await build_model(engine, request.model)
        
        # Get number of modes from options
        num_modes = request.options.get("num_modes", 10) if request.options else 10
        
        # Run modal analysis
        result = engine.solve_modal(num_modes)
        
        # Store results
        analysis_results[analysis_id] = {
            "type": "modal",
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "options": {"num_modes": num_modes}
        }
        
        return AnalysisResponse(
            success=result["success"],
            analysis_id=analysis_id,
            results=result,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Modal analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/nonlinear", response_model=AnalysisResponse)
async def run_nonlinear_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Run nonlinear static analysis"""
    try:
        analysis_id = f"nonlinear_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Create FEM engine and build model
        engine = FEMEngine()
        await build_model(engine, request.model)
        
        # Create advanced solver
        solver = AdvancedSolvers(engine)
        
        # Setup nonlinear options
        options = NonlinearOptions()
        if request.options:
            options.max_iterations = request.options.get("max_iterations", 50)
            options.tolerance = request.options.get("tolerance", 1e-6)
            options.load_steps = request.options.get("load_steps", 10)
            options.line_search = request.options.get("line_search", True)
        
        # Run nonlinear analysis
        result = solver.solve_nonlinear_static(options)
        
        # Store results
        analysis_results[analysis_id] = {
            "type": "nonlinear",
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "options": {
                "max_iterations": options.max_iterations,
                "tolerance": options.tolerance,
                "load_steps": options.load_steps
            }
        }
        
        return AnalysisResponse(
            success=result["success"],
            analysis_id=analysis_id,
            results=result,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Nonlinear analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/buckling", response_model=AnalysisResponse)
async def run_buckling_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Run linear buckling analysis"""
    try:
        analysis_id = f"buckling_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Create FEM engine and build model
        engine = FEMEngine()
        await build_model(engine, request.model)
        
        # Create advanced solver
        solver = AdvancedSolvers(engine)
        
        # Get number of modes from options
        num_modes = request.options.get("num_modes", 10) if request.options else 10
        
        # Run buckling analysis
        result = solver.solve_buckling_analysis(num_modes)
        
        # Store results
        analysis_results[analysis_id] = {
            "type": "buckling",
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "options": {"num_modes": num_modes}
        }
        
        return AnalysisResponse(
            success=result["success"],
            analysis_id=analysis_id,
            results=result,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Buckling analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dynamic", response_model=AnalysisResponse)
async def run_dynamic_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Run dynamic response analysis"""
    try:
        analysis_id = f"dynamic_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Create FEM engine and build model
        engine = FEMEngine()
        await build_model(engine, request.model)
        
        # Create advanced solver
        solver = AdvancedSolvers(engine)
        
        # Setup dynamic options
        options = DynamicOptions()
        if request.options:
            options.time_step = request.options.get("time_step", 0.01)
            options.total_time = request.options.get("total_time", 10.0)
            options.damping_ratio = request.options.get("damping_ratio", 0.05)
            options.integration_method = request.options.get("integration_method", "newmark")
        
        # Get time history loads (simplified - in practice would be more complex)
        import numpy as np
        n_steps = int(options.total_time / options.time_step)
        time_history = np.zeros((n_steps + 1, engine.total_dofs))
        
        # Apply harmonic loading for demonstration
        if request.options and "frequency" in request.options:
            freq = request.options["frequency"]
            amplitude = request.options.get("amplitude", 1000.0)
            time_vec = np.linspace(0, options.total_time, n_steps + 1)
            
            # Apply to first DOF for demonstration
            if engine.total_dofs > 0:
                time_history[:, 0] = amplitude * np.sin(2 * np.pi * freq * time_vec)
        
        # Run dynamic analysis
        result = solver.solve_dynamic_response(time_history, options)
        
        # Store results
        analysis_results[analysis_id] = {
            "type": "dynamic",
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "options": {
                "time_step": options.time_step,
                "total_time": options.total_time,
                "damping_ratio": options.damping_ratio
            }
        }
        
        return AnalysisResponse(
            success=result["success"],
            analysis_id=analysis_id,
            results=result,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Dynamic analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{analysis_id}")
async def get_analysis_results(analysis_id: str):
    """Get analysis results by ID"""
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_results[analysis_id]

@router.get("/results")
async def list_analysis_results():
    """List all analysis results"""
    return {
        "analyses": [
            {
                "id": aid,
                "type": data["type"],
                "timestamp": data["timestamp"],
                "success": data["result"].get("success", False)
            }
            for aid, data in analysis_results.items()
        ]
    }

@router.delete("/results/{analysis_id}")
async def delete_analysis_results(analysis_id: str):
    """Delete analysis results"""
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    del analysis_results[analysis_id]
    return {"message": "Analysis results deleted successfully"}

@router.post("/validate")
async def validate_model(model: StructuralModel):
    """Validate structural model before analysis"""
    try:
        validation_errors = []
        warnings = []
        
        # Check for minimum requirements
        if len(model.nodes) < 2:
            validation_errors.append("Model must have at least 2 nodes")
        
        if len(model.elements) < 1:
            validation_errors.append("Model must have at least 1 element")
        
        if len(model.materials) < 1:
            validation_errors.append("Model must have at least 1 material")
        
        # Check node connectivity
        node_ids = {node.id for node in model.nodes}
        for element in model.elements:
            for node_id in element.nodes:
                if node_id not in node_ids:
                    validation_errors.append(f"Element {element.id} references non-existent node {node_id}")
        
        # Check material references
        material_ids = {mat.id for mat in model.materials}
        for element in model.elements:
            if element.material_id not in material_ids:
                validation_errors.append(f"Element {element.id} references non-existent material {element.material_id}")
        
        # Check for boundary conditions
        has_constraints = len(model.constraints) > 0
        if not has_constraints:
            warnings.append("No boundary conditions defined - model may be unstable")
        
        # Check for loads
        has_loads = len(model.loads) > 0
        if not has_loads:
            warnings.append("No loads defined - analysis may not be meaningful")
        
        return {
            "valid": len(validation_errors) == 0,
            "errors": validation_errors,
            "warnings": warnings,
            "summary": {
                "nodes": len(model.nodes),
                "elements": len(model.elements),
                "materials": len(model.materials),
                "loads": len(model.loads),
                "constraints": len(model.constraints)
            }
        }
    
    except Exception as e:
        logger.error(f"Model validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def build_model(engine: FEMEngine, model: StructuralModel):
    """Build FEM model from Pydantic model"""
    try:
        # Add nodes
        for node_data in model.nodes:
            node = Node(
                id=node_data.id,
                x=node_data.x,
                y=node_data.y,
                z=node_data.z,
                dofs=node_data.dofs
            )
            engine.add_node(node)
        
        # Add materials
        for material_data in model.materials:
            material = Material(
                id=material_data.id,
                name=material_data.name,
                E=material_data.E,
                nu=material_data.nu,
                rho=material_data.rho,
                fy=material_data.fy,
                fu=material_data.fu
            )
            engine.add_material(material)
        
        # Add sections
        for section_data in model.sections:
            section = Section(
                id=section_data.id,
                name=section_data.name,
                A=section_data.A,
                Ix=section_data.Ix,
                Iy=section_data.Iy,
                Iz=section_data.Iz,
                J=section_data.J
            )
            engine.add_section(section)
        
        # Add elements
        for element_data in model.elements:
            element = Element(
                id=element_data.id,
                type=ElementType(element_data.type),
                nodes=element_data.nodes,
                material_id=element_data.material_id,
                section_id=element_data.section_id
            )
            engine.add_element(element)
        
        # Add loads
        for load_data in model.loads:
            load = Load(
                id=load_data.id,
                node_id=load_data.node_id,
                element_id=load_data.element_id,
                type=load_data.type,
                direction=load_data.direction,
                values=load_data.values
            )
            engine.add_load(load)
        
        # Add constraints
        for constraint_data in model.constraints:
            constraint = Constraint(
                id=constraint_data.id,
                node_id=constraint_data.node_id,
                dofs=constraint_data.dofs,
                values=constraint_data.values
            )
            engine.add_constraint(constraint)
    
    except Exception as e:
        logger.error(f"Failed to build model: {e}")
        raise