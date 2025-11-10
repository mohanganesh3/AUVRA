"""
Main Assessment Service
Orchestrates the complete hormone assessment workflow
"""

from datetime import date
from typing import Dict, List, Optional
import uuid

from models.schemas import *
from services.hormone_scorer import HormoneScorer
from services.cycle_calculator import CycleCalculator
from services.confidence_calculator import ConfidenceCalculator
from services.conflict_detector import ConflictDetector
from services.explanation_generator import ExplanationGenerator
from services.llm_service import LLMService


class AssessmentService:
    """Main service for processing hormone assessments"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """Initialize assessment service"""
        self.llm_service = LLMService(gemini_api_key)
        self.explanation_generator = ExplanationGenerator()
    
    def process_complete_assessment(
        self, 
        assessment_request: CompleteAssessmentRequest
    ) -> AssessmentResponse:
        """Process complete hormone assessment"""
        trace_id = str(uuid.uuid4())[:8]
        print(f"\n========== AUVRA ASSESSMENT START [TRACE {trace_id}] ==========")
        print("[REQUEST] Basic Info:", assessment_request.basic_info.model_dump())
        print("[REQUEST] Period Pattern:", assessment_request.period_pattern.model_dump())
        print("[REQUEST] Cycle Details:", assessment_request.cycle_details.model_dump())
        print("[REQUEST] Health Concerns:", assessment_request.health_concerns.model_dump())
        print("[REQUEST] Diagnosed Conditions:", assessment_request.diagnosed_conditions.model_dump())
        if assessment_request.lab_results:
            print("[REQUEST] Lab Results Provided:", assessment_request.lab_results.model_dump())
        else:
            print("[REQUEST] Lab Results: NONE")
        
        # Initialize services
        hormone_scorer = HormoneScorer()
        cycle_calculator = CycleCalculator()
        confidence_calculator = ConfidenceCalculator()
        conflict_detector = ConflictDetector()
        
        # Step 1: Score period pattern
        print("[STEP 1] Scoring period pattern:", assessment_request.period_pattern.period_pattern)
        hormone_scorer.score_period_pattern(assessment_request.period_pattern.period_pattern)
        
        # Step 2: Apply birth control modifier
        print("[STEP 2] Applying birth control modifier:", assessment_request.period_pattern.birth_control)
        hormone_scorer.apply_birth_control_modifier(assessment_request.period_pattern.birth_control)
        
        # Step 3: Score cycle length
        print("[STEP 3] Scoring cycle length:", assessment_request.cycle_details.cycle_length)
        hormone_scorer.score_cycle_length(assessment_request.cycle_details.cycle_length)
        
        # Step 4: Calculate cycle context
        print("[STEP 4] Calculating cycle context...")
        cycle_context = cycle_calculator.calculate_cycle_context(
            assessment_request.cycle_details.last_period_date,
            assessment_request.cycle_details.cycle_length,
            assessment_request.cycle_details.date_not_sure
        )
        print("[CYCLE CONTEXT] Phase:", cycle_context.current_phase,
              "Days Since Period:", cycle_context.days_since_period,
              "Estimated Next Period:", cycle_context.estimated_next_period)
        
        # Step 5: Score health concerns with cycle phase awareness
        print("[STEP 5] Scoring health concerns with cycle phase awareness (phase:", cycle_context.current_phase, ")")
        hormone_scorer.score_health_concerns(
            assessment_request.health_concerns,
            cycle_context.current_phase
        )
        
        # Step 6: Apply top concern multiplier
        print("[STEP 6] Applying top concern multiplier:", assessment_request.top_concern.top_concern)
        hormone_scorer.apply_top_concern_multiplier(
            assessment_request.top_concern.top_concern,
            assessment_request.health_concerns
        )
        
        # Step 7: Score diagnosed conditions
        print("[STEP 7] Scoring diagnosed conditions:", assessment_request.diagnosed_conditions.conditions)
        hormone_scorer.score_diagnosed_conditions(
            assessment_request.diagnosed_conditions.conditions
        )
        
        # Step 8: Process BOTH "Others" inputs with LLM in a SINGLE API call (if provided)
        llm_confidence = None
        clinical_flags: List[ClinicalFlag] = []
        llm_flags_raw: List[str] = []
        
        diagnosed_others = assessment_request.diagnosed_conditions.others_input if assessment_request.diagnosed_conditions.others_input else None
        health_others = assessment_request.health_concerns.others.strip() if assessment_request.health_concerns.others and assessment_request.health_concerns.others.strip() else None
        
        if diagnosed_others or health_others:
            print(f"[STEP 8][{trace_id}] Processing 'others' inputs with LLM")
            if diagnosed_others:
                print(f"  - diagnosed_conditions.others: {diagnosed_others}")
            if health_others:
                print(f"  - health_concerns.others: {health_others}")
            
            user_context = self._build_user_context(assessment_request, cycle_context)
            
            # Single API call for both inputs
            llm_response_diagnosed, llm_response_health = self.llm_service.process_both_others_inputs(
                diagnosed_input=diagnosed_others,
                health_concerns_input=health_others,
                user_context=user_context,
                trace_id=trace_id
            )
            
            # Apply scores from diagnosed conditions response
            if llm_response_diagnosed:
                llm_confidence, llm_flags = self.llm_service.apply_llm_scores(
                    llm_response_diagnosed, 
                    hormone_scorer,
                    diagnosed_others,
                    source="diagnosed_conditions",
                    trace_id=trace_id
                )
                print(f"[LLM][{trace_id}] Diagnosed Conditions Confidence:", llm_confidence)
                print(f"[LLM][{trace_id}] Diagnosed Conditions Flags:", llm_flags)
                llm_flags_raw.extend(llm_flags)
            
            # Apply scores from health concerns response
            if llm_response_health:
                llm_confidence_hc, llm_flags_hc = self.llm_service.apply_llm_scores(
                    llm_response_health, 
                    hormone_scorer,
                    health_others,
                    source="health_concerns",
                    trace_id=trace_id
                )
                print(f"[LLM][{trace_id}] Health Concerns Confidence:", llm_confidence_hc)
                print(f"[LLM][{trace_id}] Health Concerns Flags:", llm_flags_hc)
                llm_flags_raw.extend(llm_flags_hc)
                
                # Use the more conservative (lower) confidence if both present
                # Confidence levels: high > medium > low
                if llm_confidence and llm_confidence_hc:
                    confidence_order = {"low": 0, "medium": 1, "high": 2}
                    llm_confidence = llm_confidence if confidence_order[llm_confidence] <= confidence_order[llm_confidence_hc] else llm_confidence_hc
                elif llm_confidence_hc:
                    llm_confidence = llm_confidence_hc
        
        # Step 9: Score lab results if provided
        labs_uploaded = assessment_request.lab_results is not None
        labs_concordance = "none"
        
        if labs_uploaded:
            print("[STEP 9] Scoring lab results...")
            hormone_scorer.score_lab_results(assessment_request.lab_results)
            print("[LABS] Post-scoring hormone 'from_labs' contributions:")
            for h, data in hormone_scorer.hormone_scores.items():
                if data.get("from_labs", 0) > 0:
                    print(f"  - {h}: from_labs={data['from_labs']}, direction={data['direction']}")
            labs_concordance = self._calculate_lab_concordance(
                hormone_scorer.hormone_scores,
                hormone_scorer.contributing_factors
            )
            print("[LABS] Concordance classification:", labs_concordance)
        
        # Step 10: Calculate final scores
        print("[STEP 10] Calculating final scores...")
        hormone_scorer.calculate_final_scores()
        
        # Step 11: Identify primary and secondary imbalances
        print("[STEP 11] Determining primary and secondary imbalances...")
        primary_hormone, secondary_hormones = hormone_scorer.get_primary_secondary_imbalances()
        print("[IMBALANCES] Primary:", primary_hormone, "Secondary:", secondary_hormones)
        
        # Step 12: Count symptoms by hormone cluster
        print("[STEP 12] Counting symptoms by hormone cluster...")
        symptoms_count = self._count_total_symptoms(assessment_request.health_concerns)
        symptom_clusters = self._count_symptoms_by_hormone(hormone_scorer.contributing_factors)
        # symptom_clusters already contains counts per hormone (ints), so print directly
        print("[SYMPTOMS] Total:", symptoms_count, "Clusters:", symptom_clusters)
        
        # Step 13: Calculate confidence
        print("[STEP 13] Calculating confidence score...")
        confidence = confidence_calculator.calculate_confidence(
            period_pattern=assessment_request.period_pattern.period_pattern,
            last_period_date=assessment_request.cycle_details.last_period_date,
            cycle_length=assessment_request.cycle_details.cycle_length,
            date_not_sure=assessment_request.cycle_details.date_not_sure,
            diagnosed_conditions=assessment_request.diagnosed_conditions.conditions,
            top_concern_selected=True,
            birth_control=assessment_request.period_pattern.birth_control,
            symptoms_count=symptoms_count,
            symptom_clusters=symptom_clusters,
            labs_uploaded=labs_uploaded,
            labs_concordance=labs_concordance,
            conflicts_detected=0,  # Will update after conflict detection
            llm_confidence=llm_confidence
        )
        print("[CONFIDENCE] Level:", confidence.level, "Score:", confidence.score)
        for factor in confidence.calculation_breakdown:
            print(f"  [CONFIDENCE FACTOR] {factor.factor}: {factor.points}")
        
        # Step 14: Detect conflicts
        print("[STEP 14] Detecting conflicts...")
        conflicts = conflict_detector.detect_all_conflicts(
            hormone_scores=hormone_scorer.hormone_scores,
            diagnosed_conditions=assessment_request.diagnosed_conditions.conditions,
            symptoms_by_hormone=symptom_clusters,
            labs_uploaded=labs_uploaded,
            labs_concordance=labs_concordance,
            birth_control=assessment_request.period_pattern.birth_control
        )
        if conflicts:
            print("[CONFLICTS] Detected:")
            for c in conflicts:
                print("  -", c.description, "impact:", c.impact_on_confidence)
        else:
            print("[CONFLICTS] None detected")
        
        # Update confidence with conflict count
        if conflicts:
            confidence.score += sum(c.impact_on_confidence for c in conflicts)
            confidence.calculation_breakdown.append(
                ConfidenceFactor(
                    factor=f"{len(conflicts)} conflict(s) detected",
                    points=sum(c.impact_on_confidence for c in conflicts)
                )
            )
        
        # Step 15: Generate explanations and recommendations
        print("[STEP 15] Building explanations for primary hormone:", primary_hormone)
        primary_imbalance = self._build_hormone_imbalance(
            primary_hormone,
            hormone_scorer,
            labs_uploaded
        )
        
        secondary_imbalances = [
            self._build_hormone_imbalance(h, hormone_scorer, labs_uploaded)
            for h in secondary_hormones
        ]
        if secondary_imbalances:
            print("[STEP 15] Secondary imbalances built:", [s.hormone for s in secondary_imbalances])
        
        # Step 16: Generate clinical flags
        print("[STEP 16] Generating clinical flags...")
        generated_flags = self._generate_clinical_flags(
            hormone_scorer.hormone_scores,
            assessment_request,
            labs_uploaded,
            conflicts
        )
        # Normalize any plain string flags from LLM fallback into ClinicalFlag objects
        for f in llm_flags_raw:
            # llm fallback returns strings; convert to ClinicalFlag
            if isinstance(f, str):
                clinical_flags.append(
                    ClinicalFlag(
                        flag_type="general_recommendation",
                        urgency="low",
                        message=f
                    )
                )
        clinical_flags.extend(generated_flags)
        print("[FLAGS] Total clinical flags:", len(clinical_flags))
        
        # Step 17: Generate next steps
        print("[STEP 17] Generating next steps...")
        next_steps = self._generate_next_steps(
            primary_hormone,
            secondary_hormones,
            labs_uploaded,
            confidence.level
        )
        
        # Step 18: Build all hormone scores
        print("[STEP 18] Compiling all hormone scores...")
        all_hormone_scores = {}
        for hormone, data in hormone_scorer.hormone_scores.items():
            all_hormone_scores[hormone] = HormoneScore(
                total=data["total"],
                direction=data["direction"],
                breakdown=hormone_scorer.get_hormone_breakdown(hormone)
            )
            print(f"  [HORMONE SUMMARY] {hormone}: total={data['total']} direction={data['direction']} breakdown={hormone_scorer.get_hormone_breakdown(hormone)}")
        
        # Step 19: Build user profile
        print("[STEP 19] Building user profile...")
        user_profile = UserProfile(
            age=assessment_request.basic_info.age,
            last_period_date=assessment_request.cycle_details.last_period_date,
            cycle_length=assessment_request.cycle_details.cycle_length,
            birth_control=assessment_request.period_pattern.birth_control,
            diagnosed_conditions=assessment_request.diagnosed_conditions.conditions
        )
        
        # Step 20: Build complete response
        print("[STEP 20] Finalizing assessment response...")
        response = AssessmentResponse(
            assessment_metadata=AssessmentMetadata(
                user_id=str(uuid.uuid4()),
                assessment_date=date.today(),
                version="1.0",
                disclaimer="This assessment is for educational purposes only and does not constitute medical diagnosis. Please consult a qualified healthcare provider for proper diagnosis and treatment."
            ),
            user_profile=user_profile,
            cycle_context=cycle_context,
            primary_imbalance=primary_imbalance,
            secondary_imbalances=secondary_imbalances,
            all_hormone_scores=all_hormone_scores,
            confidence=confidence,
            conflicts=conflicts,
            clinical_flags=clinical_flags,
            next_steps=next_steps
        )
        print(f"[FINAL][TRACE {trace_id}] Primary Hormone:", response.primary_imbalance.hormone, "direction:", response.primary_imbalance.direction, "score:", response.primary_imbalance.total_score)
        print("[FINAL] Confidence Level:", response.confidence.level, "Score:", response.confidence.score)
        print("[FINAL] Next Steps (immediate):", response.next_steps.immediate)
        print(f"========== AUVRA ASSESSMENT END [TRACE {trace_id}] =========\n")
        return response
    
    def _build_user_context(self, request: CompleteAssessmentRequest, cycle_context: CycleContext) -> dict:
        """Build user context for LLM"""
        all_symptoms = (
            request.health_concerns.period_concerns +
            request.health_concerns.body_concerns +
            request.health_concerns.skin_hair_concerns +
            request.health_concerns.mental_health_concerns
        )
        
        return {
            "age": request.basic_info.age,
            "symptoms": all_symptoms,
            "diagnoses": request.diagnosed_conditions.conditions,
            "cycle_pattern": request.period_pattern.period_pattern,
            "cycle_phase": cycle_context.current_phase or "unknown"
        }
    
    def _calculate_lab_concordance(self, hormone_scores: Dict, contributing_factors: Dict) -> str:
        """Calculate concordance between labs and symptoms"""
        concordance_count = 0
        total_hormones_with_labs = 0
        
        for hormone, data in hormone_scores.items():
            if data["from_labs"] > 0:
                total_hormones_with_labs += 1
                if data["from_symptoms"] > 0 or data["from_diagnosis"] > 0:
                    concordance_count += 1
        
        if total_hormones_with_labs == 0:
            return "none"
        
        concordance_ratio = concordance_count / total_hormones_with_labs
        
        if concordance_ratio >= 0.75:
            return "high"
        elif concordance_ratio >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _count_total_symptoms(self, health_concerns: HealthConcernsRequest) -> int:
        """Count total symptoms reported"""
        return (
            len(health_concerns.period_concerns) +
            len(health_concerns.body_concerns) +
            len(health_concerns.skin_hair_concerns) +
            len(health_concerns.mental_health_concerns)
        )
    
    def _count_symptoms_by_hormone(self, contributing_factors: Dict[str, List[str]]) -> Dict[str, int]:
        """Count symptoms contributing to each hormone"""
        return {
            hormone: len(factors)
            for hormone, factors in contributing_factors.items()
            if len(factors) > 0
        }
    
    def _build_hormone_imbalance(
        self, 
        hormone: str, 
        scorer: HormoneScorer, 
        has_labs: bool
    ) -> HormoneImbalance:
        """Build hormone imbalance object with explanation"""
        
        data = scorer.hormone_scores[hormone]
        direction = data["direction"]
        
        explanation = self.explanation_generator.generate_explanation(
            hormone,
            direction,
            scorer.contributing_factors[hormone],
            has_labs
        )
        
        recommendations = self.explanation_generator.get_recommendations(
            hormone,
            direction,
            has_labs
        )
        
        return HormoneImbalance(
            hormone=hormone,
            direction=direction,
            total_score=data["total"],
            breakdown=scorer.get_hormone_breakdown(hormone),
            contributing_factors=scorer.contributing_factors[hormone],
            explanation=explanation,
            recommendations=recommendations
        )
    
    def _generate_clinical_flags(
        self,
        hormone_scores: Dict,
        request: CompleteAssessmentRequest,
        labs_uploaded: bool,
        conflicts: List[Conflict]
    ) -> List[ClinicalFlag]:
        """Generate clinical flags and recommendations"""
        
        flags = []
        
        # Hot flashes in young women - HIGH URGENCY
        if "hot_flashes" in request.health_concerns.body_concerns and request.basic_info.age < 40:
            flags.append(ClinicalFlag(
                flag_type="urgent_medical",
                urgency="high",
                message="Hot flashes in women under 40 may indicate premature ovarian insufficiency (POI). Please schedule appointment with gynecologist or endocrinologist urgently."
            ))
        
        # Amenorrhea - HIGH URGENCY
        if request.period_pattern.period_pattern == "no_periods":
            flags.append(ClinicalFlag(
                flag_type="urgent_medical",
                urgency="high",
                message="Absence of periods (amenorrhea) requires medical evaluation to rule out serious conditions. Please consult healthcare provider."
            ))
        
        # Recommend comprehensive testing
        if not labs_uploaded:
            hormones_to_test = []
            for hormone, data in hormone_scores.items():
                if data["total"] >= 5:
                    hormones_to_test.append(hormone)
            
            if hormones_to_test:
                test_recommendations = {
                    "androgens": "Free testosterone, Total testosterone, DHEA-S, LH:FSH ratio",
                    "thyroid": "TSH, Free T3, Free T4, TPO antibodies",
                    "insulin": "Fasting insulin, HbA1c, Fasting glucose",
                    "estrogen": "Estradiol (Day 3-5 of cycle)",
                    "progesterone": "Progesterone (Day 19-22 of cycle)",
                    "cortisol": "AM cortisol, Consider 4-point salivary cortisol"
                }
                
                tests = [test_recommendations.get(h, h) for h in hormones_to_test]
                
                flags.append(ClinicalFlag(
                    flag_type="testing_recommended",
                    urgency="moderate",
                    message=f"Consider comprehensive hormone panel: {', '.join(tests)}"
                ))
        
        # Cycle tracking recommendation
        if request.cycle_details.date_not_sure:
            flags.append(ClinicalFlag(
                flag_type="cycle_tracking",
                urgency="low",
                message="Track basal body temperature and menstrual cycle dates for 2-3 months to improve assessment accuracy and confirm ovulation."
            ))
        
        return flags
    
    def _generate_next_steps(
        self,
        primary_hormone: str,
        secondary_hormones: List[str],
        labs_uploaded: bool,
        confidence_level: str
    ) -> NextSteps:
        """Generate personalized next steps"""
        
        immediate = [
            "Schedule appointment with gynecologist or endocrinologist to discuss findings",
            "Begin tracking symptoms daily to identify patterns",
        ]
        
        if not labs_uploaded:
            immediate.append(f"Consider hormone testing: Focus on {primary_hormone} panel first")
        
        short_term = [
            "Implement lifestyle changes specific to your hormone imbalances",
            "Begin stress management practices (meditation, yoga, adequate sleep 7-9 hours)",
            "Review and optimize nutrition based on recommendations",
        ]
        
        if primary_hormone == "insulin":
            short_term.append("Start low-glycemic diet to support insulin sensitivity")
        elif primary_hormone == "thyroid":
            short_term.append("Ensure adequate iodine and selenium intake")
        elif primary_hormone == "androgens":
            short_term.append("Consider inositol supplementation for PCOS support")
        
        long_term = [
            "Regular follow-up hormone testing every 3-6 months to track progress",
            "Work with healthcare provider on personalized treatment plan",
            "Monitor symptom improvement and adjust interventions accordingly",
            "Consider working with functional medicine practitioner or hormone specialist"
        ]
        
        return NextSteps(
            immediate=immediate,
            short_term=short_term,
            long_term=long_term
        )
