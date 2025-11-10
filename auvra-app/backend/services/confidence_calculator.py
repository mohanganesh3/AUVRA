"""
Confidence Score Calculator
Calculates assessment confidence based on data quality and completeness
"""

from typing import List, Dict
from models.schemas import Confidence, ConfidenceFactor


class ConfidenceCalculator:
    """Calculate confidence score for hormone assessment"""
    
    def __init__(self):
        self.factors = []
        self.score = 0
    
    def calculate_confidence(
        self,
        period_pattern: str,
        last_period_date,
        cycle_length: str,
        date_not_sure: bool,
        diagnosed_conditions: List[str],
        top_concern_selected: bool,
        birth_control: str,
        symptoms_count: int,
        symptom_clusters: Dict[str, int],
        labs_uploaded: bool,
        labs_concordance: str,
        conflicts_detected: int,
        llm_confidence: str = None
    ) -> Confidence:
        """Calculate overall confidence score"""
        
        self.factors = []
        self.score = 0
        
        # POSITIVE FACTORS
        
        # Regular cycles
        if period_pattern == "regular":
            self._add_factor("Regular cycles reported", 2)
        elif period_pattern == "not_sure":
            self._add_factor("Period pattern uncertain", -1)
        
        # Last period date provided
        if last_period_date and not date_not_sure:
            self._add_factor("Exact last period date provided", 1)
        
        # Diagnosed condition selected
        if diagnosed_conditions:
            self._add_factor(f"Diagnosed condition(s) selected: {', '.join(diagnosed_conditions)}", 1)
        
        # Top concern selected
        if top_concern_selected:
            self._add_factor("Top concern identified", 1)
        
        # Multiple symptoms in same cluster
        for hormone, count in symptom_clusters.items():
            if count >= 3:
                self._add_factor(f"3+ {hormone}-related symptoms", 1)
                break  # Only count once
        
        # Lab results uploaded
        if labs_uploaded:
            self._add_factor("Lab results provided", 2)
        
        # Labs align with symptoms
        if labs_concordance == "high":
            self._add_factor("Lab results confirm reported symptoms", 2)
        
        # Natural cycle (no birth control)
        if birth_control == "none":
            self._add_factor("No hormonal birth control (natural cycle observable)", 1)
        
        # NEGATIVE FACTORS
        
        # Irregular cycles
        if period_pattern == "irregular":
            self._add_factor("Irregular cycles (harder to phase-map)", -1)
        
        # Date not sure
        if date_not_sure:
            self._add_factor("'I'm not sure' selected for cycle date", -2)
        
        # On hormonal birth control
        if birth_control in ["hormonal_pills", "hormonal_iud"]:
            self._add_factor("On hormonal birth control (masks natural patterns)", -1)
        
        # Conflicts detected
        if conflicts_detected > 0:
            self._add_factor(f"Conflicting symptoms detected ({conflicts_detected} conflicts)", -2)
        
        # Only diagnosis, no symptoms
        if diagnosed_conditions and symptoms_count == 0:
            self._add_factor("Diagnosis without supporting symptoms", -1)
        
        # LLM low confidence
        if llm_confidence == "low":
            self._add_factor("Custom input processed with low confidence", -2)
        elif llm_confidence == "medium":
            self._add_factor("Custom input processed with medium confidence", -1)
        
        # No labs despite high severity
        if not labs_uploaded and symptoms_count > 5:
            self._add_factor("No lab results despite significant symptoms", -1)
        
        # Labs contradict symptoms
        if labs_concordance == "low":
            self._add_factor("Lab results contradict reported symptoms", -2)
        
        # Determine confidence level
        if self.score >= 6:
            level = "high"
            recommendation = "Your assessment is highly reliable based on comprehensive data, clear patterns, and objective lab confirmation. This provides a strong foundation for understanding your hormone health."
        elif self.score >= 3:
            level = "medium"
            recommendation = "Your assessment is moderately reliable based on symptoms and available data. Consider uploading lab results (testosterone, insulin, TSH, progesterone) for enhanced accuracy and confidence."
        else:
            level = "low"
            recommendation = "Your assessment has limited reliability due to incomplete data or conflicting signals. We recommend tracking symptoms for 1-2 cycles and obtaining lab testing for accurate hormone evaluation. Consult a healthcare provider for proper diagnosis."
        
        return Confidence(
            level=level,
            score=self.score,
            calculation_breakdown=self.factors,
            recommendation=recommendation
        )
    
    def _add_factor(self, description: str, points: int):
        """Add a confidence factor"""
        self.factors.append(ConfidenceFactor(
            factor=description,
            points=points
        ))
        self.score += points
