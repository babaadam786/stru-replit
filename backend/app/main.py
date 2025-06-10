"""
FastAPI Backend for StructuralAI SaaS Platform
Main application entry point with API routes and WebSocket support.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import logging
from typing import List, Dict, Any, Optional
import json
import asyncio
from datetime import datetime

from .api import analysis, projects, ai_assistant, materials
from .core.fem_engine import FEMEngine
from .ai.llm_engine import StructuralLLM, EngineeringContext, PromptType
from .models.database import init_db
from .services.websocket_manager import WebSocketManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="StructuralAI",
    description="Advanced Structural Engineering SaaS Platform with AI Integration",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager for real-time collaboration
websocket_manager = WebSocketManager()

# Global instances
fem_engine = FEMEngine()
llm_engine = StructuralLLM()

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting StructuralAI backend...")
    
    # Initialize database
    await init_db()
    
    logger.info("StructuralAI backend started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down StructuralAI backend...")

# Include API routers
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(ai_assistant.router, prefix="/api/ai", tags=["AI Assistant"])
app.include_router(materials.router, prefix="/api/materials", tags=["Materials"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "StructuralAI Backend API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "fem_engine": "operational",
            "llm_engine": "operational" if llm_engine.model is not None else "limited",
            "database": "operational"
        }
    }

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time collaboration"""
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message["type"] == "model_update":
                # Broadcast model updates to other clients
                await websocket_manager.broadcast_to_others(
                    json.dumps({
                        "type": "model_update",
                        "data": message["data"],
                        "sender": client_id,
                        "timestamp": datetime.now().isoformat()
                    }),
                    exclude_client=client_id
                )
            
            elif message["type"] == "analysis_request":
                # Handle analysis requests
                try:
                    # Process analysis in background
                    result = await process_analysis_request(message["data"])
                    await websocket.send_text(json.dumps({
                        "type": "analysis_result",
                        "data": result,
                        "timestamp": datetime.now().isoformat()
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": str(e),
                        "timestamp": datetime.now().isoformat()
                    }))
            
            elif message["type"] == "ai_query":
                # Handle AI assistant queries
                try:
                    response = await process_ai_query(message["data"])
                    await websocket.send_text(json.dumps({
                        "type": "ai_response",
                        "data": response,
                        "timestamp": datetime.now().isoformat()
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": str(e),
                        "timestamp": datetime.now().isoformat()
                    }))
    
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)
        await websocket_manager.broadcast_to_others(
            json.dumps({
                "type": "user_disconnected",
                "user_id": client_id,
                "timestamp": datetime.now().isoformat()
            }),
            exclude_client=client_id
        )

async def process_analysis_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process structural analysis request"""
    try:
        analysis_type = data.get("analysis_type", "static")
        model_data = data.get("model", {})
        
        # Create new FEM engine instance for this analysis
        engine = FEMEngine()
        
        # Build model from data
        await build_fem_model(engine, model_data)
        
        # Run analysis
        if analysis_type == "static":
            result = engine.solve_static()
        elif analysis_type == "modal":
            num_modes = data.get("num_modes", 10)
            result = engine.solve_modal(num_modes)
        else:
            raise ValueError(f"Unsupported analysis type: {analysis_type}")
        
        return result
    
    except Exception as e:
        logger.error(f"Analysis request failed: {e}")
        return {"success": False, "error": str(e)}

async def process_ai_query(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process AI assistant query"""
    try:
        query = data.get("query", "")
        prompt_type = PromptType(data.get("prompt_type", "design_assistance"))
        context_data = data.get("context", {})
        
        # Create engineering context
        context = EngineeringContext(
            project_type=context_data.get("project_type", "building"),
            design_code=context_data.get("design_code", "AISC"),
            material_type=context_data.get("material_type", "steel"),
            analysis_type=context_data.get("analysis_type", "static")
        )
        
        # Process query
        query_result = llm_engine.process_engineering_query(query, prompt_type, context)
        
        if "error" in query_result:
            return {"success": False, "error": query_result["error"]}
        
        # Generate AI response
        response = await llm_engine.generate_response(query_result["prompt"], context)
        
        return {
            "success": True,
            "response": response,
            "context": context_data,
            "prompt_type": prompt_type.value
        }
    
    except Exception as e:
        logger.error(f"AI query failed: {e}")
        return {"success": False, "error": str(e)}

async def build_fem_model(engine: FEMEngine, model_data: Dict[str, Any]):
    """Build FEM model from JSON data"""
    try:
        # Add nodes
        for node_data in model_data.get("nodes", []):
            from .core.fem_engine import Node
            node = Node(
                id=node_data["id"],
                x=node_data["x"],
                y=node_data["y"],
                z=node_data.get("z", 0.0),
                dofs=node_data.get("dofs", [True] * 6)
            )
            engine.add_node(node)
        
        # Add materials
        for material_data in model_data.get("materials", []):
            from .core.fem_engine import Material
            material = Material(
                id=material_data["id"],
                name=material_data["name"],
                E=material_data["E"],
                nu=material_data["nu"],
                rho=material_data["rho"],
                fy=material_data.get("fy"),
                fu=material_data.get("fu")
            )
            engine.add_material(material)
        
        # Add sections
        for section_data in model_data.get("sections", []):
            from .core.fem_engine import Section
            section = Section(
                id=section_data["id"],
                name=section_data["name"],
                A=section_data["A"],
                Ix=section_data["Ix"],
                Iy=section_data["Iy"],
                Iz=section_data["Iz"],
                J=section_data["J"]
            )
            engine.add_section(section)
        
        # Add elements
        for element_data in model_data.get("elements", []):
            from .core.fem_engine import Element, ElementType
            element = Element(
                id=element_data["id"],
                type=ElementType(element_data["type"]),
                nodes=element_data["nodes"],
                material_id=element_data["material_id"],
                section_id=element_data.get("section_id")
            )
            engine.add_element(element)
        
        # Add loads
        for load_data in model_data.get("loads", []):
            from .core.fem_engine import Load
            load = Load(
                id=load_data["id"],
                node_id=load_data.get("node_id"),
                element_id=load_data.get("element_id"),
                type=load_data.get("type", "force"),
                direction=load_data.get("direction", "global"),
                values=load_data.get("values", [0.0] * 6)
            )
            engine.add_load(load)
        
        # Add constraints
        for constraint_data in model_data.get("constraints", []):
            from .core.fem_engine import Constraint
            constraint = Constraint(
                id=constraint_data["id"],
                node_id=constraint_data["node_id"],
                dofs=constraint_data["dofs"],
                values=constraint_data.get("values", [0.0] * 6)
            )
            engine.add_constraint(constraint)
    
    except Exception as e:
        logger.error(f"Failed to build FEM model: {e}")
        raise

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=12000,
        reload=True,
        log_level="info"
    )