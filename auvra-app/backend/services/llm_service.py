"""
LLM Integration Service for processing user-entered "Others" conditions
Uses Gemini API with structured prompts and validation
"""

import os
import json
from typing import Optional
from textwrap import shorten
import google.generativeai as genai
from models.schemas import LLMScoringResponse, HormoneImpact
from pydantic import ValidationError


class LLMService:
    """Service for LLM-based hormone scoring of custom inputs"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini API with configurable model and verbose debug logging"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        # Allow overriding model name via env; default to Gemini 2.5 Flash (latest stable)
        self.model_name = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            try:
                self.model = genai.GenerativeModel(self.model_name)
                print(f"[LLM][INIT] Gemini configured. model={self.model_name} (api key present: yes)")
            except Exception as e:
                print(f"[LLM][INIT][ERROR] Failed to initialize Gemini model '{self.model_name}': {e}")
                self.model = None
        else:
            self.model = None
            print("WARNING: GEMINI_API_KEY not set - LLM features will use fallback")
    
    def build_system_prompt(self, user_context: dict) -> str:
        """Build comprehensive system prompt with user context"""
        
        prompt = f"""ROLE: Clinical Hormone Scoring Assistant for Women's Health

CONTEXT:
You are analyzing a custom health concern entered by a woman aged {user_context.get('age', 'unknown')} 
in a hormone assessment application. Your task is to map this input to 
our hormone scoring system following established clinical heuristics.

USER PROFILE:
- Age: {user_context.get('age', 'unknown')}
- Symptoms already reported: {', '.join(user_context.get('symptoms', []))}
- Diagnosed conditions: {', '.join(user_context.get('diagnoses', []))}
- Cycle pattern: {user_context.get('cycle_pattern', 'unknown')}
- Current phase: {user_context.get('cycle_phase', 'unknown')}

HORMONES WE TRACK:
1. Estrogen (can be HIGH or LOW)
   - High: Heavy periods, bloating, breast tenderness
   - Low: Light periods, hot flashes, vaginal dryness

2. Progesterone (typically LOW)
   - Mood swings, anxiety, PMS, short luteal phase

3. Androgens (typically HIGH)
   - Hirsutism, acne, male-pattern hair loss, PCOS

4. Insulin (typically HIGH)
   - Weight gain (especially abdominal), sugar cravings, difficulty losing weight

5. Cortisol (can be HIGH or LOW)
   - High: Chronic stress, anxiety, sleep issues, salt/sugar cravings
   - Low: Extreme fatigue, low blood pressure, salt cravings

6. Thyroid (typically LOW - hypothyroidism)
   - Fatigue, weight gain, cold intolerance, hair thinning, constipation

SCORING RULES YOU MUST FOLLOW:

1. PCOS-Related Symptoms:
   Irregular periods, hirsutism, acne → Androgens +2 to +3, Insulin +2

2. Thyroid-Related Symptoms:
   Fatigue, weight gain, hair loss, cold sensitivity → Thyroid +2 to +3

3. Estrogen Dominance Symptoms:
   Heavy periods, bloating, breast tenderness → Estrogen HIGH +2, Progesterone LOW +1

4. Low Estrogen Symptoms:
   Light periods, hot flashes (under 40), vaginal dryness → Estrogen LOW +2 to +3

5. Progesterone Deficiency:
   Mood swings, anxiety, short cycles, PMS → Progesterone LOW +2

6. Insulin Resistance:
   Weight gain (especially abdominal), sugar cravings, difficulty losing weight → Insulin +2

7. High Cortisol:
   Chronic stress, anxiety, sleep issues, sugar/salt cravings → Cortisol HIGH +2

8. Low Cortisol:
   Extreme fatigue, low blood pressure, salt cravings → Cortisol LOW +2

9. Androgen Excess:
   Facial hair, acne, male-pattern hair loss → Androgens +2 to +3

