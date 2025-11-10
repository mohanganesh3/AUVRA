"""
Cycle Phase Calculator and Context Generator
Calculates current cycle phase and provides phase-aware adjustments
"""

from datetime import date, timedelta
from typing import Optional, Tuple
from models.schemas import CycleContext


class CycleCalculator:
    """Calculate cycle phase and context"""
    
    def __init__(self):
        self.phase_names = {
            "menstrual": "Menstrual/Early Follicular",
            "follicular": "Late Follicular/Ovulation Window",
            "luteal": "Luteal Phase",
            "late_luteal": "Late Luteal/PMS Window"
        }
    
    def calculate_cycle_context(
        self, 
        last_period_date: Optional[date],
        cycle_length: str,
        date_not_sure: bool = False
    ) -> CycleContext:
        """Calculate current cycle phase and context"""
        
        if date_not_sure or not last_period_date:
            return CycleContext(
                current_phase=None,
                days_since_period=None,
                phase_confidence="low",
                estimated_next_period=None
            )
        
        # Calculate days since last period
        today = date.today()
        days_since = (today - last_period_date).days
        
        # Parse cycle length
        avg_cycle_days = self._parse_cycle_length(cycle_length)
        
        if avg_cycle_days is None:
            return CycleContext(
                current_phase=None,
                days_since_period=days_since,
                phase_confidence="low",
                estimated_next_period=None
            )
        
        # Determine phase
        phase = self._determine_phase(days_since, avg_cycle_days)
        
        # Calculate next period estimate
        next_period = last_period_date + timedelta(days=avg_cycle_days)
        
        # Determine confidence based on cycle regularity
        if cycle_length in ["26-30", "21-25"]:
            confidence = "high"
        elif cycle_length in ["31-35", "<21"]:
            confidence = "medium"
        else:
            confidence = "low"
        
        return CycleContext(
            current_phase=phase,
            days_since_period=days_since,
            phase_confidence=confidence,
            estimated_next_period=next_period
        )
    
    def _parse_cycle_length(self, cycle_length: str) -> Optional[int]:
        """Parse cycle length string to average days"""
        mapping = {
            "<21": 20,
            "21-25": 23,
            "26-30": 28,
            "31-35": 33,
            "35+": 40,
            "not_sure": None
        }
        return mapping.get(cycle_length)
    
    def _determine_phase(self, days_since: int, cycle_length: int) -> str:
        """Determine cycle phase based on days since period"""
        
        if days_since <= 7:
            return "menstrual"
        elif days_since <= 14:
            return "follicular"
        elif days_since <= (cycle_length - 3):
            return "luteal"
        else:
            return "late_luteal"
    
    def is_phase_normal_symptom(self, symptom: str, phase: Optional[str]) -> bool:
        """Check if symptom is normal for given cycle phase"""
        
        if not phase:
            return False
        
        # Late luteal phase normal symptoms (PMS)
        late_luteal_normal = [
            "bloating",
            "breast_tenderness",
            "mood_swings",
            "sugar_cravings",
            "mild_cramps"
        ]
        
        # Menstrual phase normal symptoms
        menstrual_normal = [
            "cramps",
            "fatigue",
            "mild_mood_dips"
        ]
        
        if phase == "late_luteal" and symptom in late_luteal_normal:
            return True
        
        if phase == "menstrual" and symptom in menstrual_normal:
            return True
        
        return False
