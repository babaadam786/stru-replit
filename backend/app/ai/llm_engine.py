"""
Local LLM Engine for Structural Engineering AI Assistant
Provides intelligent design assistance, code checking, and optimization suggestions.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import numpy as np

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logging.warning("Ollama not available. LLM features will be limited.")

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers not available. Using fallback LLM.")

logger = logging.getLogger(__name__)


class PromptType(Enum):
    DESIGN_ASSISTANCE = "design_assistance"
    CODE_CHECKING = "code_checking"
    OPTIMIZATION = "optimization"
    ANALYSIS_INTERPRETATION = "analysis_interpretation"
    MATERIAL_SELECTION = "material_selection"
    LOAD_ESTIMATION = "load_estimation"


@dataclass
class EngineeringContext:
    """Context information for engineering queries"""
    project_type: str = "building"  # building, bridge, industrial, etc.
    design_code: str = "AISC"  # AISC, Eurocode, etc.
    material_type: str = "steel"  # steel, concrete, timber, etc.
    analysis_type: str = "static"  # static, dynamic, seismic, etc.
    safety_factors: Dict[str, float] = None
    
    def __post_init__(self):
        if self.safety_factors is None:
            self.safety_factors = {"dead": 1.2, "live": 1.6, "wind": 1.0, "seismic": 1.0}


class StructuralLLM:
    """Local LLM for structural engineering assistance"""
    
    def __init__(self, model_name: str = "llama2", use_ollama: bool = True):
        self.model_name = model_name
        self.use_ollama = use_ollama and OLLAMA_AVAILABLE
        self.model = None
        self.tokenizer = None
        
        # Engineering knowledge base
        self.engineering_prompts = self._load_engineering_prompts()
        self.code_standards = self._load_code_standards()
        self.material_database = self._load_material_database()
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the LLM model"""
        try:
            if self.use_ollama:
                # Check if Ollama is running and model is available
                try:
                    ollama.list()
                    logger.info(f"Using Ollama with model: {self.model_name}")
                except Exception as e:
                    logger.warning(f"Ollama not available: {e}. Falling back to transformers.")
                    self.use_ollama = False
            
            if not self.use_ollama and TRANSFORMERS_AVAILABLE:
                # Use a smaller, local model for demonstration
                model_name = "microsoft/DialoGPT-medium"  # Lightweight alternative
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                    self.model = AutoModelForCausalLM.from_pretrained(model_name)
                    logger.info(f"Using Transformers with model: {model_name}")
                except Exception as e:
                    logger.error(f"Failed to load transformers model: {e}")
                    self.model = None
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            self.model = None
    
    def _load_engineering_prompts(self) -> Dict[str, str]:
        """Load engineering-specific prompt templates"""
        return {
            "design_assistance": """
You are an expert structural engineer. Help with the following design question:

Context: {context}
Question: {question}

Provide a detailed engineering response including:
1. Design approach and methodology
2. Relevant code requirements
3. Calculations or formulas if applicable
4. Safety considerations
5. Practical recommendations

Response:""",
            
            "code_checking": """
You are a structural engineering code compliance expert. Review the following design:

Design Code: {design_code}
Element Type: {element_type}
Design Parameters: {parameters}
Question: {question}

Check compliance with relevant code provisions and provide:
1. Applicable code sections
2. Required checks and calculations
3. Compliance status
4. Recommendations for non-compliance

Response:""",
            
            "optimization": """
You are a structural optimization expert. Analyze the following design for optimization opportunities:

Current Design: {current_design}
Constraints: {constraints}
Objectives: {objectives}
Question: {question}

Provide optimization recommendations including:
1. Design variables to consider
2. Optimization strategies
3. Trade-offs and considerations
4. Expected improvements

Response:""",
            
            "analysis_interpretation": """
You are an expert in structural analysis interpretation. Help interpret the following analysis results:

Analysis Type: {analysis_type}
Results Summary: {results}
Question: {question}

Provide interpretation including:
1. What the results mean
2. Critical values and their significance
3. Potential issues or concerns
4. Recommendations for design modifications

Response:""",
            
            "material_selection": """
You are a materials engineering expert. Help with material selection:

Application: {application}
Requirements: {requirements}
Environment: {environment}
Question: {question}

Provide material recommendations including:
1. Suitable material options
2. Properties comparison
3. Cost considerations
4. Availability and constructability

Response:""",
            
            "load_estimation": """
You are an expert in structural load estimation. Help estimate loads for:

Structure Type: {structure_type}
Location: {location}
Usage: {usage}
Question: {question}

Provide load estimates including:
1. Dead loads
2. Live loads
3. Environmental loads (wind, seismic, snow)
4. Load combinations
5. Code references

Response:"""
        }
    
    def _load_code_standards(self) -> Dict[str, Dict]:
        """Load structural design code standards"""
        return {
            "AISC": {
                "name": "American Institute of Steel Construction",
                "version": "AISC 360-16",
                "material": "steel",
                "key_provisions": {
                    "tension": "Chapter D",
                    "compression": "Chapter E",
                    "flexure": "Chapter F",
                    "shear": "Chapter G",
                    "combined": "Chapter H"
                }
            },
            "ACI": {
                "name": "American Concrete Institute",
                "version": "ACI 318-19",
                "material": "concrete",
                "key_provisions": {
                    "flexure": "Chapter 9",
                    "shear": "Chapter 9",
                    "compression": "Chapter 10",
                    "development": "Chapter 25"
                }
            },
            "Eurocode": {
                "name": "European Standards",
                "version": "EN 1993-1-1",
                "material": "steel",
                "key_provisions": {
                    "resistance": "Section 6",
                    "stability": "Section 6",
                    "fatigue": "Section 9"
                }
            }
        }
    
    def _load_material_database(self) -> Dict[str, Dict]:
        """Load material properties database"""
        return {
            "steel": {
                "A992": {"fy": 345e6, "fu": 450e6, "E": 200e9, "rho": 7850},
                "A36": {"fy": 250e6, "fu": 400e6, "E": 200e9, "rho": 7850},
                "A572_Gr50": {"fy": 345e6, "fu": 450e6, "E": 200e9, "rho": 7850}
            },
            "concrete": {
                "normal_weight": {"fc": 28e6, "E": 25e9, "rho": 2400},
                "high_strength": {"fc": 55e6, "E": 35e9, "rho": 2400},
                "lightweight": {"fc": 21e6, "E": 20e9, "rho": 1800}
            },
            "timber": {
                "douglas_fir": {"fb": 12e6, "E": 13e9, "rho": 500},
                "southern_pine": {"fb": 14e6, "E": 14e9, "rho": 550}
            }
        }
    
    async def generate_response(self, prompt: str, context: EngineeringContext = None) -> str:
        """Generate AI response for engineering query"""
        try:
            if self.use_ollama:
                return await self._generate_ollama_response(prompt, context)
            elif self.model is not None:
                return await self._generate_transformers_response(prompt, context)
            else:
                return self._generate_fallback_response(prompt, context)
        
        except Exception as e:
            logger.error(f"Failed to generate AI response: {e}")
            return f"I apologize, but I encountered an error processing your request: {str(e)}"
    
    async def _generate_ollama_response(self, prompt: str, context: EngineeringContext) -> str:
        """Generate response using Ollama"""
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "temperature": 0.3,  # Lower temperature for more focused responses
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
            )
            return response['response']
        
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return self._generate_fallback_response(prompt, context)
    
    async def _generate_transformers_response(self, prompt: str, context: EngineeringContext) -> str:
        """Generate response using Transformers"""
        try:
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 200,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Remove the input prompt from response
            response = response[len(prompt):].strip()
            
            return response if response else self._generate_fallback_response(prompt, context)
        
        except Exception as e:
            logger.error(f"Transformers generation failed: {e}")
            return self._generate_fallback_response(prompt, context)
    
    def _generate_fallback_response(self, prompt: str, context: EngineeringContext) -> str:
        """Generate rule-based fallback response"""
        # Extract key engineering terms and provide relevant information
        prompt_lower = prompt.lower()
        
        if any(term in prompt_lower for term in ["beam", "flexure", "bending"]):
            return self._beam_design_guidance(prompt, context)
        elif any(term in prompt_lower for term in ["column", "compression", "buckling"]):
            return self._column_design_guidance(prompt, context)
        elif any(term in prompt_lower for term in ["connection", "bolt", "weld"]):
            return self._connection_design_guidance(prompt, context)
        elif any(term in prompt_lower for term in ["load", "force", "pressure"]):
            return self._load_estimation_guidance(prompt, context)
        elif any(term in prompt_lower for term in ["material", "steel", "concrete"]):
            return self._material_selection_guidance(prompt, context)
        else:
            return self._general_engineering_guidance(prompt, context)
    
    def _beam_design_guidance(self, prompt: str, context: EngineeringContext) -> str:
        """Provide beam design guidance"""
        if context and context.material_type == "steel":
            return """
For steel beam design, consider the following key aspects:

1. **Flexural Strength**: Check moment capacity (Mp = Fy × Z for compact sections)
2. **Shear Strength**: Verify shear capacity (Vn = 0.6 × Fy × Aw × Cv)
3. **Lateral-Torsional Buckling**: Ensure adequate lateral support
4. **Deflection**: Check serviceability limits (L/360 for live load)
5. **Web Crippling**: Verify local stability at supports and load points

Key AISC provisions:
- Chapter F: Flexural members
- Chapter G: Shear members
- Appendix 1: Design aids

Recommended approach:
1. Determine loads and load combinations
2. Select trial section
3. Check strength and serviceability
4. Optimize if necessary
"""
        else:
            return """
For beam design, key considerations include:

1. **Moment Capacity**: Ensure adequate flexural strength
2. **Shear Capacity**: Check shear resistance
3. **Deflection Control**: Limit deflections for serviceability
4. **Lateral Stability**: Provide adequate bracing
5. **Local Stability**: Check web and flange stability

Follow applicable design codes and consider:
- Load combinations
- Material properties
- Section properties
- Support conditions
"""
    
    def _column_design_guidance(self, prompt: str, context: EngineeringContext) -> str:
        """Provide column design guidance"""
        return """
For column design, consider these critical aspects:

1. **Axial Capacity**: Check compression strength
   - For steel: Pn = Fcr × Ag (AISC Chapter E)
   - Consider elastic/inelastic buckling

2. **Buckling Analysis**:
   - Determine effective length (K factor)
   - Calculate slenderness ratio
   - Check local and global buckling

3. **Combined Loading**:
   - Interaction equations for axial + bending
   - P-M interaction diagrams

4. **Design Steps**:
   - Calculate design loads
   - Determine effective lengths
   - Select trial section
   - Check capacity and stability
   - Verify code compliance

5. **Special Considerations**:
   - Seismic design requirements
   - Fire resistance
   - Connection design
"""
    
    def _connection_design_guidance(self, prompt: str, context: EngineeringContext) -> str:
        """Provide connection design guidance"""
        return """
For connection design, key considerations:

1. **Force Transfer**: Ensure adequate capacity for all forces
2. **Bolt Design**: Check shear, tension, and bearing
3. **Weld Design**: Size welds for applied forces
4. **Base Material**: Verify plate and member capacity

**Bolted Connections**:
- Shear strength: Rn = Fnv × Ab
- Tension strength: Rn = Fnt × Ab
- Bearing strength: Check bolt hole deformation

**Welded Connections**:
- Fillet welds: Rn = 0.6 × FEXX × Aw
- Complete penetration: Full base material strength

**Design Process**:
1. Determine connection forces
2. Select connection type
3. Size fasteners/welds
4. Check all limit states
5. Detail for constructability
"""
    
    def _load_estimation_guidance(self, prompt: str, context: EngineeringContext) -> str:
        """Provide load estimation guidance"""
        return """
For structural load estimation:

1. **Dead Loads**:
   - Self-weight of structure
   - Permanent equipment and finishes
   - Typical values: 3-6 psf for floors, 10-20 psf for roofs

2. **Live Loads** (per building codes):
   - Offices: 50 psf
   - Residential: 40 psf
   - Storage: 125+ psf
   - Roof live load: 20 psf minimum

3. **Environmental Loads**:
   - Wind: Use ASCE 7 wind maps
   - Seismic: Determine site class and design parameters
   - Snow: Based on ground snow load

4. **Load Combinations** (ASCE 7):
   - 1.4D
   - 1.2D + 1.6L
   - 1.2D + 1.0W + L
   - 0.9D ± 1.0W

5. **Special Considerations**:
   - Impact factors
   - Dynamic amplification
   - Load distribution
"""
    
    def _material_selection_guidance(self, prompt: str, context: EngineeringContext) -> str:
        """Provide material selection guidance"""
        materials = self.material_database.get(context.material_type if context else "steel", {})
        
        guidance = f"""
Material selection considerations for {context.material_type if context else 'structural'} applications:

**Key Properties**:
- Strength (yield and ultimate)
- Stiffness (modulus of elasticity)
- Ductility and toughness
- Durability and corrosion resistance

**Available Options**:
"""
        
        for material, props in materials.items():
            guidance += f"\n- {material}: "
            if "fy" in props:
                guidance += f"Fy = {props['fy']/1e6:.0f} MPa, "
            if "E" in props:
                guidance += f"E = {props['E']/1e9:.0f} GPa"
        
        guidance += """

**Selection Criteria**:
1. Structural requirements
2. Environmental conditions
3. Cost and availability
4. Constructability
5. Maintenance requirements

**Recommendations**:
- Use standard grades when possible
- Consider local availability
- Account for fabrication requirements
- Evaluate life-cycle costs
"""
        
        return guidance
    
    def _general_engineering_guidance(self, prompt: str, context: EngineeringContext) -> str:
        """Provide general engineering guidance"""
        return """
General structural engineering guidance:

1. **Design Philosophy**:
   - Follow applicable building codes
   - Use appropriate safety factors
   - Consider all limit states
   - Design for constructability

2. **Analysis Approach**:
   - Define loads and load paths
   - Model structure appropriately
   - Verify analysis results
   - Check for reasonableness

3. **Design Process**:
   - Conceptual design
   - Preliminary sizing
   - Detailed analysis
   - Final design and detailing

4. **Quality Assurance**:
   - Independent checking
   - Code compliance review
   - Constructability review
   - Documentation

5. **Best Practices**:
   - Use standard details when possible
   - Consider maintenance access
   - Plan for future modifications
   - Coordinate with other disciplines

For specific questions, please provide more details about your project requirements.
"""
    
    def process_engineering_query(self, query: str, prompt_type: PromptType, 
                                context: EngineeringContext = None) -> Dict[str, Any]:
        """Process engineering query with appropriate prompt template"""
        try:
            if context is None:
                context = EngineeringContext()
            
            # Select appropriate prompt template
            template = self.engineering_prompts.get(prompt_type.value, 
                                                  self.engineering_prompts["design_assistance"])
            
            # Format prompt with context
            formatted_prompt = template.format(
                context=self._format_context(context),
                question=query,
                design_code=context.design_code,
                element_type=getattr(context, 'element_type', 'general'),
                parameters=getattr(context, 'parameters', {}),
                current_design=getattr(context, 'current_design', {}),
                constraints=getattr(context, 'constraints', {}),
                objectives=getattr(context, 'objectives', 'minimize weight'),
                analysis_type=context.analysis_type,
                results=getattr(context, 'results', {}),
                application=getattr(context, 'application', context.project_type),
                requirements=getattr(context, 'requirements', {}),
                environment=getattr(context, 'environment', 'normal'),
                structure_type=context.project_type,
                location=getattr(context, 'location', 'general'),
                usage=getattr(context, 'usage', 'general')
            )
            
            return {
                "prompt": formatted_prompt,
                "context": context,
                "prompt_type": prompt_type.value
            }
            
        except Exception as e:
            logger.error(f"Failed to process engineering query: {e}")
            return {
                "error": str(e),
                "prompt": query,
                "context": context
            }
    
    def _format_context(self, context: EngineeringContext) -> str:
        """Format engineering context for prompt"""
        return f"""
Project Type: {context.project_type}
Design Code: {context.design_code}
Material: {context.material_type}
Analysis Type: {context.analysis_type}
Safety Factors: {context.safety_factors}
"""
    
    def get_code_reference(self, code: str, topic: str) -> Optional[str]:
        """Get relevant code reference for topic"""
        code_info = self.code_standards.get(code.upper())
        if code_info and topic.lower() in code_info.get("key_provisions", {}):
            provision = code_info["key_provisions"][topic.lower()]
            return f"{code_info['version']} - {provision}"
        return None
    
    def get_material_properties(self, material_type: str, grade: str) -> Optional[Dict]:
        """Get material properties from database"""
        materials = self.material_database.get(material_type.lower(), {})
        return materials.get(grade, None)