"""
Main FastAPI Application
Auvra Hormone Assessment API
"""

import os
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from models.schemas import CompleteAssessmentRequest, AssessmentResponse
from services.assessment_service import AssessmentService

# Initialize FastAPI app
app = FastAPI(
    title="Auvra Hormone Assessment API",
    description="AI-powered hormone assessment and analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize assessment service
gemini_api_key = os.getenv("GEMINI_API_KEY")
assessment_service = AssessmentService(gemini_api_key)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Auvra Hormone Assessment API",
        "version": "1.0"
    }


@app.post("/api/v1/assess", response_model=AssessmentResponse)
async def assess_hormones(assessment: CompleteAssessmentRequest, request: Request):
    """
    Complete hormone assessment endpoint
    Accepts full assessment data and returns detailed results
    """
    # Debug logging of incoming request payload (after successful model parsing)
    print("[ASSESS] Incoming payload parsed successfully:")
    try:
        print(assessment.model_dump())  # Pydantic v2 syntax
    except Exception:
        try:
            print(assessment.dict())  # fallback for older versions
        except Exception:
            print("[ASSESS] Could not dump assessment model")

    try:
        # Process assessment
        result = assessment_service.process_complete_assessment(assessment)
        print("[ASSESS] Assessment processed. Primary hormone:", result.primary_imbalance.hormone)
        return result
    except ValidationError as e:
        print("[ASSESS][ERROR] ValidationError during processing:")
        for err in e.errors():
            print("  -", err)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation error",
                "details": e.errors()
            }
        )
    except Exception as e:
        print(f"[ASSESS][ERROR] Unexpected exception: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": str(e)
            }
        )


@app.post("/api/v1/assess/quick")
async def quick_assess(data: dict):
    """
    Quick assessment endpoint for testing
    Minimal data required
    """
    try:
        from models.schemas import (
            BasicInfoRequest, PeriodPatternRequest, CycleDetailsRequest,
            HealthConcernsRequest, TopConcernRequest, DiagnosedConditionsRequest
        )
        
        quick_request = CompleteAssessmentRequest(
            basic_info=BasicInfoRequest(**data.get("basic_info", {})),
            period_pattern=PeriodPatternRequest(**data.get("period_pattern", {})),
            cycle_details=CycleDetailsRequest(**data.get("cycle_details", {})),
            health_concerns=HealthConcernsRequest(**data.get("health_concerns", {})),
            top_concern=TopConcernRequest(**data.get("top_concern", {})),
            diagnosed_conditions=DiagnosedConditionsRequest(**data.get("diagnosed_conditions", {})),
            lab_results=None
        )
        
        result = assessment_service.process_complete_assessment(quick_request)
        
        # Return simplified response
        return {
            "primary_hormone": result.primary_imbalance.hormone,
            "direction": result.primary_imbalance.direction,
            "confidence": result.confidence.level,
            "score": result.primary_imbalance.total_score
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e)}
        )


@app.post("/api/v1/validate/others")
async def validate_others_input(data: dict):
    """
    Validate and process 'Others' input with LLM
    Returns hormone impacts without full assessment
    """
    try:
        user_input = data.get("input", "")
        user_context = data.get("context", {})
        
        if not user_input:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Input is required"}
            )
        
        from services.llm_service import LLMService
        llm_service = LLMService(gemini_api_key)
        
        result = llm_service.process_others_input(user_input, user_context)
        return result.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e)}
        )


if __name__ == '__main__':
    import uvicorn
    
    port = int(os.getenv("PORT", 5000))
    
    print("=" * 60)
    print("🌸 AUVRA HORMONE ASSESSMENT API (FastAPI)")
    print("=" * 60)
    print(f"📡 Server running on: http://localhost:{port}")
    print(f"🤖 Gemini API: {'Configured ✓' if gemini_api_key else 'Not configured (using fallback)'}")
    print("=" * 60)
    print("\n📋 Available Endpoints:")
    print(f"  GET  /health                    - Health check")
    print(f"  POST /api/v1/assess             - Complete assessment")
    print(f"  POST /api/v1/assess/quick       - Quick assessment")
    print(f"  POST /api/v1/validate/others    - Validate custom input")
    print(f"  GET  /docs                      - Interactive API documentation (Swagger)")
    print(f"  GET  /redoc                     - Alternative API documentation (ReDoc)")
    print("=" * 60)
    print("\n🚀 Ready to receive requests!\n")
    
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=port,
        log_level="info"
    )
