"""
Projects API endpoints for managing structural engineering projects
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage (in production, use database)
projects_db: Dict[str, Dict[str, Any]] = {}

class ProjectModel(BaseModel):
    name: str
    description: Optional[str] = None
    project_type: str = "building"
    design_code: str = "AISC"
    location: Optional[str] = None
    client: Optional[str] = None
    engineer: Optional[str] = None
    tags: List[str] = []

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    project_type: str
    design_code: str
    location: Optional[str]
    client: Optional[str]
    engineer: Optional[str]
    tags: List[str]
    created_at: str
    updated_at: str
    model_data: Optional[Dict[str, Any]] = None
    analysis_results: List[str] = []

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    project_type: Optional[str] = None
    design_code: Optional[str] = None
    location: Optional[str] = None
    client: Optional[str] = None
    engineer: Optional[str] = None
    tags: Optional[List[str]] = None
    model_data: Optional[Dict[str, Any]] = None

@router.post("/", response_model=ProjectResponse)
async def create_project(project: ProjectModel):
    """Create a new project"""
    try:
        project_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        project_data = {
            "id": project_id,
            "name": project.name,
            "description": project.description,
            "project_type": project.project_type,
            "design_code": project.design_code,
            "location": project.location,
            "client": project.client,
            "engineer": project.engineer,
            "tags": project.tags,
            "created_at": timestamp,
            "updated_at": timestamp,
            "model_data": None,
            "analysis_results": []
        }
        
        projects_db[project_id] = project_data
        
        return ProjectResponse(**project_data)
    
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    project_type: Optional[str] = None,
    design_code: Optional[str] = None,
    tags: Optional[str] = None
):
    """List all projects with optional filtering"""
    try:
        projects = list(projects_db.values())
        
        # Apply filters
        if project_type:
            projects = [p for p in projects if p["project_type"] == project_type]
        
        if design_code:
            projects = [p for p in projects if p["design_code"] == design_code]
        
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            projects = [
                p for p in projects 
                if any(tag in p["tags"] for tag in tag_list)
            ]
        
        return [ProjectResponse(**project) for project in projects]
    
    except Exception as e:
        logger.error(f"Failed to list projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """Get a specific project"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ProjectResponse(**projects_db[project_id])

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, update: ProjectUpdate):
    """Update a project"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        project_data = projects_db[project_id]
        
        # Update fields
        update_dict = update.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if value is not None:
                project_data[field] = value
        
        project_data["updated_at"] = datetime.now().isoformat()
        
        return ProjectResponse(**project_data)
    
    except Exception as e:
        logger.error(f"Failed to update project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    del projects_db[project_id]
    return {"message": "Project deleted successfully"}

@router.post("/{project_id}/model")
async def save_model(project_id: str, model_data: Dict[str, Any]):
    """Save structural model data to project"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        projects_db[project_id]["model_data"] = model_data
        projects_db[project_id]["updated_at"] = datetime.now().isoformat()
        
        return {"message": "Model saved successfully"}
    
    except Exception as e:
        logger.error(f"Failed to save model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}/model")
async def get_model(project_id: str):
    """Get structural model data from project"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    model_data = projects_db[project_id].get("model_data")
    if model_data is None:
        raise HTTPException(status_code=404, detail="No model data found")
    
    return {"model_data": model_data}

@router.post("/{project_id}/analysis/{analysis_id}")
async def link_analysis(project_id: str, analysis_id: str):
    """Link analysis results to project"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        if analysis_id not in projects_db[project_id]["analysis_results"]:
            projects_db[project_id]["analysis_results"].append(analysis_id)
            projects_db[project_id]["updated_at"] = datetime.now().isoformat()
        
        return {"message": "Analysis linked successfully"}
    
    except Exception as e:
        logger.error(f"Failed to link analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{project_id}/analysis/{analysis_id}")
async def unlink_analysis(project_id: str, analysis_id: str):
    """Unlink analysis results from project"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        if analysis_id in projects_db[project_id]["analysis_results"]:
            projects_db[project_id]["analysis_results"].remove(analysis_id)
            projects_db[project_id]["updated_at"] = datetime.now().isoformat()
        
        return {"message": "Analysis unlinked successfully"}
    
    except Exception as e:
        logger.error(f"Failed to unlink analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}/export")
async def export_project(project_id: str, format: str = "json"):
    """Export project data"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        project_data = projects_db[project_id]
        
        if format.lower() == "json":
            return {
                "format": "json",
                "data": project_data,
                "exported_at": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
    
    except Exception as e:
        logger.error(f"Failed to export project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import")
async def import_project(project_data: Dict[str, Any]):
    """Import project data"""
    try:
        # Validate required fields
        required_fields = ["name", "project_type", "design_code"]
        for field in required_fields:
            if field not in project_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Generate new ID and timestamps
        project_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        imported_project = {
            "id": project_id,
            "name": project_data["name"],
            "description": project_data.get("description"),
            "project_type": project_data["project_type"],
            "design_code": project_data["design_code"],
            "location": project_data.get("location"),
            "client": project_data.get("client"),
            "engineer": project_data.get("engineer"),
            "tags": project_data.get("tags", []),
            "created_at": timestamp,
            "updated_at": timestamp,
            "model_data": project_data.get("model_data"),
            "analysis_results": []  # Don't import analysis results
        }
        
        projects_db[project_id] = imported_project
        
        return {
            "message": "Project imported successfully",
            "project_id": project_id,
            "project": ProjectResponse(**imported_project)
        }
    
    except Exception as e:
        logger.error(f"Failed to import project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}/statistics")
async def get_project_statistics(project_id: str):
    """Get project statistics"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        project_data = projects_db[project_id]
        model_data = project_data.get("model_data", {})
        
        stats = {
            "project_info": {
                "created_at": project_data["created_at"],
                "updated_at": project_data["updated_at"],
                "project_type": project_data["project_type"],
                "design_code": project_data["design_code"]
            },
            "model_statistics": {
                "has_model": model_data is not None,
                "nodes": len(model_data.get("nodes", [])),
                "elements": len(model_data.get("elements", [])),
                "materials": len(model_data.get("materials", [])),
                "loads": len(model_data.get("loads", [])),
                "constraints": len(model_data.get("constraints", []))
            },
            "analysis_statistics": {
                "total_analyses": len(project_data["analysis_results"]),
                "analysis_ids": project_data["analysis_results"]
            }
        }
        
        return stats
    
    except Exception as e:
        logger.error(f"Failed to get project statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))