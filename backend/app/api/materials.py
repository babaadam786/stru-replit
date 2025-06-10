"""
Materials API endpoints for managing material properties and databases
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

class MaterialModel(BaseModel):
    id: int
    name: str
    type: str  # steel, concrete, timber, etc.
    grade: str
    E: float  # Young's modulus (Pa)
    nu: float  # Poisson's ratio
    rho: float  # Density (kg/m³)
    fy: Optional[float] = None  # Yield strength (Pa)
    fu: Optional[float] = None  # Ultimate strength (Pa)
    fc: Optional[float] = None  # Compressive strength (Pa) - for concrete
    properties: Optional[Dict[str, Any]] = None

class SectionModel(BaseModel):
    id: int
    name: str
    type: str  # W, HSS, L, etc.
    material_type: str
    A: float  # Area (m²)
    Ix: float  # Moment of inertia about x-axis (m⁴)
    Iy: float  # Moment of inertia about y-axis (m⁴)
    Iz: float  # Moment of inertia about z-axis (m⁴)
    J: float  # Torsional constant (m⁴)
    Sy: Optional[float] = None  # Section modulus y (m³)
    Sz: Optional[float] = None  # Section modulus z (m³)
    dimensions: Optional[Dict[str, float]] = None

# Material database
materials_db: Dict[int, MaterialModel] = {
    1: MaterialModel(
        id=1, name="A992", type="steel", grade="A992",
        E=200e9, nu=0.3, rho=7850, fy=345e6, fu=450e6
    ),
    2: MaterialModel(
        id=2, name="A36", type="steel", grade="A36",
        E=200e9, nu=0.3, rho=7850, fy=250e6, fu=400e6
    ),
    3: MaterialModel(
        id=3, name="Normal Weight Concrete", type="concrete", grade="4000psi",
        E=25e9, nu=0.2, rho=2400, fc=28e6
    ),
    4: MaterialModel(
        id=4, name="High Strength Concrete", type="concrete", grade="8000psi",
        E=35e9, nu=0.2, rho=2400, fc=55e6
    ),
    5: MaterialModel(
        id=5, name="Douglas Fir", type="timber", grade="Select Structural",
        E=13e9, nu=0.3, rho=500, fy=12e6
    )
}

# Section database
sections_db: Dict[int, SectionModel] = {
    1: SectionModel(
        id=1, name="W12x26", type="W", material_type="steel",
        A=7.65e-3, Ix=204e-6, Iy=17.3e-6, Iz=17.3e-6, J=0.457e-6,
        Sy=33.4e-6, Sz=5.34e-6,
        dimensions={"d": 0.311, "bf": 0.165, "tf": 0.0095, "tw": 0.0061}
    ),
    2: SectionModel(
        id=2, name="W18x50", type="W", material_type="steel",
        A=14.7e-3, Ix=800e-6, Iy=40.1e-6, Iz=40.1e-6, J=1.04e-6,
        Sy=88.9e-6, Sz=12.1e-6,
        dimensions={"d": 0.459, "bf": 0.190, "tf": 0.0127, "tw": 0.0089}
    ),
    3: SectionModel(
        id=3, name="HSS8x8x1/2", type="HSS", material_type="steel",
        A=14.4e-3, Ix=347e-6, Iy=347e-6, Iz=347e-6, J=555e-6,
        dimensions={"B": 0.203, "H": 0.203, "t": 0.0127}
    )
}

@router.get("/materials", response_model=List[MaterialModel])
async def get_materials(material_type: Optional[str] = None):
    """Get all materials or filter by type"""
    materials = list(materials_db.values())
    
    if material_type:
        materials = [m for m in materials if m.type.lower() == material_type.lower()]
    
    return materials

@router.get("/materials/{material_id}", response_model=MaterialModel)
async def get_material(material_id: int):
    """Get specific material by ID"""
    if material_id not in materials_db:
        raise HTTPException(status_code=404, detail="Material not found")
    
    return materials_db[material_id]

@router.post("/materials", response_model=MaterialModel)
async def create_material(material: MaterialModel):
    """Create new material"""
    if material.id in materials_db:
        raise HTTPException(status_code=400, detail="Material ID already exists")
    
    materials_db[material.id] = material
    return material

@router.put("/materials/{material_id}", response_model=MaterialModel)
async def update_material(material_id: int, material: MaterialModel):
    """Update existing material"""
    if material_id not in materials_db:
        raise HTTPException(status_code=404, detail="Material not found")
    
    material.id = material_id  # Ensure ID consistency
    materials_db[material_id] = material
    return material

@router.delete("/materials/{material_id}")
async def delete_material(material_id: int):
    """Delete material"""
    if material_id not in materials_db:
        raise HTTPException(status_code=404, detail="Material not found")
    
    del materials_db[material_id]
    return {"message": "Material deleted successfully"}

@router.get("/sections", response_model=List[SectionModel])
async def get_sections(section_type: Optional[str] = None, material_type: Optional[str] = None):
    """Get all sections or filter by type/material"""
    sections = list(sections_db.values())
    
    if section_type:
        sections = [s for s in sections if s.type.upper() == section_type.upper()]
    
    if material_type:
        sections = [s for s in sections if s.material_type.lower() == material_type.lower()]
    
    return sections

@router.get("/sections/{section_id}", response_model=SectionModel)
async def get_section(section_id: int):
    """Get specific section by ID"""
    if section_id not in sections_db:
        raise HTTPException(status_code=404, detail="Section not found")
    
    return sections_db[section_id]

@router.post("/sections", response_model=SectionModel)
async def create_section(section: SectionModel):
    """Create new section"""
    if section.id in sections_db:
        raise HTTPException(status_code=400, detail="Section ID already exists")
    
    sections_db[section.id] = section
    return section

@router.put("/sections/{section_id}", response_model=SectionModel)
async def update_section(section_id: int, section: SectionModel):
    """Update existing section"""
    if section_id not in sections_db:
        raise HTTPException(status_code=404, detail="Section not found")
    
    section.id = section_id  # Ensure ID consistency
    sections_db[section_id] = section
    return section

@router.delete("/sections/{section_id}")
async def delete_section(section_id: int):
    """Delete section"""
    if section_id not in sections_db:
        raise HTTPException(status_code=404, detail="Section not found")
    
    del sections_db[section_id]
    return {"message": "Section deleted successfully"}

@router.get("/material-types")
async def get_material_types():
    """Get available material types"""
    return {
        "material_types": [
            {"type": "steel", "description": "Structural steel"},
            {"type": "concrete", "description": "Reinforced concrete"},
            {"type": "timber", "description": "Structural timber"},
            {"type": "aluminum", "description": "Aluminum alloys"},
            {"type": "composite", "description": "Composite materials"}
        ]
    }

@router.get("/section-types")
async def get_section_types():
    """Get available section types"""
    return {
        "section_types": [
            {"type": "W", "description": "Wide flange beam"},
            {"type": "HSS", "description": "Hollow structural section"},
            {"type": "L", "description": "Angle section"},
            {"type": "C", "description": "Channel section"},
            {"type": "T", "description": "Tee section"},
            {"type": "RECT", "description": "Rectangular section"},
            {"type": "CIRC", "description": "Circular section"}
        ]
    }

@router.post("/calculate-properties")
async def calculate_section_properties(dimensions: Dict[str, float], section_type: str):
    """Calculate section properties from dimensions"""
    try:
        if section_type.upper() == "RECT":
            # Rectangular section
            b = dimensions.get("width", 0)
            h = dimensions.get("height", 0)
            
            if b <= 0 or h <= 0:
                raise HTTPException(status_code=400, detail="Invalid dimensions")
            
            A = b * h
            Ix = b * h**3 / 12
            Iy = h * b**3 / 12
            Iz = Ix + Iy
            J = min(b, h)**3 * max(b, h) / 3  # Approximate torsional constant
            
            return {
                "A": A,
                "Ix": Ix,
                "Iy": Iy,
                "Iz": Iz,
                "J": J,
                "section_type": section_type,
                "dimensions": dimensions
            }
        
        elif section_type.upper() == "CIRC":
            # Circular section
            d = dimensions.get("diameter", 0)
            
            if d <= 0:
                raise HTTPException(status_code=400, detail="Invalid diameter")
            
            r = d / 2
            A = 3.14159 * r**2
            I = 3.14159 * r**4 / 4
            J = 3.14159 * r**4 / 2
            
            return {
                "A": A,
                "Ix": I,
                "Iy": I,
                "Iz": 2 * I,
                "J": J,
                "section_type": section_type,
                "dimensions": dimensions
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Section type {section_type} not supported for calculation")
    
    except Exception as e:
        logger.error(f"Section property calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/design-values/{material_id}")
async def get_design_values(material_id: int, design_code: str = "AISC"):
    """Get design values for material based on code"""
    if material_id not in materials_db:
        raise HTTPException(status_code=404, detail="Material not found")
    
    material = materials_db[material_id]
    
    try:
        if material.type == "steel" and design_code.upper() == "AISC":
            # AISC design values
            design_values = {
                "Fy": material.fy,
                "Fu": material.fu,
                "E": material.E,
                "G": material.E / (2 * (1 + material.nu)),
                "phi_b": 0.9,  # Flexural resistance factor
                "phi_c": 0.9,  # Compression resistance factor
                "phi_t": 0.9,  # Tension resistance factor
                "phi_v": 0.9,  # Shear resistance factor
                "design_code": design_code
            }
        
        elif material.type == "concrete" and design_code.upper() == "ACI":
            # ACI design values
            design_values = {
                "fc_prime": material.fc,
                "E": material.E,
                "phi_b": 0.9,  # Flexural resistance factor
                "phi_c": 0.65,  # Compression resistance factor
                "phi_s": 0.75,  # Shear resistance factor
                "design_code": design_code
            }
        
        else:
            # Generic values
            design_values = {
                "E": material.E,
                "nu": material.nu,
                "rho": material.rho,
                "design_code": "Generic"
            }
            
            if material.fy:
                design_values["fy"] = material.fy
            if material.fu:
                design_values["fu"] = material.fu
            if material.fc:
                design_values["fc"] = material.fc
        
        return design_values
    
    except Exception as e:
        logger.error(f"Design values calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/database/export")
async def export_database():
    """Export materials and sections database"""
    return {
        "materials": list(materials_db.values()),
        "sections": list(sections_db.values()),
        "exported_at": datetime.now().isoformat()
    }

@router.post("/database/import")
async def import_database(data: Dict[str, Any]):
    """Import materials and sections database"""
    try:
        imported_count = {"materials": 0, "sections": 0}
        
        # Import materials
        if "materials" in data:
            for material_data in data["materials"]:
                material = MaterialModel(**material_data)
                materials_db[material.id] = material
                imported_count["materials"] += 1
        
        # Import sections
        if "sections" in data:
            for section_data in data["sections"]:
                section = SectionModel(**section_data)
                sections_db[section.id] = section
                imported_count["sections"] += 1
        
        return {
            "message": "Database imported successfully",
            "imported": imported_count,
            "imported_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Database import failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))