"""
Conflict Detection Service
Detects and reports conflicts in hormone assessments
"""

from typing import List, Dict
from models.schemas import Conflict


class ConflictDetector:
    """Detect conflicts in hormone assessment data"""
    
    def __init__(self):
        self.conflicts = []
    
    def detect_all_conflicts(
        self,
        hormone_scores: Dict,
        diagnosed_conditions: List[str],
        symptoms_by_hormone: Dict[str, int],
        labs_uploaded: bool,
        labs_concordance: str,
        birth_control: str
    ) -> List[Conflict]:
        """Detect all types of conflicts"""
        
        self.conflicts = []
        
        # 1. Hormone direction conflicts
        self._check_hormone_direction_conflicts(hormone_scores)
        
        # 2. Symptom-diagnosis mismatch
        self._check_diagnosis_symptom_mismatch(diagnosed_conditions, symptoms_by_hormone)
        
        # 3. Lab-symptom mismatch
        if labs_uploaded and labs_concordance == "low":
            self._check_lab_symptom_mismatch(hormone_scores)
        
        # 4. Birth control masking
        if birth_control in ["hormonal_pills", "hormonal_iud"]:
            self._check_birth_control_masking(diagnosed_conditions)
        
        return self.conflicts
    
    def _check_hormone_direction_conflicts(self, hormone_scores: Dict):
        """Check for conflicting hormone directions"""
        
        # Estrogen: Check if both high and low signals present
        if "estrogen" in hormone_scores:
            high_score = hormone_scores["estrogen"].get("high_score", 0)
            low_score = hormone_scores["estrogen"].get("low_score", 0)
            
            if high_score > 0 and low_score > 0:
                self.conflicts.append(Conflict(
                    type="hormone_direction",
                    severity="moderate",
                    description="Symptoms suggest both high estrogen (bloating, heavy periods) and low estrogen (light periods, hot flashes)",
                    recommendation="Test estradiol on Day 3-5 of cycle to clarify estrogen status. May indicate estrogen fluctuation throughout cycle.",
                    impact_on_confidence=-2
                ))
        
        # Cortisol: Check if both high and low signals present
        if "cortisol" in hormone_scores:
            high_score = hormone_scores["cortisol"].get("high_score", 0)
            low_score = hormone_scores["cortisol"].get("low_score", 0)
            
            if high_score > 0 and low_score > 0:
                self.conflicts.append(Conflict(
                    type="hormone_direction",
                    severity="moderate",
                    description="Symptoms suggest both high cortisol (stress, anxiety) and low cortisol (extreme fatigue)",
                    recommendation="Test AM and PM cortisol, or consider 4-point cortisol testing to assess HPA axis function throughout the day.",
                    impact_on_confidence=-2
                ))
    
    def _check_diagnosis_symptom_mismatch(self, diagnosed_conditions: List[str], symptoms_by_hormone: Dict):
        """Check for diagnosis-symptom mismatches"""
        
        # PCOS without androgen symptoms
        if "pcos" in diagnosed_conditions:
            androgen_symptoms = symptoms_by_hormone.get("androgens", 0)
            if androgen_symptoms == 0:
                self.conflicts.append(Conflict(
                    type="diagnosis_mismatch",
                    severity="low",
                    description="PCOS diagnosed but no androgen-related symptoms (hirsutism, acne) reported",
                    recommendation="You may have lean PCOS (non-hyperandrogenic phenotype) or PCOS may be well-controlled. Consider testing free testosterone and DHEA-S to clarify.",
                    impact_on_confidence=-1
                ))
        
        # Thyroid condition without thyroid symptoms
        if any(cond in diagnosed_conditions for cond in ["hashimotos", "hypothyroidism"]):
            thyroid_symptoms = symptoms_by_hormone.get("thyroid", 0)
            if thyroid_symptoms == 0:
                self.conflicts.append(Conflict(
                    type="diagnosis_mismatch",
                    severity="low",
                    description="Thyroid condition diagnosed but no thyroid-related symptoms (fatigue, weight gain, hair loss) reported",
                    recommendation="Your thyroid condition may be well-managed with medication. Ensure TSH is being monitored regularly (target: 0.5-2.0 mIU/L for optimal symptom relief).",
                    impact_on_confidence=-1
                ))
        
        # Endometriosis without estrogen symptoms
        if "endometriosis" in diagnosed_conditions:
            estrogen_symptoms = symptoms_by_hormone.get("estrogen", 0)
            if estrogen_symptoms == 0:
                self.conflicts.append(Conflict(
                    type="diagnosis_mismatch",
                    severity="low",
                    description="Endometriosis diagnosed but no estrogen-related symptoms reported",
                    recommendation="Endometriosis may be well-controlled with treatment. Continue monitoring symptoms, especially around menstruation.",
                    impact_on_confidence=-1
                ))
    
    def _check_lab_symptom_mismatch(self, hormone_scores: Dict):
        """Check for lab-symptom discordance"""
        
        for hormone, data in hormone_scores.items():
            symptom_score = data.get("from_symptoms", 0)
            lab_score = data.get("from_labs", 0)
            
            # Symptoms present but labs normal
            if symptom_score >= 3 and lab_score == 0:
                hormone_name = hormone.capitalize()
                
                if hormone == "thyroid":
                    recommendation = "Consider testing Free T3, thyroid antibodies (TPO, TG), or other causes of symptoms (iron deficiency, vitamin D, sleep apnea)."
                elif hormone == "androgens":
                    recommendation = "Test free testosterone (more sensitive than total), DHEA-S, and consider checking SHBG which affects androgen bioavailability."
                elif hormone == "insulin":
                    recommendation = "Fasting insulin may be normal despite insulin resistance. Consider oral glucose tolerance test with insulin measurements or HOMA-IR calculation."
                else:
                    recommendation = f"Consider additional testing for {hormone} or investigate other potential causes of your symptoms."
                
                self.conflicts.append(Conflict(
                    type="lab_symptom_mismatch",
                    severity="moderate",
                    description=f"{hormone_name} symptoms present but lab results are within normal range",
                    recommendation=recommendation,
                    impact_on_confidence=-2
                ))
    
    def _check_birth_control_masking(self, diagnosed_conditions: List[str]):
        """Check if birth control may be masking symptoms"""
        
        if "pcos" in diagnosed_conditions:
            self.conflicts.append(Conflict(
                type="diagnosis_mismatch",
                severity="moderate",
                description="On hormonal birth control with PCOS diagnosis - symptoms may be masked",
                recommendation="Hormonal birth control suppresses natural hormone production and may mask underlying PCOS symptoms. Consider reassessment 3+ months after discontinuation if medically appropriate and trying to conceive.",
                impact_on_confidence=-1
            ))
