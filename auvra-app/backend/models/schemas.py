"""
Pydantic models for request/response validation
Auvra Hormone Assessment System
"""

from pydantic import BaseModel, Field, validator
from typing import List, Literal, Optional, Dict
from datetime import date

# ==================== LLM RESPONSE MODELS ====================

class HormoneImpact(BaseModel):
    """Model for individual hormone impact from LLM"""
    hormone: Literal["estrogen", "progesterone", "androgens", "insulin", "cortisol", "thyroid"]
    direction: Literal["high", "low"]
    score_weight: int = Field(ge=0, le=3)
    reasoning: str = Field(min_length=10, max_length=500)
    
    @validator('reasoning')
    def reasoning_must_be_clinical(cls, v):
        if len(v.split()) < 5:
            raise ValueError('Reasoning must be substantive (at least 5 words)')
        return v

class LLMScoringResponse(BaseModel):
    """Response from Gemini API for 'Others' input processing"""
    hormone_impacts: List[HormoneImpact]
    overall_confidence: Literal["high", "medium", "low"]
    clinical_flags: List[str] = []
    needs_medical_review: bool
    
    @validator('hormone_impacts')
    def no_duplicate_hormones(cls, v):
        hormones = [impact.hormone for impact in v]
        if len(hormones) != len(set(hormones)):
            raise ValueError('Cannot score same hormone twice')
        return v
    
    class Config:
        extra = 'forbid'  # Reject any additional fields

# ==================== ASSESSMENT REQUEST MODELS ====================

class BasicInfoRequest(BaseModel):
    """Question 1: Basic user information"""
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=18, le=40)

class PeriodPatternRequest(BaseModel):
    """Question 2: Period pattern and birth control
    Added 'not_sure' to allow user uncertainty (UI supports this). 'not_sure' contributes no score and slightly reduces confidence.
    """
    period_pattern: Literal["regular", "irregular", "occasional_skips", "no_periods", "not_sure"]
    birth_control: Literal["hormonal_pills", "hormonal_iud", "copper_iud", "none"]

class CycleDetailsRequest(BaseModel):
    """Question 3: Cycle details"""
    last_period_date: Optional[date] = None
    date_not_sure: bool = False
    cycle_length: Literal["<21", "21-25", "26-30", "31-35", "35+", "not_sure"]

class HealthConcernsRequest(BaseModel):
    """Question 4: Multi-select health concerns"""
    period_concerns: List[Literal["irregular_periods", "painful_periods", "light_periods", "heavy_periods"]] = []
    body_concerns: List[Literal["bloating", "hot_flashes", "nausea", "weight_difficulty", "recent_weight_gain", "menstrual_headaches"]] = []
    skin_hair_concerns: List[Literal["hirsutism", "hair_thinning", "adult_acne"]] = []
    mental_health_concerns: List[Literal["mood_swings", "stress", "fatigue"]] = []
    others: Optional[str] = None  # Custom health concerns to send to LLM
    none: bool = False  # Flag if user selected "none of these"

class TopConcernRequest(BaseModel):
    """Question 5: Top concern selection"""
    top_concern: str = Field(min_length=1)

class DiagnosedConditionsRequest(BaseModel):
    """Question 6: Diagnosed conditions"""
    conditions: List[Literal["pcos", "pcod", "endometriosis", "dysmenorrhea", "amenorrhea", 
                            "menorrhagia", "metrorrhagia", "pms", "pmdd", 
                            "hashimotos", "hypothyroidism"]] = []
    others_input: Optional[str] = None

class LabResultsRequest(BaseModel):
    """Lab results manual entry"""
    total_testosterone: Optional[float] = None
    free_testosterone: Optional[float] = None
    dhea_s: Optional[float] = None
    lh: Optional[float] = None
    fsh: Optional[float] = None
    tsh: Optional[float] = None
    free_t3: Optional[float] = None
    free_t4: Optional[float] = None
    fasting_insulin: Optional[float] = None
    hba1c: Optional[float] = None
    fasting_glucose: Optional[float] = None
    am_cortisol: Optional[float] = None
    estradiol: Optional[float] = None
    progesterone: Optional[float] = None
    shbg: Optional[float] = None

class CompleteAssessmentRequest(BaseModel):
    """Complete assessment submission"""
    basic_info: BasicInfoRequest
    period_pattern: PeriodPatternRequest
    cycle_details: CycleDetailsRequest
    health_concerns: HealthConcernsRequest
    top_concern: TopConcernRequest
    diagnosed_conditions: DiagnosedConditionsRequest
    lab_results: Optional[LabResultsRequest] = None

# ==================== ASSESSMENT RESPONSE MODELS ====================

class HormoneBreakdown(BaseModel):
    """Breakdown of hormone scores by source"""
    from_symptoms: int
    from_diagnosis: int
    from_labs: int

class HormoneScore(BaseModel):
    """Complete hormone score information"""
    total: int
    direction: Literal["high", "low"]
    breakdown: HormoneBreakdown

class HormoneImbalance(BaseModel):
    """Detailed hormone imbalance information"""
    hormone: str
    direction: Literal["high", "low"]
    total_score: int
    breakdown: HormoneBreakdown
    contributing_factors: List[str]
    explanation: str
    recommendations: Dict[str, List[str]]

class ConfidenceFactor(BaseModel):
    """Individual confidence calculation factor"""
    factor: str
    points: int

class Confidence(BaseModel):
    """Assessment confidence information"""
    level: Literal["high", "medium", "low"]
    score: int
    calculation_breakdown: List[ConfidenceFactor]
    recommendation: str

class Conflict(BaseModel):
    """Detected conflict in assessment"""
    type: Literal["symptom_mismatch", "hormone_direction", "diagnosis_mismatch", "lab_symptom_mismatch"]
    severity: Literal["low", "moderate", "high"]
    description: str
    recommendation: str
    impact_on_confidence: int

class ClinicalFlag(BaseModel):
    """Clinical flag or recommendation"""
    flag_type: Literal["testing_recommended", "urgent_medical", "cycle_tracking", "general_recommendation"]
    urgency: Literal["low", "moderate", "high"]
    message: str

class CycleContext(BaseModel):
    """Menstrual cycle context information"""
    current_phase: Optional[str] = None
    days_since_period: Optional[int] = None
    phase_confidence: Literal["high", "medium", "low"]
    estimated_next_period: Optional[date] = None

class UserProfile(BaseModel):
    """User profile summary"""
    age: int
    last_period_date: Optional[date]
    cycle_length: str
    birth_control: str
    diagnosed_conditions: List[str]

class AssessmentMetadata(BaseModel):
    """Assessment metadata"""
    user_id: str
    assessment_date: date
    version: str
    disclaimer: str

class NextSteps(BaseModel):
    """Recommended next steps"""
    immediate: List[str]
    short_term: List[str]
    long_term: List[str]

class AssessmentResponse(BaseModel):
    """Complete assessment result response"""
    assessment_metadata: AssessmentMetadata
    user_profile: UserProfile
    cycle_context: CycleContext
    primary_imbalance: HormoneImbalance
    secondary_imbalances: List[HormoneImbalance]
    all_hormone_scores: Dict[str, HormoneScore]
    confidence: Confidence
    conflicts: List[Conflict]
    clinical_flags: List[ClinicalFlag]
    next_steps: NextSteps