CRITICAL REQUIREMENTS:
- Be conservative if input is vague or ambiguous
- Consider existing reported symptoms to avoid double-counting
- Flag if condition requires immediate medical attention
- Return ONLY valid JSON - no markdown, no explanations outside JSON
- Use only these hormone names: estrogen, progesterone, androgens, insulin, cortisol, thyroid
- Use only these directions: high, low
- Score weights must be integers: 0, 1, 2, or 3

REQUIRED JSON OUTPUT FORMAT:
{{
  "hormone_impacts": [
    {{
      "hormone": "hormone_name",
      "direction": "high or low",
      "score_weight": 0-3,
      "reasoning": "Brief clinical rationale (minimum 10 characters)"
    }}
  ],
  "overall_confidence": "high|medium|low",
  "clinical_flags": ["array of any concerns or recommendations"],
  "needs_medical_review": true|false
}}

If the input is unrelated to hormones or unclear, return empty hormone_impacts array and set overall_confidence to "low".
"""
        return prompt
    
    def _merge_duplicate_hormones(self, hormone_impacts: list) -> list:
        """
        Merge duplicate hormone entries by taking the highest score_weight
        and combining reasoning statements.
        
        Gemini sometimes returns the same hormone twice with different reasoning.
        Instead of rejecting, we merge them intelligently.
        """
        if not hormone_impacts:
            return hormone_impacts
        
        merged = {}
        for impact in hormone_impacts:
            hormone = impact['hormone']
            direction = impact['direction']
            key = f"{hormone}_{direction}"
            
            if key not in merged:
                merged[key] = impact
            else:
                # Merge: take max score, combine reasoning
                existing = merged[key]
                if impact['score_weight'] > existing['score_weight']:
                    existing['score_weight'] = impact['score_weight']
                
                # Combine reasoning if different, but respect 500 char limit
                if impact['reasoning'] not in existing['reasoning']:
                    combined = f"{existing['reasoning']}; {impact['reasoning']}"
                    # Pydantic validates max_length=500, ensure we don't exceed
                    if len(combined) <= 500:
                        existing['reasoning'] = combined
                    else:
                        # Keep the longer/more detailed reasoning
                        if len(impact['reasoning']) > len(existing['reasoning']):
                            existing['reasoning'] = impact['reasoning'][:500]
                        # else: keep existing reasoning
        
        return list(merged.values())
    
    def process_both_others_inputs(
        self, 
        diagnosed_input: Optional[str], 
        health_concerns_input: Optional[str],
        user_context: dict, 
        trace_id: Optional[str] = None
    ) -> tuple[Optional[LLMScoringResponse], Optional[LLMScoringResponse]]:
        """
        Process BOTH 'others' inputs in a SINGLE Gemini API call for efficiency.
        Returns (diagnosed_response, health_concerns_response)
        """
        
        tag = f"[LLM][{trace_id}]" if trace_id else "[LLM]"
        
        # If both are empty, return None for both
        if not diagnosed_input and not health_concerns_input:
            return None, None
        
        # If only one is provided, fall back to single call
        if not diagnosed_input:
            return None, self.process_others_input(health_concerns_input, user_context, trace_id)
        if not health_concerns_input:
            return self.process_others_input(diagnosed_input, user_context, trace_id), None
        
        # Both inputs provided - process together
        if not self.model:
            print(f"{tag} Gemini model not configured. Using fallback keyword scoring.")
            return self._fallback_scoring(diagnosed_input), self._fallback_scoring(health_concerns_input)
        
        try:
            from datetime import datetime
            
            # Build combined prompt
            system_prompt = self.build_system_prompt(user_context)
            full_prompt = f"""{system_prompt}

USER HAS PROVIDED TWO SEPARATE INPUTS TO ANALYZE:

INPUT 1 (from diagnosed conditions):
"{diagnosed_input}"

INPUT 2 (from health concerns):
"{health_concerns_input}"

