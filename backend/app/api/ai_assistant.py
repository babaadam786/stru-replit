"""
AI Assistant API endpoints for LLM-powered engineering assistance
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from ..ai.llm_engine import StructuralLLM, EngineeringContext, PromptType

logger = logging.getLogger(__name__)
router = APIRouter()

# Global LLM instance
llm_engine = StructuralLLM()

class EngineeringContextModel(BaseModel):
    project_type: str = "building"
    design_code: str = "AISC"
    material_type: str = "steel"
    analysis_type: str = "static"
    safety_factors: Optional[Dict[str, float]] = None

class AIQueryRequest(BaseModel):
    query: str
    prompt_type: str = "design_assistance"
    context: Optional[EngineeringContextModel] = None
    include_references: bool = True

class AIQueryResponse(BaseModel):
    success: bool
    response: str
    context: Optional[Dict[str, Any]] = None
    references: Optional[List[str]] = None
    timestamp: str
    error: Optional[str] = None

class CodeReferenceRequest(BaseModel):
    code: str
    topic: str

class MaterialPropertiesRequest(BaseModel):
    material_type: str
    grade: str

@router.post("/query", response_model=AIQueryResponse)
async def ai_query(request: AIQueryRequest):
    """Process AI assistant query"""
    try:
        # Convert prompt type
        try:
            prompt_type = PromptType(request.prompt_type)
        except ValueError:
            prompt_type = PromptType.DESIGN_ASSISTANCE
        
        # Create engineering context
        context = None
        if request.context:
            context = EngineeringContext(
                project_type=request.context.project_type,
                design_code=request.context.design_code,
                material_type=request.context.material_type,
                analysis_type=request.context.analysis_type,
                safety_factors=request.context.safety_factors
            )
        
        # Process query
        query_result = llm_engine.process_engineering_query(
            request.query, prompt_type, context
        )
        
        if "error" in query_result:
            return AIQueryResponse(
                success=False,
                response="",
                error=query_result["error"],
                timestamp=datetime.now().isoformat()
            )
        
        # Generate AI response
        ai_response = await llm_engine.generate_response(
            query_result["prompt"], context
        )
        
        # Get code references if requested
        references = []
        if request.include_references and context:
            ref = llm_engine.get_code_reference(context.design_code, request.query)
            if ref:
                references.append(ref)
        
        return AIQueryResponse(
            success=True,
            response=ai_response,
            context=request.context.dict() if request.context else None,
            references=references if references else None,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"AI query failed: {e}")
        return AIQueryResponse(
            success=False,
            response="",
            error=str(e),
            timestamp=datetime.now().isoformat()
        )

@router.post("/code-reference")
async def get_code_reference(request: CodeReferenceRequest):
    """Get code reference for specific topic"""
    try:
        reference = llm_engine.get_code_reference(request.code, request.topic)
        
        if reference:
            return {
                "success": True,
                "reference": reference,
                "code": request.code,
                "topic": request.topic
            }
        else:
            return {
                "success": False,
                "message": f"No reference found for {request.topic} in {request.code}"
            }
    
    except Exception as e:
        logger.error(f"Code reference lookup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/material-properties")
async def get_material_properties(request: MaterialPropertiesRequest):
    """Get material properties from database"""
    try:
        properties = llm_engine.get_material_properties(
            request.material_type, request.grade
        )
        
        if properties:
            return {
                "success": True,
                "properties": properties,
                "material_type": request.material_type,
                "grade": request.grade
            }
        else:
            return {
                "success": False,
                "message": f"No properties found for {request.grade} {request.material_type}"
            }
    
    except Exception as e:
        logger.error(f"Material properties lookup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prompt-types")
async def get_prompt_types():
    """Get available prompt types"""
    return {
        "prompt_types": [
            {
                "value": prompt_type.value,
                "name": prompt_type.value.replace("_", " ").title(),
                "description": get_prompt_description(prompt_type)
            }
            for prompt_type in PromptType
        ]
    }

@router.get("/design-codes")
async def get_design_codes():
    """Get available design codes"""
    return {
        "design_codes": [
            {
                "code": "AISC",
                "name": "American Institute of Steel Construction",
                "version": "AISC 360-16",
                "material": "steel"
            },
            {
                "code": "ACI",
                "name": "American Concrete Institute",
                "version": "ACI 318-19",
                "material": "concrete"
            },
            {
                "code": "Eurocode",
                "name": "European Standards",
                "version": "EN 1993-1-1",
                "material": "steel"
            }
        ]
    }

@router.get("/material-database")
async def get_material_database():
    """Get available materials from database"""
    return {
        "materials": llm_engine.material_database
    }

@router.post("/design-assistance")
async def design_assistance(request: AIQueryRequest):
    """Specialized endpoint for design assistance"""
    request.prompt_type = "design_assistance"
    return await ai_query(request)

@router.post("/code-checking")
async def code_checking(request: AIQueryRequest):
    """Specialized endpoint for code checking"""
    request.prompt_type = "code_checking"
    return await ai_query(request)

@router.post("/optimization")
async def optimization_assistance(request: AIQueryRequest):
    """Specialized endpoint for optimization assistance"""
    request.prompt_type = "optimization"
    return await ai_query(request)

@router.post("/analysis-interpretation")
async def analysis_interpretation(request: AIQueryRequest):
    """Specialized endpoint for analysis interpretation"""
    request.prompt_type = "analysis_interpretation"
    return await ai_query(request)

@router.get("/status")
async def ai_status():
    """Get AI assistant status"""
    return {
        "status": "operational" if llm_engine.model is not None else "limited",
        "model_name": llm_engine.model_name,
        "use_ollama": llm_engine.use_ollama,
        "capabilities": {
            "design_assistance": True,
            "code_checking": True,
            "optimization": True,
            "analysis_interpretation": True,
            "material_selection": True,
            "load_estimation": True
        }
    }

def get_prompt_description(prompt_type: PromptType) -> str:
    """Get description for prompt type"""
    descriptions = {
        PromptType.DESIGN_ASSISTANCE: "Get help with structural design questions and methodology",
        PromptType.CODE_CHECKING: "Check compliance with design codes and standards",
        PromptType.OPTIMIZATION: "Get suggestions for design optimization",
        PromptType.ANALYSIS_INTERPRETATION: "Understand and interpret analysis results",
        PromptType.MATERIAL_SELECTION: "Get guidance on material selection",
        PromptType.LOAD_ESTIMATION: "Estimate structural loads and load combinations"
    }
    return descriptions.get(prompt_type, "General engineering assistance")