"""
Core Hormone Scoring Engine
Implements the heuristic-based scoring system for all 6 hormones
Based on clinical documentation and validated questionnaires
"""

from typing import Dict, List, Tuple, Optional
from datetime import date, datetime
from models.schemas import *


class HormoneScorer:
    """Main hormone scoring engine"""
    
    def __init__(self):
        """Initialize hormone scores structure"""
        self.hormone_scores = {
            "estrogen": {
                "from_symptoms": 0,
                "from_diagnosis": 0,
                "from_labs": 0,
                "total": 0,
                "direction": "high",  # Can be "high" or "low"
                "high_score": 0,  # Track both directions
                "low_score": 0
            },
            "progesterone": {
                "from_symptoms": 0,
                "from_diagnosis": 0,
                "from_labs": 0,
                "total": 0,
                "direction": "low"
            },
            "androgens": {
                "from_symptoms": 0,
                "from_diagnosis": 0,
                "from_labs": 0,
                "total": 0,
                "direction": "high"
            },
            "insulin": {
                "from_symptoms": 0,
                "from_diagnosis": 0,
                "from_labs": 0,
                "total": 0,
                "direction": "high"
            },
            "cortisol": {
                "from_symptoms": 0,
                "from_diagnosis": 0,
                "from_labs": 0,
                "total": 0,
                "direction": "high",  # Can be "high" or "low"
                "high_score": 0,
                "low_score": 0
            },
            "thyroid": {
                "from_symptoms": 0,
                "from_diagnosis": 0,
                "from_labs": 0,
                "total": 0,
                "direction": "low"
            }
        }
        
        self.contributing_factors = {hormone: [] for hormone in self.hormone_scores}
        self.birth_control_modifier = 1.0
        self.top_concern_multiplier = 1.0
        
    def score_period_pattern(self, pattern: str) -> None:
        """Question 2: Score period pattern"""
        if pattern == "regular":
            # Baseline - no scoring
            pass
        elif pattern == "not_sure":
            # User uncertain – do not apply scoring adjustments
            pass
        
        elif pattern == "irregular":
            self.hormone_scores["androgens"]["from_symptoms"] += 2
            self.hormone_scores["thyroid"]["from_symptoms"] += 1
            self.hormone_scores["cortisol"]["from_symptoms"] += 1
            self.hormone_scores["cortisol"]["high_score"] += 1
            
            self.contributing_factors["androgens"].append("Irregular periods (strong PCOS indicator)")
            self.contributing_factors["thyroid"].append("Irregular periods")
            self.contributing_factors["cortisol"].append("Irregular periods (stress-related)")
        
        elif pattern == "occasional_skips":
            self.hormone_scores["androgens"]["from_symptoms"] += 1
            self.hormone_scores["cortisol"]["from_symptoms"] += 1
            self.hormone_scores["cortisol"]["high_score"] += 1
            self.hormone_scores["progesterone"]["from_symptoms"] += 1
            
            self.contributing_factors["androgens"].append("Occasional period skips")
            self.contributing_factors["cortisol"].append("Occasional period skips (stress)")
            self.contributing_factors["progesterone"].append("Occasional period skips (ovulation disruption)")
        
        elif pattern == "no_periods":
            self.hormone_scores["androgens"]["from_symptoms"] += 2
            self.hormone_scores["estrogen"]["from_symptoms"] += 1
            self.hormone_scores["estrogen"]["low_score"] += 1
            self.hormone_scores["thyroid"]["from_symptoms"] += 2
            
            self.contributing_factors["androgens"].append("Amenorrhea (absence of periods)")
            self.contributing_factors["estrogen"].append("Amenorrhea (possible low estrogen)")
            self.contributing_factors["thyroid"].append("Amenorrhea (possible hypothyroidism)")
    
    def apply_birth_control_modifier(self, bc_type: str) -> None:
        """Question 2B: Apply birth control modifier"""
        if bc_type == "hormonal_pills":
            self.birth_control_modifier = 0.7  # 30% reduction
        elif bc_type == "hormonal_iud":
            self.birth_control_modifier = 0.8  # 20% reduction
        else:
            self.birth_control_modifier = 1.0  # No adjustment
    
    def score_cycle_length(self, length: str) -> None:
        """Question 3: Score cycle length"""
        if length == "<21":
            self.hormone_scores["estrogen"]["from_symptoms"] += 1
            self.hormone_scores["estrogen"]["high_score"] += 1
            self.hormone_scores["progesterone"]["from_symptoms"] += 1
            
            self.contributing_factors["estrogen"].append("Short cycle (<21 days)")
            self.contributing_factors["progesterone"].append("Short luteal phase")
        
        elif length == "26-30":
            # Normal range - no adjustments
            pass
        
        elif length == "31-35":
            self.hormone_scores["androgens"]["from_symptoms"] += 1
            self.hormone_scores["thyroid"]["from_symptoms"] += 1
            
            self.contributing_factors["androgens"].append("Long cycle (31-35 days)")
            self.contributing_factors["thyroid"].append("Long cycle")
        
        elif length == "35+":
            self.hormone_scores["androgens"]["from_symptoms"] += 2
            self.hormone_scores["insulin"]["from_symptoms"] += 1
            self.hormone_scores["thyroid"]["from_symptoms"] += 1
            
            self.contributing_factors["androgens"].append("Very long cycle (35+ days) - strong PCOS indicator")
            self.contributing_factors["insulin"].append("Very long cycle (insulin resistance)")
            self.contributing_factors["thyroid"].append("Very long cycle")
    
    def score_health_concerns(self, concerns: HealthConcernsRequest, cycle_phase: Optional[str] = None) -> None:
        """Question 4: Score health concerns with cycle phase awareness"""
        
        # PERIOD CONCERNS
        if "irregular_periods" in concerns.period_concerns:
            self.hormone_scores["androgens"]["from_symptoms"] += 2
            self.hormone_scores["thyroid"]["from_symptoms"] += 1
            self.hormone_scores["cortisol"]["from_symptoms"] += 1
            self.hormone_scores["cortisol"]["high_score"] += 1
            self.contributing_factors["androgens"].append("Irregular periods selected as concern")
        
        if "painful_periods" in concerns.period_concerns:
            self.hormone_scores["estrogen"]["from_symptoms"] += 1
            self.hormone_scores["estrogen"]["high_score"] += 1
            self.hormone_scores["progesterone"]["from_symptoms"] += 2
            self.contributing_factors["progesterone"].append("Painful periods (progesterone deficiency)")
        
        if "light_periods" in concerns.period_concerns:
            self.hormone_scores["estrogen"]["from_symptoms"] += 2
            self.hormone_scores["estrogen"]["low_score"] += 2
            self.hormone_scores["progesterone"]["from_symptoms"] += 1
            self.hormone_scores["thyroid"]["from_symptoms"] += 1
            self.contributing_factors["estrogen"].append("Light periods/spotting (low estrogen)")
        
        if "heavy_periods" in concerns.period_concerns:
            self.hormone_scores["estrogen"]["from_symptoms"] += 2
            self.hormone_scores["estrogen"]["high_score"] += 2
            self.hormone_scores["progesterone"]["from_symptoms"] += 1
            self.contributing_factors["estrogen"].append("Heavy periods (estrogen dominance)")
        
        # BODY CONCERNS
        if "bloating" in concerns.body_concerns:
            # Check if late luteal phase (normal PMS)
            if cycle_phase == "late_luteal":
                score_modifier = 0.5  # Reduce by 50% - it's phase-normal
            else:
                score_modifier = 1.0
            
            self.hormone_scores["estrogen"]["from_symptoms"] += int(2 * score_modifier)
            self.hormone_scores["estrogen"]["high_score"] += int(2 * score_modifier)
            self.hormone_scores["cortisol"]["from_symptoms"] += int(1 * score_modifier)
            self.hormone_scores["cortisol"]["high_score"] += int(1 * score_modifier)
            
            if cycle_phase == "late_luteal":
                self.contributing_factors["estrogen"].append("Bloating (phase-normal PMS)")
            else:
                self.contributing_factors["estrogen"].append("Bloating (estrogen excess)")
        
        if "hot_flashes" in concerns.body_concerns:
            self.hormone_scores["estrogen"]["from_symptoms"] += 3
            self.hormone_scores["estrogen"]["low_score"] += 3
            self.hormone_scores["thyroid"]["from_symptoms"] += 1
            self.contributing_factors["estrogen"].append("Hot flashes (severe estrogen deficiency - HIGH URGENCY)")
        
        if "nausea" in concerns.body_concerns:
            self.hormone_scores["estrogen"]["from_symptoms"] += 1
            self.hormone_scores["estrogen"]["high_score"] += 1
            self.contributing_factors["estrogen"].append("Nausea (estrogen spikes)")
        
        if "weight_difficulty" in concerns.body_concerns:
            self.hormone_scores["insulin"]["from_symptoms"] += 2
            self.hormone_scores["cortisol"]["from_symptoms"] += 2
            self.hormone_scores["cortisol"]["high_score"] += 2
            self.hormone_scores["thyroid"]["from_symptoms"] += 2
            self.contributing_factors["insulin"].append("Difficulty losing weight/stubborn belly fat")
            self.contributing_factors["cortisol"].append("Difficulty losing weight/stubborn belly fat")
            self.contributing_factors["thyroid"].append("Difficulty losing weight/stubborn belly fat")
        
        if "recent_weight_gain" in concerns.body_concerns:
            self.hormone_scores["thyroid"]["from_symptoms"] += 2
            self.hormone_scores["cortisol"]["from_symptoms"] += 1
            self.hormone_scores["cortisol"]["high_score"] += 1
            self.hormone_scores["insulin"]["from_symptoms"] += 1
            self.contributing_factors["thyroid"].append("Recent weight gain (primary suspect)")
        
        if "menstrual_headaches" in concerns.body_concerns:
            self.hormone_scores["estrogen"]["from_symptoms"] += 1
            self.hormone_scores["estrogen"]["low_score"] += 1
            self.hormone_scores["progesterone"]["from_symptoms"] += 1
            self.contributing_factors["estrogen"].append("Menstrual headaches (estrogen withdrawal)")
        
        # SKIN AND HAIR CONCERNS
        if "hirsutism" in concerns.skin_hair_concerns:
            self.hormone_scores["androgens"]["from_symptoms"] += 3
            self.contributing_factors["androgens"].append("Hirsutism (VERY HIGH severity - direct androgen marker)")
        
        if "hair_thinning" in concerns.skin_hair_concerns:
            self.hormone_scores["thyroid"]["from_symptoms"] += 2
            self.hormone_scores["androgens"]["from_symptoms"] += 1
            self.hormone_scores["cortisol"]["from_symptoms"] += 1
            self.hormone_scores["cortisol"]["high_score"] += 1
            self.contributing_factors["thyroid"].append("Hair thinning (most common cause)")
        
        if "adult_acne" in concerns.skin_hair_concerns:
            self.hormone_scores["androgens"]["from_symptoms"] += 2
            self.hormone_scores["insulin"]["from_symptoms"] += 1
            self.contributing_factors["androgens"].append("Adult acne (androgen-driven)")
        
        # MENTAL HEALTH CONCERNS
        if "mood_swings" in concerns.mental_health_concerns:
            # Check if late luteal phase (normal PMS)
            if cycle_phase == "late_luteal":
                score_modifier = 0.5
            else:
                score_modifier = 1.0
            
            self.hormone_scores["progesterone"]["from_symptoms"] += int(2 * score_modifier)
            self.hormone_scores["cortisol"]["from_symptoms"] += int(1 * score_modifier)
            self.hormone_scores["cortisol"]["high_score"] += int(1 * score_modifier)
            self.hormone_scores["estrogen"]["from_symptoms"] += int(1 * score_modifier)
            
            if cycle_phase == "late_luteal":
                self.contributing_factors["progesterone"].append("Mood swings (phase-normal PMS)")
            else:
                self.contributing_factors["progesterone"].append("Mood swings (progesterone deficiency)")
        
        if "stress" in concerns.mental_health_concerns:
            self.hormone_scores["cortisol"]["from_symptoms"] += 2
            self.hormone_scores["cortisol"]["high_score"] += 2
            # Cortisol suppresses progesterone
            self.contributing_factors["cortisol"].append("Chronic stress (elevated cortisol)")
        
        if "fatigue" in concerns.mental_health_concerns:
            self.hormone_scores["thyroid"]["from_symptoms"] += 2
            self.hormone_scores["cortisol"]["from_symptoms"] += 2
            # Could be high or low cortisol - track both
            self.hormone_scores["cortisol"]["high_score"] += 1
            self.hormone_scores["cortisol"]["low_score"] += 1
            self.hormone_scores["insulin"]["from_symptoms"] += 1
            self.contributing_factors["thyroid"].append("Fatigue (most commonly hypothyroidism)")
    
    def apply_top_concern_multiplier(self, top_concern: str, health_concerns: HealthConcernsRequest) -> None:
        """Question 5: Apply 1.5x multiplier to hormones linked to the top concern.
        We inflate the symptom-derived score portion for associated hormones by 50% (rounding up).
        The mapping supports both display labels and token forms to be resilient to front-end changes.
        """
        if not top_concern or top_concern == "none":
            return

        mapping = {
            # Period concerns
            "irregular_periods": ["androgens", "thyroid", "cortisol"],
            "Irregular Periods": ["androgens", "thyroid", "cortisol"],
            "painful_periods": ["estrogen", "progesterone"],
            "Painful Periods": ["estrogen", "progesterone"],
            "light_periods": ["estrogen", "progesterone", "thyroid"],
            "Light periods / Spotting": ["estrogen", "progesterone", "thyroid"],
            "heavy_periods": ["estrogen", "progesterone"],
            "Heavy periods": ["estrogen", "progesterone"],
            # Body concerns
            "bloating": ["estrogen", "cortisol"],
            "Bloating": ["estrogen", "cortisol"],
            "hot_flashes": ["estrogen", "thyroid"],
            "Hot Flashes": ["estrogen", "thyroid"],
            "nausea": ["estrogen"],
            "Nausea": ["estrogen"],
            "weight_difficulty": ["insulin", "cortisol", "thyroid"],
            "Difficulty losing weight / stubborn belly fat": ["insulin", "cortisol", "thyroid"],
            "recent_weight_gain": ["thyroid", "cortisol", "insulin"],
            "Recent weight gain": ["thyroid", "cortisol", "insulin"],
            "menstrual_headaches": ["estrogen", "progesterone"],
            "Menstrual headaches": ["estrogen", "progesterone"],
            # Skin/Hair
            "hirsutism": ["androgens"],
            "Hirsutism (hair growth on chin, nipples etc)": ["androgens"],
            "hair_thinning": ["thyroid", "androgens", "cortisol"],
            "Thinning of hair": ["thyroid", "androgens", "cortisol"],
            "adult_acne": ["androgens", "insulin"],
            "Adult Acne": ["androgens", "insulin"],
            # Mental
            "mood_swings": ["progesterone", "cortisol", "estrogen"],
            "Mood swings": ["progesterone", "cortisol", "estrogen"],
            "stress": ["cortisol"],
            "Stress": ["cortisol"],
            "fatigue": ["thyroid", "cortisol", "insulin"],
            "Fatigue": ["thyroid", "cortisol", "insulin"],
        }

        target_hormones = mapping.get(top_concern, [])
        if not target_hormones:
            return

        for hormone in target_hormones:
            original = self.hormone_scores[hormone]["from_symptoms"]
            if original > 0:  # Only boost if symptom contributed
                boosted = int((original * 1.5) + 0.5)  # round up
                delta = boosted - original
                self.hormone_scores[hormone]["from_symptoms"] = boosted
                self.contributing_factors[hormone].append(f"Top concern emphasis (+{delta}) for '{top_concern}'")
    
    def score_diagnosed_conditions(self, conditions: List[str]) -> None:
        """Question 6: Score diagnosed conditions"""
        
        if "pcos" in conditions:
            self.hormone_scores["androgens"]["from_diagnosis"] += 3
            self.hormone_scores["insulin"]["from_diagnosis"] += 3
            self.contributing_factors["androgens"].append("PCOS diagnosis")
            self.contributing_factors["insulin"].append("PCOS diagnosis (insulin resistance)")
        
        if "pcod" in conditions:
            self.hormone_scores["androgens"]["from_diagnosis"] += 2
            self.hormone_scores["insulin"]["from_diagnosis"] += 2
            self.contributing_factors["androgens"].append("PCOD diagnosis")
        
        if "endometriosis" in conditions:
            self.hormone_scores["estrogen"]["from_diagnosis"] += 3
            self.hormone_scores["estrogen"]["high_score"] += 3
            self.contributing_factors["estrogen"].append("Endometriosis diagnosis (estrogen-driven)")
        
        if "dysmenorrhea" in conditions:
            self.hormone_scores["estrogen"]["from_diagnosis"] += 1
            self.hormone_scores["estrogen"]["high_score"] += 1
            self.hormone_scores["progesterone"]["from_diagnosis"] += 2
            self.contributing_factors["progesterone"].append("Dysmenorrhea (painful periods)")
        
        if "amenorrhea" in conditions:
            self.hormone_scores["estrogen"]["from_diagnosis"] += 3
            self.hormone_scores["estrogen"]["low_score"] += 3
            self.hormone_scores["androgens"]["from_diagnosis"] += 2
            self.hormone_scores["thyroid"]["from_diagnosis"] += 2
            self.contributing_factors["estrogen"].append("Amenorrhea diagnosis")
        
        if "menorrhagia" in conditions:
            self.hormone_scores["estrogen"]["from_diagnosis"] += 3
            self.hormone_scores["estrogen"]["high_score"] += 3
            self.hormone_scores["progesterone"]["from_diagnosis"] += 1
            self.contributing_factors["estrogen"].append("Menorrhagia (heavy bleeding)")
        
        if "metrorrhagia" in conditions:
            self.hormone_scores["estrogen"]["from_diagnosis"] += 2
            self.hormone_scores["progesterone"]["from_diagnosis"] += 2
            self.contributing_factors["estrogen"].append("Metrorrhagia (irregular bleeding)")
        
        if "pms" in conditions:
            self.hormone_scores["progesterone"]["from_diagnosis"] += 1
            self.hormone_scores["estrogen"]["from_diagnosis"] += 1
            self.contributing_factors["progesterone"].append("PMS diagnosis")
        
        if "pmdd" in conditions:
            self.hormone_scores["progesterone"]["from_diagnosis"] += 3
            self.hormone_scores["cortisol"]["from_diagnosis"] += 2
            self.hormone_scores["cortisol"]["high_score"] += 2
            self.contributing_factors["progesterone"].append("PMDD diagnosis (severe progesterone sensitivity)")
        
        if "hashimotos" in conditions or "hypothyroidism" in conditions:
            self.hormone_scores["thyroid"]["from_diagnosis"] += 3
            self.contributing_factors["thyroid"].append("Thyroid condition diagnosis")
    
    def score_lab_results(self, labs: Optional[LabResultsRequest]) -> Dict[str, List[str]]:
        """Score lab results and return concordance information"""
        if not labs:
            return {}
        
        concordance_notes = {}
        print("[LAB SCORING] Raw lab inputs:")
        for field in [
            'total_testosterone','free_testosterone','dhea_s','lh','fsh','tsh','free_t3','free_t4',
            'fasting_insulin','hba1c','fasting_glucose','am_cortisol','estradiol','progesterone','shbg']:
            val = getattr(labs, field, None)
            if val is not None:
                print(f"  - {field}: {val}")
        
        # Androgens
        if labs.free_testosterone and labs.free_testosterone > 2.0:
            self.hormone_scores["androgens"]["from_labs"] += 2
            self.contributing_factors["androgens"].append(f"Free testosterone elevated ({labs.free_testosterone} pg/mL)")
            print(f"    [LAB→androgens] Free testosterone >2.0 adds +2 (value={labs.free_testosterone})")
        
        if labs.total_testosterone and labs.total_testosterone > 60:
            self.hormone_scores["androgens"]["from_labs"] += 2
            self.contributing_factors["androgens"].append(f"Total testosterone elevated ({labs.total_testosterone} ng/dL)")
            print(f"    [LAB→androgens] Total testosterone >60 adds +2 (value={labs.total_testosterone})")
        
        if labs.dhea_s and labs.dhea_s > 300:
            self.hormone_scores["androgens"]["from_labs"] += 2
            self.contributing_factors["androgens"].append(f"DHEA-S elevated ({labs.dhea_s} µg/dL) - adrenal source")
            print(f"    [LAB→androgens] DHEA-S >300 adds +2 (value={labs.dhea_s})")
        
        # LH:FSH ratio for PCOS
        if labs.lh and labs.fsh and labs.fsh > 0:
            ratio = labs.lh / labs.fsh
            if ratio > 2.5:
                self.hormone_scores["androgens"]["from_labs"] += 2
                self.contributing_factors["androgens"].append(f"LH:FSH ratio elevated ({ratio:.2f}) - PCOS indicator")
                print(f"    [LAB→androgens] LH:FSH ratio {ratio:.2f} >2.5 adds +2")
        
        # Thyroid
        if labs.tsh:
            if 2.5 < labs.tsh <= 4.5:
                self.hormone_scores["thyroid"]["from_labs"] += 2
                self.contributing_factors["thyroid"].append(f"TSH subclinical range ({labs.tsh} mIU/L)")
                print(f"    [LAB→thyroid] TSH subclinical (2.5-4.5) adds +2 (value={labs.tsh})")
            elif labs.tsh > 4.5:
                self.hormone_scores["thyroid"]["from_labs"] += 3
                self.contributing_factors["thyroid"].append(f"TSH elevated ({labs.tsh} mIU/L) - hypothyroidism")
                print(f"    [LAB→thyroid] TSH >4.5 adds +3 (value={labs.tsh})")
        
        if labs.free_t3 and labs.free_t3 < 2.5:
            self.hormone_scores["thyroid"]["from_labs"] += 2
            self.contributing_factors["thyroid"].append(f"Free T3 low ({labs.free_t3} pg/mL)")
            print(f"    [LAB→thyroid] Free T3 <2.5 adds +2 (value={labs.free_t3})")
        
        if labs.free_t4 and labs.free_t4 < 1.0:
            self.hormone_scores["thyroid"]["from_labs"] += 1
            self.contributing_factors["thyroid"].append(f"Free T4 low ({labs.free_t4} ng/dL)")
            print(f"    [LAB→thyroid] Free T4 <1.0 adds +1 (value={labs.free_t4})")
        
        # Insulin
        if labs.fasting_insulin and labs.fasting_insulin > 6:
            self.hormone_scores["insulin"]["from_labs"] += 2
            self.contributing_factors["insulin"].append(f"Fasting insulin elevated ({labs.fasting_insulin} µIU/mL)")
            print(f"    [LAB→insulin] Fasting insulin >6 adds +2 (value={labs.fasting_insulin})")
        
        if labs.hba1c and labs.hba1c > 5.4:
            self.hormone_scores["insulin"]["from_labs"] += 2
            self.contributing_factors["insulin"].append(f"HbA1c prediabetic range ({labs.hba1c}%)")
            print(f"    [LAB→insulin] HbA1c >5.4 adds +2 (value={labs.hba1c})")
        
        if labs.fasting_glucose and labs.fasting_glucose > 100:
            self.hormone_scores["insulin"]["from_labs"] += 1
            self.contributing_factors["insulin"].append(f"Fasting glucose elevated ({labs.fasting_glucose} mg/dL)")
            print(f"    [LAB→insulin] Fasting glucose >100 adds +1 (value={labs.fasting_glucose})")
        
        # Cortisol
        if labs.am_cortisol:
            if labs.am_cortisol > 20:
                self.hormone_scores["cortisol"]["from_labs"] += 2
                self.hormone_scores["cortisol"]["high_score"] += 2
                self.contributing_factors["cortisol"].append(f"AM cortisol elevated ({labs.am_cortisol} µg/dL)")
                print(f"    [LAB→cortisol] AM cortisol >20 adds +2 HIGH (value={labs.am_cortisol})")
            elif labs.am_cortisol < 6:
                self.hormone_scores["cortisol"]["from_labs"] += 2
                self.hormone_scores["cortisol"]["low_score"] += 2
                self.contributing_factors["cortisol"].append(f"AM cortisol low ({labs.am_cortisol} µg/dL)")
                print(f"    [LAB→cortisol] AM cortisol <6 adds +2 LOW (value={labs.am_cortisol})")
        
        # Estrogen
        if labs.estradiol:
            # Day 3 reference: 30-100 pg/mL
            if labs.estradiol < 30:
                self.hormone_scores["estrogen"]["from_labs"] += 2
                self.hormone_scores["estrogen"]["low_score"] += 2
                self.contributing_factors["estrogen"].append(f"Estradiol low ({labs.estradiol} pg/mL)")
                print(f"    [LAB→estrogen] Estradiol <30 adds +2 LOW (value={labs.estradiol})")
            elif labs.estradiol > 100:
                self.hormone_scores["estrogen"]["from_labs"] += 2
                self.hormone_scores["estrogen"]["high_score"] += 2
                self.contributing_factors["estrogen"].append(f"Estradiol elevated ({labs.estradiol} pg/mL)")
                print(f"    [LAB→estrogen] Estradiol >100 adds +2 HIGH (value={labs.estradiol})")
        
        # Progesterone
        if labs.progesterone and labs.progesterone < 5:
            self.hormone_scores["progesterone"]["from_labs"] += 2
            self.contributing_factors["progesterone"].append(f"Progesterone low ({labs.progesterone} ng/mL)")
            print(f"    [LAB→progesterone] Progesterone <5 adds +2 (value={labs.progesterone})")
        
        # SHBG modifier
        if labs.shbg:
            if labs.shbg < 30:
                self.hormone_scores["androgens"]["from_labs"] += 1
                self.contributing_factors["androgens"].append(f"Low SHBG ({labs.shbg} nmol/L) - increases free androgens")
                print(f"    [LAB→androgens] SHBG <30 adds +1 (value={labs.shbg})")
            elif labs.shbg > 100:
                self.hormone_scores["androgens"]["from_labs"] -= 1
                self.contributing_factors["androgens"].append(f"High SHBG ({labs.shbg} nmol/L) - decreases free androgens")
                print(f"    [LAB→androgens] SHBG >100 subtracts 1 (value={labs.shbg})")
        
        return concordance_notes
    
    def calculate_final_scores(self) -> None:
        """Calculate final scores with all modifiers"""
        for hormone in self.hormone_scores:
            # Sum all sources
            total = (
                self.hormone_scores[hormone]["from_symptoms"] +
                self.hormone_scores[hormone]["from_diagnosis"] +
                self.hormone_scores[hormone]["from_labs"]
            )
            
            # Apply birth control modifier
            total = int(total * self.birth_control_modifier)
            
            # Determine direction for bi-directional hormones
            if hormone in ["estrogen", "cortisol"]:
                high = self.hormone_scores[hormone].get("high_score", 0)
                low = self.hormone_scores[hormone].get("low_score", 0)
                if high > low:
                    self.hormone_scores[hormone]["direction"] = "high"
                elif low > high:
                    self.hormone_scores[hormone]["direction"] = "low"
            
            self.hormone_scores[hormone]["total"] = total
    
    def get_primary_secondary_imbalances(self) -> Tuple[str, List[str]]:
        """Identify primary and secondary hormone imbalances"""
        # Sort hormones by total score
        sorted_hormones = sorted(
            self.hormone_scores.items(),
            key=lambda x: x[1]["total"],
            reverse=True
        )
        
        # Tie-breaking priority
        priority = ["androgens", "thyroid", "insulin", "estrogen", "cortisol", "progesterone"]
        
        # Get primary
        primary = sorted_hormones[0][0]
        primary_score = sorted_hormones[0][1]["total"]
        
        # Get secondary (>= 50% of primary score)
        threshold = primary_score * 0.5
        secondary = []
        
        for hormone, data in sorted_hormones[1:]:
            if data["total"] >= threshold:
                secondary.append(hormone)
        
        return primary, secondary
    
    def get_hormone_breakdown(self, hormone: str) -> HormoneBreakdown:
        """Get breakdown for specific hormone"""
        return HormoneBreakdown(
            from_symptoms=self.hormone_scores[hormone]["from_symptoms"],
            from_diagnosis=self.hormone_scores[hormone]["from_diagnosis"],
            from_labs=self.hormone_scores[hormone]["from_labs"]
        )
