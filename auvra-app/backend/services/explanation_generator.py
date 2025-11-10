"""
Clinical Explanation Generator
Generates user-friendly, evidence-based explanations for hormone imbalances
"""

from typing import Dict, List


class ExplanationGenerator:
    """Generate clinical explanations for hormone imbalances"""
    
    def __init__(self):
        self.explanations = {
            "androgens": self._generate_androgen_explanation,
            "estrogen": self._generate_estrogen_explanation,
            "progesterone": self._generate_progesterone_explanation,
            "insulin": self._generate_insulin_explanation,
            "cortisol": self._generate_cortisol_explanation,
            "thyroid": self._generate_thyroid_explanation
        }
        
        self.recommendations = {
            "androgens": self._get_androgen_recommendations,
            "estrogen": self._get_estrogen_recommendations,
            "progesterone": self._get_progesterone_recommendations,
            "insulin": self._get_insulin_recommendations,
            "cortisol": self._get_cortisol_recommendations,
            "thyroid": self._get_thyroid_recommendations
        }
    
    def generate_explanation(
        self, 
        hormone: str, 
        direction: str, 
        contributing_factors: List[str],
        has_labs: bool = False
    ) -> str:
        """Generate explanation for specific hormone imbalance"""
        
        if hormone in self.explanations:
            return self.explanations[hormone](direction, contributing_factors, has_labs)
        return "Explanation not available for this hormone."
    
    def get_recommendations(self, hormone: str, direction: str, has_labs: bool = False) -> Dict[str, List[str]]:
        """Get recommendations for specific hormone"""
        
        if hormone in self.recommendations:
            return self.recommendations[hormone](direction, has_labs)
        return {"testing": [], "lifestyle": [], "supplements": []}
    
    # ==================== ANDROGENS ====================
    
    def _generate_androgen_explanation(self, direction: str, factors: List[str], has_labs: bool) -> str:
        factors_text = ", ".join(factors[:3]) if factors else "various indicators"
        
        if direction == "high":
            explanation = f"""**TESTOSTERONE appears ELEVATED** based on:

**Supporting Evidence:**
{self._format_factors(factors)}

**What This Might Mean:**
Elevated androgens (testosterone, DHEA-S) can cause unwanted hair growth (hirsutism), acne, and irregular periods. In PCOS, this is often driven by insulin resistance affecting the ovaries and adrenal glands. High insulin stimulates ovarian testosterone production, creating a cycle that worsens both conditions.

This is commonly seen in Polycystic Ovary Syndrome (PCOS), which affects 8-13% of reproductive-age women. The androgen excess can disrupt normal ovulation, leading to irregular periods and difficulty conceiving.

**Impact on Your Health:**
- Disrupted menstrual cycles and ovulation
- Increased risk of insulin resistance and metabolic syndrome
- Potential fertility challenges
- Emotional and aesthetic concerns from hirsutism and acne"""
        else:
            explanation = f"""**TESTOSTERONE appears LOW** based on: {factors_text}

Low androgens in women can cause decreased libido, fatigue, and mood changes. This is less common but may occur with adrenal insufficiency or after oophorectomy."""
        
        return explanation
    
    def _get_androgen_recommendations(self, direction: str, has_labs: bool) -> Dict[str, List[str]]:
        if direction == "high":
            testing = ["Free testosterone and total testosterone", "DHEA-S (check adrenal contribution)", "LH:FSH ratio (PCOS indicator)"]
            if not has_labs:
                testing.append("Fasting insulin and HbA1c (insulin resistance)")
                testing.append("Pelvic ultrasound (check for polycystic ovaries)")
            
            return {
                "testing": testing,
                "lifestyle": [
                    "Low-glycemic diet to reduce insulin spikes (avoid refined carbs and sugar)",
                    "Strength training 3x/week to improve insulin sensitivity",
                    "Adequate protein at each meal (25-30g) to stabilize blood sugar",
                    "Manage stress through mindfulness, adequate sleep (7-9 hours)",
                    "Consider intermittent fasting (consult provider first)"
                ],
                "supplements": [
                    "Inositol (myo + d-chiro 40:1 ratio, 2-4g daily) - shown to reduce androgens and improve ovulation",
                    "Spearmint tea (2 cups daily) - clinically shown to reduce free testosterone",
                    "Zinc (30mg daily) - supports healthy testosterone metabolism",
                    "NAC (N-acetylcysteine, 600mg 2x daily) - antioxidant support for PCOS",
                    "Vitamin D3 (if deficient) - improves insulin sensitivity"
                ]
            }
        else:
            return {
                "testing": ["Free testosterone", "DHEA-S", "Cortisol (AM)"],
                "lifestyle": ["Strength training", "Adequate dietary fats", "Stress management"],
                "supplements": ["DHEA (consult provider)", "Zinc", "Magnesium"]
            }
    
    # ==================== ESTROGEN ====================
    
    def _generate_estrogen_explanation(self, direction: str, factors: List[str], has_labs: bool) -> str:
        if direction == "high":
            explanation = f"""**ESTROGEN appears ELEVATED** based on:

**Supporting Evidence:**
{self._format_factors(factors)}

**What This Might Mean:**
Estrogen dominance occurs when estrogen levels are too high relative to progesterone. This can cause heavy periods, bloating, breast tenderness, mood swings, and weight gain (especially around hips and thighs).

Common causes include:
- Progesterone deficiency (not enough to balance estrogen)
- Poor estrogen metabolism in the liver
- Xenoestrogen exposure (plastics, pesticides)
- High body fat (fat cells produce estrogen)
- Stress (cortisol blocks progesterone production)

**Impact on Your Health:**
- Heavy, painful periods increasing risk of anemia
- Increased risk of estrogen-sensitive conditions (fibroids, endometriosis)
- PMS and mood disturbances
- Potential increased risk of breast conditions with prolonged imbalance"""
        else:
            explanation = f"""**ESTROGEN appears LOW** based on:

**Supporting Evidence:**
{self._format_factors(factors)}

**What This Might Mean:**
Low estrogen in reproductive-age women is concerning and can indicate:
- Hypothalamic amenorrhea (stress, over-exercise, under-eating)
- Premature ovarian insufficiency (POI)
- Severe thyroid dysfunction
- Pituitary or hypothalamic disorders

Hot flashes in women under 40 are a RED FLAG requiring medical evaluation.

**Impact on Your Health:**
- Bone density loss (increased osteoporosis risk)
- Vaginal dryness and painful intercourse
- Mood changes and depression
- Cognitive effects (memory, focus)
- Cardiovascular health concerns"""
        
        return explanation
    
    def _get_estrogen_recommendations(self, direction: str, has_labs: bool) -> Dict[str, List[str]]:
        if direction == "high":
            return {
                "testing": ["Estradiol (Day 3 of cycle)", "Progesterone (Day 19-22)", "Liver function tests", "SHBG"],
                "lifestyle": [
                    "Increase cruciferous vegetables (broccoli, cauliflower, Brussels sprouts) - support estrogen metabolism",
                    "Reduce alcohol consumption (burdens liver estrogen clearance)",
                    "High-fiber diet (30g+ daily) to bind excess estrogen in gut",
                    "Regular exercise (avoid over-training)",
                    "Minimize plastics and xenoestrogen exposure"
                ],
                "supplements": [
                    "DIM (diindolylmethane, 200mg) - promotes healthy estrogen metabolism",
                    "Calcium-D-Glucarate (500mg) - supports estrogen detoxification",
                    "Magnesium glycinate (300-400mg evening) - supports progesterone production",
                    "Vitamin B-complex - liver support for hormone metabolism",
                    "Milk thistle - liver detoxification support"
                ]
            }
        else:
            return {
                "testing": ["Estradiol (Day 3)", "FSH and LH", "AMH (ovarian reserve)", "Thyroid panel", "Pituitary MRI if indicated"],
                "lifestyle": [
                    "Increase healthy fats (avocado, nuts, olive oil)",
                    "Ensure adequate caloric intake (don't under-eat)",
                    "Reduce excessive exercise if over-training",
                    "Manage stress (high cortisol suppresses estrogen)",
                    "Consider plant phytoestrogens (flax seeds, soy in moderation)"
                ],
                "supplements": [
                    "Omega-3 fatty acids (2g daily)",
                    "Vitamin E (400 IU daily)",
                    "B-complex vitamins",
                    "Note: Work with provider - may need hormone replacement"
                ]
            }
    
    # ==================== PROGESTERONE ====================
    
    def _generate_progesterone_explanation(self, direction: str, factors: List[str], has_labs: bool) -> str:
        explanation = f"""**PROGESTERONE appears LOW** based on:

**Supporting Evidence:**
{self._format_factors(factors)}

**What This Might Mean:**
Progesterone is produced after ovulation in the second half of your cycle (luteal phase). It has calming, mood-stabilizing effects by influencing GABA receptors in the brain. Low progesterone can cause:

- PMS and PMDD symptoms (mood swings, irritability, anxiety)
- Insomnia (especially premenstrual)
- Heavy or painful periods (estrogen goes "unopposed")
- Short luteal phase (<10 days after ovulation)
- Difficulty conceiving or early miscarriage

**Common Causes:**
- Anovulatory cycles (not ovulating regularly)
- Stress - cortisol directly blocks progesterone production
- Luteal phase defect
- Thyroid dysfunction
- Over-exercise or under-eating

**Impact on Your Health:**
- Mood and sleep disturbances affecting quality of life
- Increased estrogen dominance symptoms
- Fertility challenges if trying to conceive
- Increased anxiety and emotional sensitivity"""
        
        return explanation
    
    def _get_progesterone_recommendations(self, direction: str, has_labs: bool) -> Dict[str, List[str]]:
        return {
            "testing": [
                "Progesterone blood test on Day 19-22 of cycle (should be >10 ng/mL)",
                "Track basal body temperature to confirm ovulation",
                "Consider tracking LH surge with ovulation strips"
            ],
            "lifestyle": [
                "Stress management is CRITICAL - cortisol blocks progesterone production",
                "Ensure adequate sleep (7-9 hours) - progesterone is made during sleep",
                "Vitamin B6-rich foods (chickpeas, salmon, potatoes)",
                "Adequate cholesterol intake (progesterone is made from cholesterol)",
                "Avoid over-exercising - maintain healthy body fat percentage"
            ],
            "supplements": [
                "Vitamin B6 (50-100mg daily) - supports progesterone synthesis",
                "Magnesium glycinate (300-400mg evening) - improves PMS, supports progesterone",
                "Vitex (chasteberry, 400mg daily) - may support healthy progesterone levels",
                "L-theanine (for anxiety and sleep support)",
                "Consider bioidentical progesterone cream with provider guidance (severe PMS/PMDD)"
            ]
        }
    
    # ==================== INSULIN ====================
    
    def _generate_insulin_explanation(self, direction: str, factors: List[str], has_labs: bool) -> str:
        explanation = f"""**INSULIN RESISTANCE appears present** based on:

**Supporting Evidence:**
{self._format_factors(factors)}

**What This Might Mean:**
Insulin resistance occurs when your cells don't respond properly to insulin, forcing your pancreas to produce more. This leads to:

- Difficulty losing weight (especially stubborn belly fat)
- Constant hunger and sugar cravings
- Energy crashes after meals
- Fat storage instead of fat burning
- Increased androgens in women (worsens PCOS)

**Why It Matters:**
Insulin resistance is a pre-diabetic state affecting 30-40% of adults. If left unchecked, it progresses to type 2 diabetes. In women, it's the primary driver of PCOS and significantly impacts fertility, cardiovascular health, and metabolic function.

**Impact on Your Health:**
- Increased risk of type 2 diabetes and cardiovascular disease
- Worsens PCOS and androgen excess
- Promotes abdominal fat storage and inflammation
- Increases risk of non-alcoholic fatty liver disease"""
        
        return explanation
    
    def _get_insulin_recommendations(self, direction: str, has_labs: bool) -> Dict[str, List[str]]:
        return {
            "testing": [
                "Fasting insulin (>6 µIU/mL suggests resistance)",
                "HbA1c (>5.4% indicates concern)",
                "HOMA-IR calculation (insulin x glucose / 405)",
                "Oral glucose tolerance test with insulin measurements (gold standard)"
            ],
            "lifestyle": [
                "LOW-GLYCEMIC DIET - most important intervention",
                "Prioritize protein and healthy fats at each meal",
                "Avoid refined carbs, sugar, and processed foods",
                "Strength training 3-4x/week (builds insulin-sensitive muscle)",
                "Consider time-restricted eating (12-14 hour fasting window)",
                "Get 7-9 hours quality sleep (poor sleep worsens insulin resistance)",
                "Manage stress (cortisol worsens insulin resistance)"
            ],
            "supplements": [
                "Inositol (myo + d-chiro 40:1, 2-4g daily) - improves insulin sensitivity",
                "Berberine (500mg 3x daily with meals) - as effective as metformin in studies",
                "Chromium picolinate (200-400mcg) - improves glucose metabolism",
                "Omega-3 fish oil (2-3g daily) - reduces inflammation",
                "Alpha-lipoic acid (300-600mg) - improves insulin sensitivity",
                "Magnesium glycinate (400mg) - most deficient mineral in insulin resistance"
            ]
        }
    
    # ==================== CORTISOL ====================
    
    def _generate_cortisol_explanation(self, direction: str, factors: List[str], has_labs: bool) -> str:
        if direction == "high":
            explanation = f"""**CORTISOL appears ELEVATED** based on:

**Supporting Evidence:**
{self._format_factors(factors)}

**What This Might Mean:**
Chronic stress and elevated cortisol ("stress hormone") creates a cascade of hormonal disruptions:

- Suppresses progesterone production (cortisol steals pregnenolone)
- Disrupts thyroid function (reduces T3 conversion)
- Worsens insulin resistance (raises blood sugar)
- Disrupts sleep (especially waking 2-4am)
- Causes weight gain (especially belly fat and "cortisol face")

**Common Causes:**
- Chronic psychological stress (work, relationships, financial)
- Under-eating or over-exercising
- Chronic infections or inflammation
- Blood sugar dysregulation
- Poor sleep quality

**Impact on Your Health:**
- Anxiety, irritability, and difficulty relaxing
- Disrupted sleep and chronic fatigue
- Weakened immune function
- Accelerated aging and inflammation
- Increased risk of metabolic syndrome"""
        else:
            explanation = f"""**CORTISOL appears LOW** based on: {self._format_factors(factors)}

Low cortisol (adrenal fatigue/HPA axis dysfunction) occurs after chronic stress, causing extreme fatigue, low blood pressure, salt cravings, and difficulty handling stress. This requires medical evaluation to rule out Addison's disease."""
        
        return explanation
    
    def _get_cortisol_recommendations(self, direction: str, has_labs: bool) -> Dict[str, List[str]]:
        if direction == "high":
            return {
                "testing": [
                    "AM cortisol (should be highest in morning)",
                    "Consider 4-point salivary cortisol test (shows pattern throughout day)",
                    "DHEA-S (often low when cortisol is chronically high)"
                ],
                "lifestyle": [
                    "STRESS MANAGEMENT is essential - this is root cause",
                    "Daily mindfulness or meditation (10-20 minutes)",
                    "Moderate exercise only (avoid high-intensity if stressed)",
                    "Prioritize 7-9 hours sleep in completely dark room",
                    "Reduce caffeine (especially after noon)",
                    "Blood sugar balance (eat protein with every meal)",
                    "Set boundaries and reduce commitments where possible"
                ],
                "supplements": [
                    "Magnesium glycinate (400mg evening) - calming, improves sleep",
                    "Phosphatidylserine (300mg evening) - lowers cortisol",
                    "Ashwagandha (300-500mg) - adaptogen, reduces cortisol 25-30%",
                    "L-theanine (200mg) - promotes calm without drowsiness",
                    "Rhodiola rosea - adaptogen for stress resilience",
                    "Omega-3 fatty acids - reduces inflammation"
                ]
            }
        else:
            return {
                "testing": ["AM cortisol", "ACTH stimulation test", "DHEA-S", "Aldosterone"],
                "lifestyle": ["Adequate salt intake", "Small frequent meals", "Adequate rest", "Gentle movement only"],
                "supplements": ["Licorice root (if appropriate)", "Vitamin C", "B-complex", "DHEA (provider supervised)"]
            }
    
    # ==================== THYROID ====================
    
    def _generate_thyroid_explanation(self, direction: str, factors: List[str], has_labs: bool) -> str:
        explanation = f"""**THYROID FUNCTION appears LOW** based on:

**Supporting Evidence:**
{self._format_factors(factors)}

**What This Might Mean:**
Your thyroid controls your metabolic rate - affecting every cell in your body. Hypothyroidism (low thyroid function) causes:

- Fatigue and low energy (hallmark symptom)
- Weight gain despite diet/exercise efforts
- Cold intolerance (always feeling cold)
- Hair thinning and dry skin
- Constipation and bloating
- Brain fog and poor concentration
- Depression and mood changes

**Common Causes:**
- Hashimoto's thyroiditis (autoimmune - most common)
- Iodine or selenium deficiency
- High cortisol (blocks thyroid hormone conversion)
- Estrogen dominance (increases TBG, reducing free thyroid hormones)

**Important Note:**
Many women have "normal" TSH but still have symptoms. Optimal TSH is 0.5-2.0 mIU/L, NOT just <4.5. Free T3 (active hormone) is often more important than TSH.

**Impact on Your Health:**
- Significantly reduced quality of life from fatigue
- Increased cardiovascular risk
- Fertility challenges
- Cognitive decline if untreated
- Progression to overt hypothyroidism"""
        
        return explanation
    
    def _get_thyroid_recommendations(self, direction: str, has_labs: bool) -> Dict[str, List[str]]:
        return {
            "testing": [
                "TSH (optimal: 0.5-2.0 mIU/L, not just 'normal')",
                "Free T3 (most active hormone - should be upper half of range)",
                "Free T4",
                "Thyroid antibodies: TPO and Thyroglobulin (check for Hashimoto's)",
                "Reverse T3 (if Free T3 is low despite normal TSH)",
                "Selenium and iodine levels"
            ],
            "lifestyle": [
                "Ensure adequate iodine from seafood, seaweed, iodized salt",
                "Brazil nuts (selenium) - 2-3 daily provides 200mcg selenium",
                "Gluten-free trial if Hashimoto's (reduces antibodies in many)",
                "Address gut health (70% of T4→T3 conversion happens in gut)",
                "Manage stress (cortisol inhibits thyroid conversion)",
                "Avoid raw cruciferous vegetables in excess (goitrogens)",
                "Ensure adequate protein and healthy fats"
            ],
            "supplements": [
                "Selenium (200mcg daily) - shown to reduce thyroid antibodies in Hashimoto's",
                "Zinc (30mg) - needed for thyroid hormone production",
                "Vitamin D3 (if deficient) - thyroid receptor function",
                "Iron (if deficient) - required for thyroid peroxidase enzyme",
                "B-complex - supports energy and thyroid function",
                "L-tyrosine (if appropriate) - building block of thyroid hormones",
                "Consider levothyroxine with doctor if TSH >2.5 with symptoms"
            ]
        }
    
    # ==================== HELPER METHODS ====================
    
    def _format_factors(self, factors: List[str]) -> str:
        """Format contributing factors as bullet list"""
        if not factors:
            return "- General indicators present"
        
        formatted = []
        for factor in factors[:5]:  # Limit to top 5 factors
            formatted.append(f"- {factor}")
        
        if len(factors) > 5:
            formatted.append(f"- ...and {len(factors) - 5} additional indicators")
        
        return "\n".join(formatted)