IMPORTANT: Return a JSON object with TWO separate analyses in this exact format:
{{
  "input1_analysis": {{
    "hormone_impacts": [...],
    "overall_confidence": "high|medium|low",
    "clinical_flags": [...],
    "needs_medical_review": true|false
  }},
  "input2_analysis": {{
    "hormone_impacts": [...],
    "overall_confidence": "high|medium|low",
    "clinical_flags": [...],
    "needs_medical_review": true|false
  }}
}}

Analyze each input independently and avoid double-counting symptoms between them."""
            
            # Call Gemini API
            print("\n" + "#" * 100)
            print("# GEMINI API CALL - START (COMBINED ANALYSIS)")
            print("# TRACE ID: " + (trace_id or 'N/A'))
            print("# MODEL: " + self.model_name)
            print("# PURPOSE: Analyze BOTH 'Others' inputs in single call")
            print("# TIMESTAMP: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            print("#" * 100)
            
            print("\n# INPUT 1 (diagnosed conditions):")
            print(f'"{diagnosed_input}"')
            print("\n# INPUT 2 (health concerns):")
            print(f'"{health_concerns_input}"')
            print()
            
            print("# PROMPT SENT TO GEMINI:")
            print("#" * 100)
            print(full_prompt)
            print()
            print(f"# PROMPT LENGTH: {len(full_prompt)} characters")
            print("#" * 100)

            print("\n# Calling Gemini API... please wait...")
            response = self.model.generate_content(full_prompt)
            response_text = response.text or ""
            print("# Gemini API responded successfully!\n")
            
            print("# RAW RESPONSE FROM GEMINI:")
            print("#" * 100)
            print(response_text)
            print()
            print(f"# RESPONSE LENGTH: {len(response_text)} characters")
            print("#" * 100)
            print()
            
            # Clean response
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse combined JSON
            response_data = json.loads(response_text)
            
            print("# PARSED JSON FROM GEMINI:")
            print("#" * 100)
            parsed_pretty = json.dumps(response_data, indent=2)
            print(parsed_pretty)
            print()
            print(f"# JSON LENGTH: {len(parsed_pretty)} characters")
            print("#" * 100)
            print()
            
            # Extract both analyses (with safe defaults)
            input1_data = response_data.get("input1_analysis")
            input2_data = response_data.get("input2_analysis")
            
            # Validate structure
            if not input1_data and not input2_data:
                raise ValueError("Gemini response missing both input1_analysis and input2_analysis keys")
            
            # Merge duplicate hormones before validation (Gemini sometimes lists same hormone twice)
            if input1_data and 'hormone_impacts' in input1_data:
                input1_data['hormone_impacts'] = self._merge_duplicate_hormones(input1_data['hormone_impacts'])
            if input2_data and 'hormone_impacts' in input2_data:
                input2_data['hormone_impacts'] = self._merge_duplicate_hormones(input2_data['hormone_impacts'])
            
            # Validate with Pydantic (with proper error handling)
            input1_response = None
            input2_response = None
            
            if input1_data:
                try:
                    input1_response = LLMScoringResponse(**input1_data)
                except ValidationError as e:
                    print(f"{tag}[WARNING] input1_analysis validation failed: {e}")
                    print(f"{tag}[WARNING] Falling back for input 1")
                    input1_response = self._fallback_scoring(diagnosed_input) if diagnosed_input else None
                    
            if input2_data:
                try:
                    input2_response = LLMScoringResponse(**input2_data)
                except ValidationError as e:
                    print(f"{tag}[WARNING] input2_analysis validation failed: {e}")
                    print(f"{tag}[WARNING] Falling back for input 2")
                    input2_response = self._fallback_scoring(health_concerns_input) if health_concerns_input else None
            
            # Print summary
            print("# GEMINI ANALYSIS SUMMARY:")
            print("#" * 100)
            
            if input1_response:
                print(f"# INPUT 1 (diagnosed conditions): {diagnosed_input}")
                print(f"#   Confidence: {input1_response.overall_confidence.upper()}")
                if input1_response.hormone_impacts:
                    print(f"#   Impacts ({len(input1_response.hormone_impacts)}):")
                    for idx, hi in enumerate(input1_response.hormone_impacts, 1):
                        print(f"#     {idx}. {hi.hormone.upper()} → {hi.direction.upper()} (+{hi.score_weight})")
                else:
                    print("#   No hormone impacts detected")
            
            print()
            
            if input2_response:
                print(f"# INPUT 2 (health concerns): {health_concerns_input}")
                print(f"#   Confidence: {input2_response.overall_confidence.upper()}")
                if input2_response.hormone_impacts:
                    print(f"#   Impacts ({len(input2_response.hormone_impacts)}):")
                    for idx, hi in enumerate(input2_response.hormone_impacts, 1):
                        print(f"#     {idx}. {hi.hormone.upper()} → {hi.direction.upper()} (+{hi.score_weight})")
                else:
                    print("#   No hormone impacts detected")
            
            print("#" * 100)
            print("# GEMINI API CALL - END")
            print("#" * 100 + "\n")
            
            return input1_response, input2_response
            
        except ValidationError as e:
            print(f"{tag}[ERROR] Validation error: {e}")
            return self._fallback_scoring(diagnosed_input), self._fallback_scoring(health_concerns_input)
        
        except json.JSONDecodeError as e:
            print(f"{tag}[ERROR] JSON decode error: {e}")
            return self._fallback_scoring(diagnosed_input), self._fallback_scoring(health_concerns_input)
        
        except Exception as e:
            print(f"{tag}[ERROR] Exception calling Gemini API: {e}")
            return self._fallback_scoring(diagnosed_input), self._fallback_scoring(health_concerns_input)
    
    def process_others_input(self, user_input: str, user_context: dict, trace_id: Optional[str] = None) -> LLMScoringResponse:
        """Process user's 'Others' input using Gemini API"""
        
        tag = f"[LLM][{trace_id}]" if trace_id else "[LLM]"
        if not self.model:
            print(f"{tag} Gemini model not configured. Using fallback keyword scoring.")
            print(f"{tag}[INPUT] Others input:", user_input)
            return self._fallback_scoring(user_input)
        
        try:
            # Build prompt
            system_prompt = self.build_system_prompt(user_context)
            full_prompt = f"""{system_prompt}

USER INPUT TO ANALYZE:
"{user_input}"

Return your analysis as JSON following the required format above."""
            
            # Call Gemini API
            from datetime import datetime
            
            print("\n" + "#" * 100)
            print("# GEMINI API CALL - START")
            print("# TRACE ID: " + (trace_id or 'N/A'))
            print("# MODEL: " + self.model_name)
            print("# PURPOSE: Analyze 'Others' input for hormone scoring")
            print("# TIMESTAMP: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            print("#" * 100)
            
            print("\n# INPUT TO GEMINI (User's 'Others' field):")
            print(f'"{user_input}"')
            print()
            
            print("\n# INPUT TO GEMINI (User's 'Others' field):")
            print(f'"{user_input}"')
            print()
            
            # Show FULL prompt for supervisor demo (always enabled)
            print("# PROMPT SENT TO GEMINI (FULL CLINICAL CONTEXT):")
            print("#" * 100)
            print(full_prompt)
            print()
            print(f"# PROMPT LENGTH: {len(full_prompt)} characters")
            print("#" * 100)

            print("\n# Calling Gemini API... please wait...")
            response = self.model.generate_content(full_prompt)
            response_text = response.text or ""
            print("# Gemini API responded successfully!\n")
            
            print("# RAW RESPONSE FROM GEMINI (COMPLETE):")
            print("#" * 100)
            print(response_text)
            print()
            print(f"# RESPONSE LENGTH: {len(response_text)} characters")
            print("#" * 100)
            print()
            
            # Clean response (remove markdown if present)
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse JSON
            response_data = json.loads(response_text)
            
            print("# PARSED JSON FROM GEMINI (COMPLETE):")
            print("#" * 100)
            parsed_pretty = json.dumps(response_data, indent=2)
            print(parsed_pretty)
            print()
            print(f"# JSON LENGTH: {len(parsed_pretty)} characters")
            print("#" * 100)
            print()
            
            # Merge duplicate hormones before validation (Gemini sometimes lists same hormone twice)
            if 'hormone_impacts' in response_data:
                response_data['hormone_impacts'] = self._merge_duplicate_hormones(response_data['hormone_impacts'])
            
            # Validate with Pydantic
            llm_response = LLMScoringResponse(**response_data)
            
            print("# GEMINI ANALYSIS SUMMARY:")
            print("#" * 100)
            print(f"# Overall Confidence: {llm_response.overall_confidence.upper()}")
            if llm_response.hormone_impacts:
                print(f"# Hormone Impacts ({len(llm_response.hormone_impacts)} detected):")
                for idx, hi in enumerate(llm_response.hormone_impacts, 1):
                    print(f"#   {idx}. {hi.hormone.upper()} → {hi.direction.upper()} (+{hi.score_weight} points)")
                    print(f"#      Reason: {hi.reasoning}")
            else:
                print("# No hormone impacts detected")
            
            if llm_response.clinical_flags:
                print(f"# Clinical Flags ({len(llm_response.clinical_flags)}):")
                for idx, f in enumerate(llm_response.clinical_flags, 1):
                    print(f"#   {idx}. {f}")
            
            print(f"# Requires Medical Review: {'YES' if llm_response.needs_medical_review else 'NO'}")
            print("#" * 100)
            print("# GEMINI API CALL - END")
            print("#" * 100 + "\n")
            
            return llm_response
            
        except ValidationError as e:
            print(f"Validation error in LLM response: {e}")
            return self._fallback_scoring(user_input)
        
        except json.JSONDecodeError as e:
            print(f"{tag}[ERROR] JSON decode error: {e}")
            print(f"{tag} Raw response (truncated): {response_text[:200]}")
            return self._fallback_scoring(user_input)
        
        except Exception as e:
            print(f"{tag}[ERROR] Exception calling Gemini API: {e}")
            return self._fallback_scoring(user_input)
    
    def _fallback_scoring(self, user_input: str) -> LLMScoringResponse:
        """Fallback keyword-based scoring if LLM fails"""
        
        # Handle None or empty input
        if not user_input or not user_input.strip():
            return LLMScoringResponse(
                hormone_impacts=[],
                overall_confidence="low",
                clinical_flags=[
                    "No custom input provided",
                    "Please consult healthcare provider for accurate diagnosis"
                ],
                needs_medical_review=True
            )
        
        input_lower = user_input.lower()
        impacts = []
        flags = []
        
        # Keyword matching
        if any(word in input_lower for word in ["hair loss", "thinning hair", "losing hair"]):
            impacts.append(HormoneImpact(
                hormone="thyroid",
                direction="low",
                score_weight=2,
                reasoning="Hair loss commonly associated with hypothyroidism"
            ))
            impacts.append(HormoneImpact(
                hormone="androgens",
                direction="high",
                score_weight=1,
                reasoning="Hair loss can also indicate androgen excess"
            ))
        
        if any(word in input_lower for word in ["weight gain", "gaining weight", "can't lose weight"]):
            impacts.append(HormoneImpact(
                hormone="thyroid",
                direction="low",
                score_weight=2,
                reasoning="Weight gain is primary symptom of hypothyroidism"
            ))
            impacts.append(HormoneImpact(
                hormone="insulin",
                direction="high",
                score_weight=1,
                reasoning="Weight gain can indicate insulin resistance"
            ))
        
        if any(word in input_lower for word in ["acne", "pimples", "breakouts"]):
            impacts.append(HormoneImpact(
                hormone="androgens",
                direction="high",
                score_weight=2,
                reasoning="Acne is commonly caused by androgen excess"
            ))
        
        if any(word in input_lower for word in ["fatigue", "tired", "exhausted", "no energy"]):
            impacts.append(HormoneImpact(
                hormone="thyroid",
                direction="low",
                score_weight=2,
                reasoning="Fatigue is hallmark symptom of hypothyroidism"
            ))
            impacts.append(HormoneImpact(
                hormone="cortisol",
                direction="high",
                score_weight=1,
                reasoning="Chronic fatigue can indicate HPA axis dysfunction"
            ))
        
        if any(word in input_lower for word in ["stress", "anxious", "anxiety", "worried"]):
            impacts.append(HormoneImpact(
                hormone="cortisol",
                direction="high",
                score_weight=2,
                reasoning="Stress and anxiety indicate elevated cortisol"
            ))
        
        if any(word in input_lower for word in ["mood", "emotional", "depression", "irritable"]):
            impacts.append(HormoneImpact(
                hormone="progesterone",
                direction="low",
                score_weight=2,
                reasoning="Mood issues commonly related to progesterone deficiency"
            ))
        
        if any(word in input_lower for word in ["facial hair", "unwanted hair", "chin hair"]):
            impacts.append(HormoneImpact(
                hormone="androgens",
                direction="high",
                score_weight=3,
                reasoning="Hirsutism is direct marker of androgen excess"
            ))
        
        # Determine confidence
        if len(impacts) == 0:
            confidence = "low"
            flags.append("Unable to identify hormone-related concerns from input")
        elif len(impacts) >= 2:
            confidence = "medium"
        else:
            confidence = "low"
        
        flags.append("Analysis used keyword matching (LLM unavailable)")
        flags.append("Please consult healthcare provider for accurate diagnosis")
        
        # Note: clinical_flags here are strings; they will be normalized to ClinicalFlag
        # objects in AssessmentService before returning the final response model.
        result = LLMScoringResponse(
            hormone_impacts=impacts,
            overall_confidence=confidence,
            clinical_flags=flags,
            needs_medical_review=True
        )
        # Log fallback JSON for transparency
        try:
            payload = result.model_dump() if hasattr(result, "model_dump") else result.dict()
            pretty = json.dumps(payload, indent=2)
            if len(pretty) > 2000:
                pretty = pretty[:2000] + "..."
            print("[LLM][FALLBACK] Returning JSON output:\n" + pretty)
        except Exception:
            pass
        return result
    
    def apply_llm_scores(self, llm_response: LLMScoringResponse, hormone_scorer, user_input: str, source: str = "others", trace_id: Optional[str] = None):
        """Apply LLM-derived scores to hormone scorer"""
        tag = f"[LLM][{trace_id}]" if trace_id else "[LLM]"
        print(f"{tag} Applying LLM-derived scores to hormone model...")
        for impact in llm_response.hormone_impacts:
            hormone = impact.hormone
            
            # Add to appropriate source (typically from_diagnosis for "others" input)
            if source == "others":
                hormone_scorer.hormone_scores[hormone]["from_diagnosis"] += impact.score_weight
            else:
                hormone_scorer.hormone_scores[hormone]["from_symptoms"] += impact.score_weight
            
            # Track direction for bi-directional hormones
            if hormone in ["estrogen", "cortisol"]:
                if impact.direction == "high":
                    hormone_scorer.hormone_scores[hormone]["high_score"] += impact.score_weight
                else:
                    hormone_scorer.hormone_scores[hormone]["low_score"] += impact.score_weight
            
            # Add to contributing factors
            factor_text = f"Custom input: {user_input[:50]}... ({impact.reasoning})"
            hormone_scorer.contributing_factors[hormone].append(factor_text)
            print(f"  {tag} [APPLY→{hormone}] direction={impact.direction} +{impact.score_weight} reason={impact.reasoning}")
        
        return llm_response.overall_confidence, llm_response.clinical_flags
