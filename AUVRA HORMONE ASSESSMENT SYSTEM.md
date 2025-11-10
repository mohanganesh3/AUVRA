 **AUVRA HORMONE ASSESSMENT SYSTEM**  
 **Backend Clinical Documentation for Mobile Application**

**Document Version:** 1.0  
 **Last Updated:** November 7, 2025  
 **Target Population:** Women aged 18-40  
 **Purpose:** Hormone imbalance screening and confidence scoring system

---

**EXECUTIVE SUMMARY**

This document outlines the backend scoring logic for the Auvra mobile hormone assessment system. The system evaluates six key hormones (Estrogen, Progesterone, Androgens, Insulin, Cortisol, Thyroid) through a symptom-based questionnaire, diagnosis matching, and optional lab report integration. The output identifies primary and secondary hormone imbalances with a confidence score (Low/Medium/High) to guide users toward appropriate health interventions.

**Key Features:**

* Heuristic-based scoring aligned with Rotterdam, NIH, ACOG, and Endocrine Society guidelines

* LLM integration (Gemini API) for processing user-entered "other" conditions

* Cycle phase-aware scoring to differentiate normal from abnormal symptoms

* Lab report overlay for enhanced accuracy

* Conflict detection for contradictory hormone signals

---

**SECTION 1: SYSTEM OVERVIEW**

**1.1 Hormones Tracked**

**Primary Hormones (assessed via questionnaire):**

1. **Estrogen** \- Can be HIGH or LOW

   * High: Heavy periods, bloating, breast tenderness

   * Low: Light periods, hot flashes, vaginal dryness

2. **Progesterone** \- Typically assessed as LOW

   * Mood swings, anxiety, PMS, short luteal phase

3. **Androgens (Testosterone)** \- Typically assessed as HIGH

   * Hirsutism, acne, male-pattern hair loss, PCOS

4. **Insulin** \- Typically assessed as HIGH

   * Weight gain (especially abdominal), sugar cravings, difficulty losing weight

5. **Cortisol** \- Can be HIGH or LOW

   * High: Chronic stress, anxiety, sleep issues, salt/sugar cravings

   * Low: Extreme fatigue, low blood pressure, salt cravings

6. **Thyroid** \- Typically assessed as LOW (hypothyroidism)

   * Fatigue, weight gain, cold intolerance, hair thinning, constipation

**1.2 Assessment Goals**

**Primary Objective:** Identify which hormone(s) are most likely imbalanced based on:

* Reported symptoms

* Diagnosed conditions

* Menstrual cycle patterns

* Optional: Lab test results

**Secondary Objective:** Provide confidence level indicating assessment reliability:

* **HIGH (Score 6+):** Strong data quality, clear patterns, lab confirmation

* **MEDIUM (Score 3-5):** Adequate data, some missing elements

* **LOW (Score 0-2):** Limited data, conflicts, heavy LLM reliance

**1.3 Clinical Standards Referenced**

* **PCOS:** Rotterdam Criteria (2 of 3: irregular ovulation, hyperandrogenism, polycystic ovaries)

* **Thyroid:** TSH \>2.5 mIU/L suggests subclinical hypothyroidism (Endocrine Society)

* **PMDD:** DSM-5 criteria for premenstrual dysphoric disorder

* **Insulin Resistance:** Fasting insulin \>6 µIU/mL or HbA1c \>5.4%

* **Validated PCOS Questionnaires:** Ferriman-Gallwey scoring for hirsutism (sensitivity 76%, specificity 70%)

---

**SECTION 2: QUESTIONNAIRE STRUCTURE & SCORING LOGIC**

**2.1 Question 1: Basic Information**  
 **Fields:** Name, Age

**Backend Processing:**

* Store for personalization

* Validate age range (18-40)

* NO hormone scoring impact

---

**2.2 Question 2: Period Pattern**

**Question Display:** "How would you describe your periods?"

**Options and Hormone Impact:**

**Option 1: Regular**

* Hormone Impact: NONE (baseline)

* Score Weight: \+0 to all hormones

* Clinical Note: Suggests balanced hormonal function

**Option 2: Irregular**

* Hormone Impact:

  * Androgens: \+2

  * Thyroid: \+1

  * Cortisol: \+1

* Clinical Rationale: Common in PCOS (androgen excess), hypothyroidism, or chronic stress affecting HPA axis

**Option 3: Occasional Skips**

* Hormone Impact:

  * Androgens: \+1

  * Cortisol: \+1

  * Progesterone: \+1

* Clinical Rationale: Suggests intermittent ovulation disruption, often stress-related or early PCOS

**Option 4: I don't get periods (Amenorrhea)**

* Hormone Impact:

  * Androgens: \+2

  * Estrogen LOW: \+1

  * Thyroid: \+2

* Clinical Rationale: High-severity flag for hypothalamic amenorrhea, PCOS, premature ovarian insufficiency (POI), or severe hypothyroidism

* Additional Flag: "High clinical concern \- recommend medical evaluation"

---

**2.3 Question 2B: Birth Control Usage**

**Sub-Question:** "Also let me know if you use..."

**Options and Modifiers:**

**Option 1: Hormonal Birth Control Pills**

* Modifier: Reduce ALL hormone scores by 30%

* Confidence Impact: \-1

* Rationale: Synthetic hormones suppress natural cycle, masking underlying patterns

**Option 2: IUD (Intrauterine Device)**

* If Hormonal IUD: Reduce all scores by 20%

* If Copper IUD: No modifier

* Confidence Impact: \-1 (if hormonal)

**Option 3: None**

* Modifier: No adjustment

* Confidence Impact: \+1 (natural cycle allows accurate assessment)

---

**2.4 Question 3: Cycle Details**

**Part A: When did your last period start?**

* Input: Date picker (MM/DD/YYYY)

* Option: "I'm not sure"

**Part B: What is your average cycle length?**

* Options:

  * Less than 21 days

  * 21-25 days

  * 26-30 days (optimal range)

  * 31-35 days

  * 35+ days

  * I'm not sure

**Cycle Length Hormone Scoring:**

**Less than 21 days:**

* Estrogen HIGH: \+1

* Progesterone LOW: \+1

* Rationale: Short luteal phase indicates progesterone deficiency

**21-30 days:**

* No adjustments (normal range)

**31-35 days:**

* Androgens: \+1

* Thyroid: \+1

* Rationale: Could indicate PCOS or subclinical hypothyroidism

**35+ days:**

* Androgens: \+2

* Insulin: \+1

* Thyroid: \+1

* Rationale: High likelihood of PCOS or hypothyroidism; cycles \>35 days are abnormal

**Cycle Phase Calculation (if date provided):**

Days Since Period \= Today's Date \- Last Period Date

Phase Assignment:  
\- Days 1-7: Menstrual/Early Follicular  
\- Days 8-14: Late Follicular/Ovulation Window  
\- Days 15 to (Cycle Length \- 3): Luteal  
\- Last 3 days of cycle: Late Luteal/PMS Window

**Confidence Impact:**

* Date provided: \+1

* "I'm not sure" selected: \-2

---

**2.5 Question 4: Health Concerns (Multi-Select)**

This is the core symptom mapping section. Users select multiple symptoms across four categories.

**CATEGORY A: PERIOD CONCERNS**

**Symptom: Irregular Periods**

* Androgens: \+2

* Thyroid: \+1

* Cortisol: \+1

* Rationale: Most commonly PCOS, but also thyroid dysfunction or chronic stress

**Symptom: Painful Periods**

* Estrogen HIGH: \+1

* Progesterone LOW: \+2

* Rationale: Estrogen dominance or progesterone deficiency causing increased prostaglandins

**Symptom: Light Periods / Spotting**

* Estrogen LOW: \+2

* Progesterone LOW: \+1

* Thyroid: \+1

* Rationale: Hypoestrogenism, hypothalamic amenorrhea, or thyroid issues

**Symptom: Heavy Periods**

* Estrogen HIGH: \+2

* Progesterone LOW: \+1

* Rationale: Estrogen dominance without progesterone balance; may indicate fibroids

---

**CATEGORY B: BODY CONCERNS**

**Symptom: Bloating**

* Estrogen HIGH: \+2

* Cortisol: \+1

* Rationale: Estrogen causes water retention; cortisol affects aldosterone

**Symptom: Hot Flashes**

* Estrogen LOW: \+3

* Thyroid: \+1

* Flag: "HIGH URGENCY \- If under 40, possible premature ovarian insufficiency"

* Rationale: Hot flashes in reproductive-age women indicate severe estrogen deficiency

**Symptom: Nausea**

* Estrogen HIGH: \+1

* Rationale: Estrogen spikes can cause GI sensitivity (mild indicator)

**Symptom: Difficulty Losing Weight / Stubborn Belly Fat**

* Insulin: \+2

* Cortisol: \+2

* Thyroid: \+2

* Rationale: Triple threat \- insulin resistance, high cortisol, or hypothyroidism all cause weight retention

**Symptom: Recent Weight Gain**

* Thyroid: \+2

* Cortisol: \+1

* Insulin: \+1

* Rationale: Hypothyroidism is primary suspect; cortisol and insulin as secondary

**Symptom: Menstrual Headaches**

* Estrogen LOW: \+1

* Progesterone: \+1

* Rationale: Estrogen withdrawal headaches common in luteal phase

---

**CATEGORY C: SKIN AND HAIR CONCERNS**

**Symptom: Hirsutism (hair growth on chin, nipples, etc.)**

* Androgens: \+3

* Flag: "VERY HIGH severity indicator"

* Rationale: Direct clinical marker of androgen excess; sensitivity 76% for PCOS (Bedrick et al., 2020\)

**Symptom: Thinning of Hair**

* Thyroid: \+2

* Androgens: \+1

* Cortisol: \+1

* Rationale: Hypothyroidism most common cause; high androgens also cause male-pattern hair loss

**Symptom: Adult Acne**

* Androgens: \+2

* Insulin: \+1

* Rationale: Androgen-driven sebum production; insulin exacerbates

---

**CATEGORY D: MENTAL HEALTH CONCERNS**

**Symptom: Mood Swings**

* Progesterone LOW: \+2

* Cortisol: \+1

* Estrogen fluctuation: \+1

* Rationale: Progesterone is mood-stabilizing; deficiency causes emotional lability

**Symptom: Stress**

* Cortisol HIGH: \+2

* Progesterone: \-1 (suppressed by cortisol)

* Rationale: Chronic stress elevates cortisol, which suppresses progesterone production

**Symptom: Fatigue**

* Thyroid: \+2

* Cortisol: \+2 (if chronic) or \-2 (if adrenal fatigue)

* Insulin: \+1

* Rationale: Most commonly hypothyroidism; also HPA axis dysfunction or insulin resistance

---

**2.6 Question 5: Top Concern Selection**

**Display:** User selects their \#1 concern from previously chosen symptoms

**Backend Logic:**

* Apply **1.5x multiplier** to ALL hormone scores associated with that symptom

* Example: If "Hirsutism" is top concern:

  * Base: Androgens \+3

  * With multiplier: Androgens \+4.5 (round to \+5)

**Confidence Impact:** \+1 (clear priority helps refine diagnosis)

---

**2.7 Question 6: Diagnosed Conditions**

**Question Display:** "Is there any diagnosed health condition that I should know about?"

**Options:**

**CONDITION 1: PCOS (Polycystic Ovary Syndrome)**

**If PCOS \+ Matching Symptoms Present:**  
 (Symptoms: Irregular periods, hirsutism, acne, weight gain, difficulty losing weight)

* Androgens: \+3

* Insulin: \+3

* Confidence: \+1

**If PCOS \+ NO Matching Symptoms:**  
 (Flag as possible Lean PCOS or Adrenal PCOS)

* Androgens: \+1

* Insulin: \+1

* Cortisol: \+1

* Note: "Possible lean/adrenal PCOS phenotype"

**Lab Integration (if available):**

* LH:FSH ratio \>2.5 → Androgens \+2

* DHEA-S \>300 µg/dL → Androgens \+2 (adrenal source)

* Free Testosterone \>2.0 pg/mL → Androgens \+2

---

**CONDITION 2: PCOD (Polycystic Ovarian Disease)**

(Note: Often used interchangeably with PCOS; may indicate milder presentation)

* Androgens: \+2

* Insulin: \+2

---

**CONDITION 3: Endometriosis**

**If Endo \+ Severe Symptoms:**  
 (Painful cramps, heavy bleeding, GI distress, bloating, fatigue)

* Estrogen HIGH: \+3

* Inflammation marker: \+2

* Confidence: \+1

**If Endo \+ Mild Symptoms:**

* Estrogen HIGH: \+1

**Cycle Phase Modifier:**

* If cramps occur in FOLLICULAR phase (not during period): \+1 to Estrogen (abnormal timing)

---

**CONDITION 4: Dysmenorrhea (Painful Periods)**

* Estrogen HIGH: \+1

* Progesterone LOW: \+2

* Note: Consider secondary causes like endometriosis

---

**CONDITION 5: Amenorrhea (Absence of Periods)**

* Estrogen LOW: \+3

* Androgens: \+2

* Thyroid: \+2

* Flag: "HIGH clinical concern \- possible hypothalamic, PCOS, or POI"

---

**CONDITION 6: Menorrhagia (Heavy/Prolonged Bleeding)**

* Estrogen HIGH: \+3

* Progesterone LOW: \+1

* Note: Check for fibroids or clotting disorders

---

**CONDITION 7: Metrorrhagia (Irregular Bleeding)**

* Estrogen fluctuation: \+2

* Progesterone LOW: \+2

* Flag: "May require structural evaluation"

---

**CONDITION 8: Premenstrual Syndrome (PMS)**

* Progesterone LOW: \+1

* Estrogen fluctuation: \+1

---

**CONDITION 9: PMDD (Premenstrual Dysphoric Disorder)**

**If PMDD \+ Severe Mood Symptoms:**  
 (Rage, depression, suicidal ideation, intense irritability in 5-10 days before period)

* Progesterone Sensitivity: \+3

* Cortisol: \+2

* Note: "This reflects GABA receptor sensitivity to progesterone metabolites, not always low progesterone"

**If PMDD \+ Moderate Symptoms:**

* Progesterone: \+2

* Cortisol: \+1

**Lab Note:**  
 If progesterone levels are normal in luteal phase but symptoms severe, flag as "neuro-sensitivity rather than hormonal deficit"

---

**CONDITION 10: Hashimoto's or Hypothyroidism**

**If Thyroid Condition \+ Matching Symptoms:**  
 (Fatigue, hair thinning, weight gain, cold intolerance, constipation)

* Thyroid: \+3

* Confidence: \+1

**If Diagnosed but Few Symptoms:**

* Thyroid: \+1

* Note: "May be well-managed on medication"

**Lab Integration:**

* TSH \>2.5 mIU/L → Thyroid \+2 (subclinical hypothyroidism per Endocrine Society)

* TSH \>4.5 mIU/L → Thyroid \+3 (definite hypothyroidism)

* Free T3 \<2.5 pg/mL → Thyroid \+2

* If symptoms present but TSH normal → Thyroid \+1 (possible tissue-level resistance)

---

**CONDITION 11: Others (Free Text Input)**

**Challenge:** User can enter any condition not in the predefined list

**Solution:** LLM Integration via Gemini API

**See Section 3 for complete LLM implementation details**

---

**SECTION 3: LLM INTEGRATION FOR "OTHERS" INPUT**

**3.1 Use Case**

When a user enters a custom condition or symptom in the "Others" field, the system must:

1. Understand the medical context

2. Map it to relevant hormone imbalances

3. Assign appropriate scoring weights

4. Maintain consistency with established heuristics

**3.2 System Prompt for Gemini API**

**Prompt Structure:**

SYSTEM ROLE: Clinical Hormone Scoring Assistant

CONTEXT:  
You are part of a women's hormone health assessment system for ages 18-40.   
Your role is to analyze user-reported conditions or symptoms that aren't in our   
predefined list and map them to hormone scoring following our established heuristics.

HORMONES WE TRACK:  
1\. Estrogen (can be HIGH or LOW)  
2\. Progesterone (typically LOW)  
3\. Androgens/Testosterone (typically HIGH)  
4\. Insulin (typically HIGH)  
5\. Cortisol (can be HIGH or LOW)  
6\. Thyroid (typically LOW)

SCORING SCALE:  
\+3 \= Very strong association (direct clinical marker)  
\+2 \= Strong association (common indicator)  
\+1 \= Moderate association (contributing factor)  
0 \= No clear association

HEURISTIC RULES YOU MUST FOLLOW:

1\. PCOS-Related Symptoms:  
   Irregular periods, hirsutism, acne → Androgens \+2 to \+3, Insulin \+2

2\. Thyroid-Related Symptoms:  
   Fatigue, weight gain, hair loss, cold sensitivity → Thyroid \+2 to \+3

3\. Estrogen Dominance Symptoms:  
   Heavy periods, bloating, breast tenderness → Estrogen HIGH \+2, Progesterone LOW \+1

4\. Low Estrogen Symptoms:  
   Light periods, hot flashes (under 40), vaginal dryness → Estrogen LOW \+2 to \+3

5\. Progesterone Deficiency:  
   Mood swings, anxiety, short cycles, PMS → Progesterone LOW \+2

6\. Insulin Resistance:  
   Weight gain (especially abdominal), sugar cravings, difficulty losing weight → Insulin \+2

7\. High Cortisol:  
   Chronic stress, anxiety, sleep issues, sugar/salt cravings → Cortisol HIGH \+2

8\. Low Cortisol:  
   Extreme fatigue, low blood pressure, salt cravings → Cortisol LOW \+2

9\. Androgen Excess:  
   Facial hair, acne, male-pattern hair loss → Androgens \+2 to \+3

TASK:  
Analyze the user's "other" input and return a JSON response with:  
1\. Hormone impacts and score weights  
2\. Clinical reasoning  
3\. Confidence level in your assessment  
4\. Any flags or concerns

REQUIRED JSON FORMAT (STRICT):  
{  
  "hormone\_impacts": \[  
    {  
      "hormone": "androgens",  
      "direction": "high",  
      "score\_weight": 2,  
      "reasoning": "Clinical explanation here"  
    }  
  \],  
  "overall\_confidence": "high|medium|low",  
  "clinical\_flags": \["any concerns or recommendations"\],  
  "needs\_medical\_review": true|false  
}

CRITICAL GUIDELINES:  
\- Be conservative with scoring if input is vague  
\- If condition is serious or unclear, set "needs\_medical\_review": true  
\- Always provide clinical reasoning  
\- Consider hormone interactions (e.g., high cortisol suppresses progesterone)  
\- If input seems unrelated to hormones, return empty hormone\_impacts and low confidence  
\- Only use hormone names: estrogen, progesterone, androgens, insulin, cortisol, thyroid  
\- Only use directions: high, low  
\- Score weights must be 0, 1, 2, or 3

**3.3 API Call Structure**

**Request to Gemini:**

User Input: \[Free text from "Others" field\]

Additional Context:  
\- Age: \[user age\]  
\- Selected symptoms: \[comma-separated list\]  
\- Diagnosed conditions: \[if any already selected\]  
\- Current cycle phase: \[if calculable\]

Analyze this input according to the hormone scoring heuristics provided   
in the system prompt and return structured JSON.

**3.4 Response Validation (Pydantic Schema)**

**Python Models:**

from pydantic import BaseModel, Field  
from typing import List, Literal

class HormoneImpact(BaseModel):  
    hormone: Literal\["estrogen", "progesterone", "androgens",   
                     "insulin", "cortisol", "thyroid"\]  
    direction: Literal\["high", "low"\]  
    score\_weight: int \= Field(ge=0, le=3)  
    reasoning: str

class LLMScoringResponse(BaseModel):  
    hormone\_impacts: List\[HormoneImpact\]  
    overall\_confidence: Literal\["high", "medium", "low"\]  
    clinical\_flags: List\[str\] \= \[\]  
    needs\_medical\_review: bool

**Validation Benefits:**

* Ensures only valid hormone names

* Restricts scores to 0-3 range

* Guarantees required fields present

* Type-safe integration with backend

**3.5 Integration Workflow**

**Step-by-Step Process:**

1. Receive "Others" input from mobile app

2. Construct Gemini API request with system prompt \+ user context

3. Send request to Gemini API

4. Receive JSON response

5. Validate response using Pydantic models

6. If validation passes:

   * Apply hormone scores to aggregation object

   * Add LLM confidence penalty to overall confidence:

     * LLM "high" confidence: \+0

     * LLM "medium" confidence: \-1

     * LLM "low" confidence: \-2

7. If `needs_medical_review: true`:

   * Add flag: "This condition requires professional medical evaluation"

8. If validation fails or API error:

   * Log error for manual review

   * Apply generic \+1 to most common hormones based on keyword matching

   * Set confidence to "low"

   * Flag: "Unable to fully process custom input \- please consult healthcare provider"

**3.6 Example LLM Responses**

**Example 1: Clear Input**

User Input: "Endometriosis"

{  
  "hormone\_impacts": \[  
    {  
      "hormone": "estrogen",  
      "direction": "high",  
      "score\_weight": 3,  
      "reasoning": "Endometriosis is driven by estrogen excess and inflammatory processes"  
    }  
  \],  
  "overall\_confidence": "high",  
  "clinical\_flags": \["Consider pelvic ultrasound or laparoscopy for confirmation"\],  
  "needs\_medical\_review": true  
}

**Example 2: Vague Input**

User Input: "Hair loss"

{  
  "hormone\_impacts": \[  
    {  
      "hormone": "thyroid",  
      "direction": "low",  
      "score\_weight": 2,  
      "reasoning": "Hair thinning is most commonly associated with hypothyroidism"  
    },  
    {  
      "hormone": "androgens",  
      "direction": "high",  
      "score\_weight": 1,  
      "reasoning": "High androgens can cause male-pattern hair loss in women"  
    }  
  \],  
  "overall\_confidence": "medium",  
  "clinical\_flags": \["Recommend TSH and free testosterone testing"\],  
  "needs\_medical\_review": false  
}

**Example 3: Unrelated Input**

User Input: "Broken arm last year"

{  
  "hormone\_impacts": \[\],  
  "overall\_confidence": "low",  
  "clinical\_flags": \["Input does not appear related to hormonal health"\],  
  "needs\_medical\_review": false  
}

---

**SECTION 4: CYCLE PHASE CONTEXT & NORMALIZATION**

**4.1 Why Cycle Phase Matters**

Certain symptoms are **normal and expected** in specific cycle phases. These should NOT heavily weight hormone imbalance scoring.

**4.2 Phase-Normal Symptoms (Reduce Score by 50%)**

**Late Luteal Phase (Days 25-28 of cycle):**  
 Normal Symptoms:

* Bloating → Reduce Estrogen HIGH score by 50%

* Breast tenderness → Reduce Estrogen HIGH score by 50%

* Mood swings → Reduce Progesterone LOW score by 50%

* Sugar/chocolate cravings → Reduce Insulin score by 50%

Rationale: These are expected PMS symptoms due to normal hormone fluctuations

**Menstrual Phase (Days 1-5):**  
 Normal Symptoms:

* Cramps → Reduce Estrogen/Progesterone scores by 50%

* Fatigue → Reduce Thyroid/Cortisol scores by 50%

* Mild mood dips → Reduce Progesterone score by 50%

Rationale: Expected during hormone withdrawal at period start

**4.3 Abnormal Symptom Timing (INCREASE Score)**

**Cramps During Follicular Phase (Days 6-14):**

* Add \+1 to Estrogen HIGH

* Flag: "Possible endometriosis \- cramps outside of menstruation are abnormal"

**Heavy Bleeding Lasting \>7 Days:**

* Add \+1 to Estrogen HIGH

* Flag: "May indicate fibroids, adenomyosis, or clotting issues"

**Mid-Cycle Bleeding (Between Periods):**

* Add \+1 to Estrogen fluctuation

* Flag: "Possible metrorrhagia or ovulation bleeding \- recommend evaluation"

**4.4 Implementation Logic**

IF cycle\_phase \== "late\_luteal" AND symptom IN \["bloating", "breast\_tenderness", "mood\_swings"\]:  
    current\_hormone\_score \*= 0.5

IF cycle\_phase \== "follicular" AND symptom \== "cramps":  
    estrogen\_high \+= 1  
    flags.append("Cramps in follicular phase suggest endometriosis")

---

**SECTION 5: HORMONE SCORE AGGREGATION**

**5.1 Tracking Structure**

For each hormone, maintain three score sources:

hormone\_scores \= {  
    "androgens": {  
        "from\_symptoms": 0,  
        "from\_diagnosis": 0,  
        "from\_labs": 0,  
        "total": 0,  
        "direction": "high"  
    },  
    "estrogen": {  
        "from\_symptoms": 0,  
        "from\_diagnosis": 0,  
        "from\_labs": 0,  
        "total": 0,  
        "direction": "high"  \# or "low"  
    },  
    \# ... repeat for all 6 hormones  
}

**5.2 Score Calculation Steps**

**Step 1: Symptom Scoring**

* For each selected symptom, add weight to associated hormone

* Example: "Hirsutism" selected → androgens.from\_symptoms \+= 3

**Step 2: Diagnosis Scoring**

* For each diagnosed condition, add weight per Section 2.7 rules

* Example: PCOS with symptoms → androgens.from\_diagnosis \+= 3, insulin.from\_diagnosis \+= 3

**Step 3: Cycle Phase Adjustment**

* Apply 50% reduction for phase-normal symptoms

* Apply \+1 bonus for abnormally timed symptoms

**Step 4: Top Concern Multiplier**

* Apply 1.5x multiplier to all hormones associated with top concern

* Round to nearest integer

**Step 5: Birth Control Modifier**

* If on hormonal BC, multiply all scores by 0.7 (30% reduction)

**Step 6: Lab Overlay (if provided)**

* Add lab-based scores per Section 6

**Step 7: Calculate Totals**

for hormone in hormone\_scores:  
    hormone\_scores\[hormone\]\["total"\] \= (  
        hormone\_scores\[hormone\]\["from\_symptoms"\] \+  
        hormone\_scores\[hormone\]\["from\_diagnosis"\] \+  
        hormone\_scores\[hormone\]\["from\_labs"\]  
    )

**5.3 Identifying Primary & Secondary Imbalances**

**Algorithm:**

1. Sort hormones by total score (descending)

2. **Primary Imbalance:** Hormone with highest total score

3. **Secondary Imbalances:** Next 1-2 hormones with scores ≥50% of primary score

**Tie-Breaking Priority (if equal scores):**  
 Androgens \> Thyroid \> Insulin \> Estrogen \> Cortisol \> Progesterone

**Example:**

Androgens: 10 (PRIMARY)  
Insulin: 6 (SECONDARY \- 60% of primary)  
Progesterone: 5 (SECONDARY \- 50% of primary)  
Thyroid: 2 (below 50% threshold \- not included)

---

**SECTION 6: LAB REPORT INTEGRATION**

**6.1 Lab Tests Tracked**

**Complete Lab Panel:**

| Lab Test | Normal Range | Threshold for Scoring | Hormone Impact |
| ----- | ----- | ----- | ----- |
| **Total Testosterone** | \<50 ng/dL | \>60 ng/dL | Androgens \+2 |
| **Free Testosterone** | \<2.0 pg/mL | \>2.0 pg/mL | Androgens \+2 |
| **DHEA-S** | 35-430 µg/dL | \>300 µg/dL | Androgens \+2 (adrenal) |
| **LH** | 2-20 mIU/mL | Used for ratio | \- |
| **FSH** | 2-10 mIU/mL | Used for ratio | \- |
| **LH:FSH Ratio** | \<2:1 | \>2.5:1 | Androgens \+2 (PCOS) |
| **TSH** | 0.4-4.5 mIU/L | \>2.5 mIU/L | Thyroid \+2 (subclinical) |
| **TSH** | \- | \>4.5 mIU/L | Thyroid \+3 (overt) |
| **Free T3** | 2.3-4.2 pg/mL | \<2.5 pg/mL | Thyroid \+2 |
| **Free T4** | 0.8-1.8 ng/dL | \<1.0 ng/dL | Thyroid \+1 |
| **Fasting Insulin** | 2-20 µIU/mL | \>6 µIU/mL | Insulin \+2 |
| **HbA1c** | \<5.7% | \>5.4% | Insulin \+2 (prediabetic) |
| **Fasting Glucose** | 70-99 mg/dL | \>100 mg/dL | Insulin \+1 |
| **AM Cortisol** | 6-23 µg/dL | \>20 or \<6 µg/dL | Cortisol \+2 |
| **Estradiol (E2)** | Day 3: 30-100 pg/mL | \<30 or \>100 pg/mL | Estrogen ±2 |
| **Progesterone** | Luteal: \>10 ng/mL | \<5 ng/mL (luteal) | Progesterone \+2 |
| **SHBG** | 20-100 nmol/L | \<30 or \>100 nmol/L | Modifier (see 6.2) |

**6.2 SHBG as Modifier**

**SHBG (Sex Hormone Binding Globulin):**

**Low SHBG (\<30 nmol/L):**

* Increases free androgen levels

* Modify: Androgens \+1 (even if total testosterone normal)

* Often seen with insulin resistance

**High SHBG (\>100 nmol/L):**

* Decreases free androgen levels

* Modify: Androgens \-1 (may reduce androgen symptoms)

* Can mask PCOS

**6.3 Lab-Symptom Concordance**

**High Concordance (Labs Align with Symptoms):**

* Example: User reports hirsutism \+ acne, labs show Free T \>2.0 pg/mL

* Action: Add \+2 to confidence score

* Strengthen clinical explanation: "Your symptoms of \[X\] are confirmed by elevated \[lab name\]"

**Low Concordance (Labs Contradict Symptoms):**

* Example: User reports severe fatigue \+ weight gain, but TSH \= 1.5 (normal)

* Action: Subtract \-2 from confidence score

* Add conflict: "Your symptoms suggest thyroid issues, but labs are within normal range. This may indicate:

  * Tissue-level thyroid resistance

  * Other causes of fatigue (iron deficiency, sleep apnea)

  * Need for additional testing (Free T3, thyroid antibodies)"

**6.4 Cycle Phase Considerations for Labs**

**Estradiol (E2):**

* Should be tested on Day 3-5 of cycle

* If tested at wrong time, flag: "Estradiol timing unclear \- retest on Day 3-5 for accurate assessment"

**Progesterone:**

* Should be tested on Day 19-22 of 28-day cycle (mid-luteal)

* If \<5 ng/mL in luteal phase → definite deficiency

* If tested at wrong time, results invalid

**6.5 Lab Overlay Workflow**

**Step 1:** User uploads lab report (PDF or manual entry)

**Step 2:** Extract lab values (OCR or structured input form)

**Step 3:** Validate each value against normal ranges

**Step 4:** Apply scoring rules from Table 6.1

**Step 5:** Check symptom-lab concordance:

if symptom\_indicates\_hypothyroid AND TSH \> 2.5:  
    concordance \= "high"  
    confidence \+= 2  
elif symptom\_indicates\_hypothyroid AND TSH \<= 2.5:  
    concordance \= "low"  
    confidence \-= 2  
    conflicts.append("Thyroid symptoms present but TSH normal")

**Step 6:** Recalculate primary/secondary imbalances with lab data included

**Step 7:** Flag any critical values requiring immediate medical attention:

* TSH \>10 mIU/L

* Free Testosterone \>5 pg/mL

* HbA1c \>6.5% (diabetes range)

* Fasting glucose \>126 mg/dL

---

**SECTION 7: CONFIDENCE SCORE CALCULATION**

**7.1 Confidence Score Components**

**Base Score:** 0

**Add Points (+) For:**

| Factor | Points | Criteria |
| ----- | ----- | ----- |
| Regular cycles reported | \+2 | Predictable hormone patterns |
| Exact last period date provided | \+1 | Enables accurate phase calculation |
| Diagnosed condition selected | \+1 | Clinical anchor point |
| Top concern selected | \+1 | Clear priority direction |
| 3+ symptoms in same hormone cluster | \+1 | Strong convergence signal |
| Lab results uploaded | \+2 | Objective data available |
| Labs align with symptoms | \+2 | High concordance |
| Birth control \= None | \+1 | Natural cycle observable |

**Subtract Points (-) For:**

| Factor | Points | Criteria |
| ----- | ----- | ----- |
| Irregular cycles | \-1 | Harder to phase-map |
| "I'm not sure" for cycle date | \-2 | Cannot calculate phase |
| On hormonal birth control | \-1 | Masked natural patterns |
| Conflicting symptoms detected | \-2 | E.g., high AND low estrogen signals |
| Only diagnosis, no symptoms | \-1 | Possible misdiagnosis or well-controlled |
| LLM-scored "Others" with low confidence | \-2 | Uncertain mapping |
| No labs despite high severity symptoms | \-1 | Missing objective validation |
| Labs contradict symptoms | \-2 | Discordance reduces reliability |

**7.2 Confidence Level Thresholds**

| Total Score | Confidence Level | Interpretation |
| ----- | ----- | ----- |
| **6+** | **HIGH** | Strong data quality, clear hormone patterns, minimal conflicts, lab confirmation available |
| **3-5** | **MEDIUM** | Adequate data with some uncertainty or missing pieces; generally reliable but could benefit from labs |
| **0-2** | **LOW** | Insufficient data, conflicting signals, heavy reliance on LLM, or significant missing information |

**7.3 Confidence Score Display**

**Example Output:**

{  
  "confidence": {  
    "level": "medium",  
    "score": 4,  
    "factors": \[  
      "Regular cycle data provided (+2)",  
      "PCOS diagnosis selected (+1)",  
      "Top concern identified (+1)",  
      "3+ androgen-related symptoms (+1)",  
      "On birth control (-1)",  
      "No lab results available (-1)"  
    \],  
    "recommendation": "Your assessment is moderately reliable. Consider uploading lab results (testosterone, insulin, TSH) for a more precise analysis."  
  }  
}

---

**SECTION 8: CONFLICT DETECTION**

**8.1 Types of Conflicts**

**Conflict Type 1: Hormone Direction Conflicts**

Example: Symptoms suggest BOTH high estrogen (bloating, heavy periods) AND low estrogen (light periods, hot flashes)

Action:

* Flag conflict: "Conflicting estrogen signals detected"

* Recommendation: "Test estradiol on Day 3 of cycle to clarify"

* Impact: \-2 confidence

**Conflict Type 2: Symptom-Diagnosis Mismatch**

Example: PCOS diagnosed but NO androgen symptoms present

Action:

* Flag: "Diagnosis does not align with reported symptoms"

* Note: "You may have lean PCOS (non-hyperandrogenic phenotype) or PCOS may be well-controlled"

* Impact: \-1 confidence

**Conflict Type 3: Lab-Symptom Mismatch**

Example: Severe fatigue \+ hair loss but TSH \= 1.0 (normal)

Action:

* Flag: "Thyroid symptoms present but TSH normal"

* Recommendation: "Consider testing Free T3, thyroid antibodies, or other causes (iron, vitamin D, sleep apnea)"

* Impact: \-2 confidence

**Conflict Type 4: Birth Control Masking**

Example: On hormonal birth control but reporting severe PCOS symptoms

Action:

* Note: "Birth control may be suppressing some symptoms. Consider assessment off birth control for 3+ months if medically appropriate"

* Impact: \-1 confidence

**8.2 Conflict Resolution Strategy**

**Backend Logic:**

conflicts \= \[\]

\# Check for estrogen direction conflict  
if estrogen\_high\_score \> 0 AND estrogen\_low\_score \> 0:  
    conflicts.append({  
        "type": "hormone\_direction",  
        "hormone": "estrogen",  
        "description": "Symptoms suggest both high and low estrogen",  
        "recommendation": "Test estradiol on Day 3 of cycle",  
        "severity": "moderate"  
    })

\# Check for diagnosis-symptom mismatch  
if "PCOS" in diagnoses AND androgens\_from\_symptoms \== 0:  
    conflicts.append({  
        "type": "diagnosis\_mismatch",  
        "description": "PCOS diagnosed but no androgen symptoms reported",  
        "recommendation": "You may have lean PCOS phenotype",  
        "severity": "low"  
    })

\# Check for lab-symptom discordance  
if thyroid\_symptoms\_present AND TSH \< 2.5:  
    conflicts.append({  
        "type": "lab\_symptom\_mismatch",  
        "description": "Thyroid symptoms present but TSH normal",  
        "recommendation": "Consider Free T3, thyroid antibodies, or other causes",  
        "severity": "moderate"  
    })

---

**SECTION 9: CLINICAL EXPLANATIONS GENERATOR**

**9.1 Purpose**

Provide user-friendly, evidence-based explanations for each flagged hormone imbalance.

**9.2 Explanation Template**

**For each Primary/Secondary Hormone:**

\[HORMONE NAME\] appears \[DIRECTION\] based on:

SUPPORTING EVIDENCE:  
\- \[Symptom 1\], \[Symptom 2\] (common signs of \[hormone\] imbalance)  
\- \[Diagnosis\] (often associated with \[hormone\] \[direction\])  
\[If labs present:\]  
\- Your \[lab name\] level of \[value\] is \[above/below\] optimal range

WHAT THIS MIGHT MEAN:  
\[Clinical context paragraph explaining physiological mechanism\]

WHAT YOU CAN DO:  
\[Lifestyle recommendations\]  
\[Testing recommendations\]  
\[Supplement suggestions\]

**9.3 Example Explanations**

**Example 1: Androgens (High)**

TESTOSTERONE appears ELEVATED based on:

SUPPORTING EVIDENCE:  
\- Hirsutism and adult acne (common signs of androgen excess)  
\- PCOS diagnosis (often associated with high androgens)  
\- Your free testosterone level of 2.5 pg/mL is above optimal range (\<2.0)

WHAT THIS MIGHT MEAN:  
Elevated androgens (testosterone, DHEA-S) can cause unwanted hair growth,   
acne, and irregular periods. In PCOS, this is often driven by insulin   
resistance affecting the ovaries and adrenal glands. High insulin stimulates   
ovarian testosterone production, creating a cycle that worsens both conditions.

WHAT YOU CAN DO:  
Testing Recommendations:  
\- Fasting insulin and HbA1c (check for insulin resistance)  
\- DHEA-S (determine if adrenal glands are contributing)

Lifestyle Strategies:  
\- Focus on blood sugar balance through low-glycemic foods (avoid refined carbs)  
\- Strength training improves insulin sensitivity  
\- Adequate protein at each meal helps stabilize blood sugar

Supplement Considerations:  
\- Inositol (myo \+ d-chiro 40:1 ratio) may help regulate androgens  
\- Spearmint tea (2 cups daily) shown to reduce free testosterone  
\- Zinc supports healthy testosterone metabolism

---

**Example 2: Thyroid (Low)**

THYROID FUNCTION appears LOW based on:

SUPPORTING EVIDENCE:  
\- Fatigue, hair thinning, and recent weight gain (classic hypothyroid symptoms)  
\- Hashimoto's diagnosis (autoimmune thyroid disease)  
\- Your TSH level of 3.8 mIU/L suggests subclinical hypothyroidism

WHAT THIS MIGHT MEAN:  
Your TSH is in the "normal" range (0.4-4.5) but above the optimal range   
for many women (\<2.5). Even mild thyroid hormone deficiency can cause   
significant symptoms. In Hashimoto's, the immune system attacks the thyroid,   
gradually reducing its ability to produce thyroid hormones (T3 and T4).   
Research shows TSH \>2.5 is associated with higher cardiovascular risk and   
progression to overt hypothyroidism.

WHAT YOU CAN DO:  
Testing Recommendations:  
\- Free T3 (most active thyroid hormone \- should be in upper half of range)  
\- Thyroid antibodies (TPO, TG \- confirm Hashimoto's)  
\- Retest TSH in 3 months to track progression

Lifestyle Strategies:  
\- Ensure adequate iodine (but don't over-supplement if Hashimoto's present)  
\- Selenium (200 mcg daily) shown to reduce thyroid antibodies  
\- Address gut health (70% of thyroid hormone conversion happens in gut)  
\- Manage stress (cortisol inhibits thyroid hormone conversion)

Medical Considerations:  
\- Discuss levothyroxine with your doctor if TSH continues rising or symptoms worsen  
\- Optimal treatment target: TSH 0.5-2.0 mIU/L for symptom relief

---

**Example 3: Progesterone (Low)**

PROGESTERONE appears LOW based on:

SUPPORTING EVIDENCE:  
\- Mood swings and irritability in the week before your period  
\- Painful periods  
\- PMDD diagnosis

WHAT THIS MIGHT MEAN:  
Progesterone is produced after ovulation in the second half of your cycle   
(luteal phase). It has calming, mood-stabilizing effects by influencing   
GABA receptors in the brain. Low progesterone can cause PMS, anxiety,   
insomnia, and heavier periods (since estrogen goes "unopposed"). This can   
result from stress (cortisol suppresses progesterone), anovulatory cycles,   
or luteal phase defects.

WHAT YOU CAN DO:  
Testing Recommendations:  
\- Progesterone blood test on Day 19-22 of your cycle (should be \>10 ng/mL)  
\- Consider tracking basal body temperature to confirm ovulation

Lifestyle Strategies:  
\- Stress management is critical (cortisol blocks progesterone production)  
\- Vitamin B6 (100 mg daily) supports progesterone synthesis  
\- Magnesium glycinate (300-400 mg daily) improves PMS symptoms  
\- Ensure adequate cholesterol intake (progesterone is made from cholesterol)

Supplement Considerations:  
\- Vitex (chasteberry) may support healthy progesterone levels  
\- Discuss bioidentical progesterone cream with your provider for severe PMS/PMDD

Cycle Optimization:  
\- Seed cycling: Flax/pumpkin seeds (follicular), sunflower/sesame (luteal)  
\- Ensure ovulation is occurring (progesterone only produced if you ovulate)

---

**SECTION 10: FINAL JSON OUTPUT SCHEMA**

**10.1 Complete Response Structure**

{  
  "assessment\_metadata": {  
    "user\_id": "user\_abc123",  
    "assessment\_date": "2025-11-07",  
    "version": "1.0",  
    "disclaimer": "This assessment is for educational purposes only and does not constitute medical diagnosis. Please consult a qualified healthcare provider."  
  },

  "user\_profile": {  
    "age": 28,  
    "last\_period\_date": "2025-10-15",  
    "cycle\_length": 32,  
    "birth\_control": "none",  
    "diagnosed\_conditions": \["PCOS", "Hashimoto's"\]  
  },

  "cycle\_context": {  
    "current\_phase": "luteal",  
    "days\_since\_period": 18,  
    "phase\_confidence": "high",  
    "estimated\_next\_period": "2025-11-16"  
  },

  "assessment\_results": {  
    "primary\_imbalance": {  
      "hormone": "androgens",  
      "direction": "high",  
      "total\_score": 10,  
      "breakdown": {  
        "from\_symptoms": 5,  
        "from\_diagnosis": 3,  
        "from\_labs": 2  
      },  
      "contributing\_factors": \[  
        "Hirsutism (very strong indicator)",  
        "Adult acne",  
        "PCOS diagnosis",  
        "Free testosterone \>2.0 pg/mL"  
      \],  
      "explanation": "\[See Section 9.3 Example 1\]",  
      "recommendations": {  
        "testing": \["Fasting insulin", "HbA1c", "DHEA-S"\],  
        "lifestyle": \["Low-glycemic diet", "Strength training"\],  
        "supplements": \["Inositol", "Spearmint tea", "Zinc"\]  
      }  
    },

    "secondary\_imbalances": \[  
      {  
        "hormone": "insulin",  
        "direction": "high",  
        "total\_score": 6,  
        "explanation": "...",  
        "recommendations": {...}  
      },  
      {  
        "hormone": "thyroid",  
        "direction": "low",  
        "total\_score": 5,  
        "explanation": "...",  
        "recommendations": {...}  
      }  
    \],

    "all\_hormone\_scores": {  
      "estrogen": {  
        "total": 2,  
        "direction": "high",  
        "from\_symptoms": 1,  
        "from\_diagnosis": 1,  
        "from\_labs": 0  
      },  
      "progesterone": {  
        "total": 4,  
        "direction": "low",  
        "from\_symptoms": 2,  
        "from\_diagnosis": 2,  
        "from\_labs": 0  
      },  
      "androgens": {  
        "total": 10,  
        "direction": "high",  
        "from\_symptoms": 5,  
        "from\_diagnosis": 3,  
        "from\_labs": 2  
      },  
      "insulin": {  
        "total": 6,  
        "direction": "high",  
        "from\_symptoms": 2,  
        "from\_diagnosis": 3,  
        "from\_labs": 1  
      },  
      "cortisol": {  
        "total": 3,  
        "direction": "high",  
        "from\_symptoms": 2,  
        "from\_diagnosis": 0,  
        "from\_labs": 1  
      },  
      "thyroid": {  
        "total": 5,  
        "direction": "low",  
        "from\_symptoms": 2,  
        "from\_diagnosis": 3,  
        "from\_labs": 0  
      }  
    }  
  },

  "confidence": {  
    "level": "medium",  
    "score": 4,  
    "calculation\_breakdown": \[  
      {"factor": "Regular cycle data provided", "points": 2},  
      {"factor": "PCOS diagnosis", "points": 1},  
      {"factor": "Hashimoto's diagnosis", "points": 1},  
      {"factor": "Top concern selected", "points": 1},  
      {"factor": "3+ androgen symptoms", "points": 1},  
      {"factor": "No labs uploaded", "points": \-1},  
      {"factor": "Conflicting estrogen signals", "points": \-1}  
    \],  
    "recommendation": "Your assessment is moderately reliable based on symptoms and diagnoses. Uploading lab results (testosterone, insulin, TSH, progesterone) would increase confidence to HIGH."  
  },

  "conflicts": \[  
    {  
      "type": "symptom\_mismatch",  
      "severity": "low",  
      "description": "Both bloating (high estrogen) and light spotting (low estrogen) reported",  
      "recommendation": "Test estradiol on Day 3-5 of cycle to clarify estrogen status",  
      "impact\_on\_confidence": \-1  
    }  
  \],

  "clinical\_flags": \[  
    {  
      "flag\_type": "testing\_recommended",  
      "urgency": "moderate",  
      "message": "Consider comprehensive hormone panel including: Free testosterone, DHEA-S, TSH, Free T3, Fasting insulin, HbA1c, Progesterone (day 19-22)"  
    },  
    {  
      "flag\_type": "cycle\_tracking",  
      "urgency": "low",  
      "message": "Track basal body temperature to confirm ovulation is occurring regularly"  
    }  
  \],

  "lab\_results": {  
    "uploaded": false,  
    "tests\_analyzed": \[\],  
    "concordance\_score": null,  
    "recommendations": "Upload labs for enhanced accuracy. Recommended tests: \[list\]"  
  },

  "llm\_processed\_inputs": \[  
    {  
      "user\_input": "I think I might have lean PCOS",  
      "llm\_confidence": "medium",  
      "hormones\_impacted": \[  
        {"hormone": "androgens", "score\_applied": 1},  
        {"hormone": "insulin", "score\_applied": 1}  
      \],  
      "reasoning": "Lean PCOS is a phenotype with normal weight but androgen excess"  
    }  
  \],

  "next\_steps": {  
    "immediate": \[  
      "Schedule appointment with gynecologist or endocrinologist to discuss findings",  
      "Begin tracking symptoms daily to identify patterns",  
      "Consider hormone testing: Free testosterone, DHEA-S, TSH, Free T3, Fasting insulin, HbA1c"  
    \],  
    "short\_term": \[  
      "Implement low-glycemic diet to support insulin sensitivity",  
      "Begin stress management practices (meditation, yoga, adequate sleep)",  
      "Consider supplements: Inositol for PCOS, Selenium for thyroid support",  
      "Track basal body temperature for 2-3 cycles to confirm ovulation"  
    \],  
    "long\_term": \[  
      "Regular follow-up hormone testing every 3-6 months",  
      "Work with healthcare provider on personalized treatment plan",  
      "Consider lifestyle modifications: strength training, anti-inflammatory diet",  
      "Monitor symptom improvement and adjust interventions accordingly"  
    \]  
  }  
}

---

**SECTION 11: BACKEND IMPLEMENTATION ARCHITECTURE**

**11.1 System Flow Overview**

**Step-by-Step Backend Process:**

1. **User Input Reception**

   * Mobile app sends questionnaire responses via REST API

   * Validate input data structure and completeness

   * Sanitize all user inputs for security

2. **Data Validation Layer**

   * Verify age range (18-40)

   * Validate date formats for cycle tracking

   * Check for required fields completion

   * Flag any data inconsistencies

3. **Heuristic Scoring Engine**

   * Initialize hormone score objects for all 6 hormones

   * Process each question response through scoring rules (Section 2\)

   * Apply symptom weights to corresponding hormones

   * Track score sources (symptoms, diagnosis, labs)

4. **Cycle Phase Calculation**

   * Calculate days since last period

   * Determine current cycle phase

   * Apply phase-aware score adjustments (Section 4\)

   * Flag abnormal timing patterns

5. **LLM Integration Point (for "Others" input)**

   * Construct prompt with system context \+ user input

   * Call Gemini API with structured prompt

   * Validate JSON response using Pydantic models

   * Apply LLM-derived scores to aggregation

   * Handle API failures gracefully

6. **Score Aggregation**

   * Sum scores from all sources for each hormone

   * Apply birth control modifier if applicable

   * Apply top concern multiplier (1.5x)

   * Calculate final totals

7. **Primary/Secondary Identification**

   * Rank hormones by total score

   * Identify primary imbalance (highest score)

   * Flag secondary imbalances (≥50% of primary)

   * Apply tie-breaking rules

8. **Confidence Calculation**

   * Evaluate all confidence factors (Section 7\)

   * Calculate total confidence score

   * Assign confidence level (Low/Medium/High)

   * Document confidence reasoning

9. **Conflict Detection**

   * Check for hormone direction conflicts

   * Identify diagnosis-symptom mismatches

   * Flag contradictory patterns

   * Generate resolution recommendations

10. **Clinical Explanation Generation**

    * Retrieve templates for identified imbalances

    * Populate with user-specific data

    * Generate personalized recommendations

    * Include testing and lifestyle guidance

11. **JSON Response Construction**

    * Assemble complete output per Section 10 schema

    * Include all metadata, scores, and explanations

    * Add disclaimer and next steps

    * Return to mobile app

12. **Logging & Analytics**

    * Log assessment for quality monitoring

    * Track LLM usage and confidence patterns

    * Monitor for unusual scoring patterns

    * Store anonymized data for system improvement

---

**11.2 LLM Integration Detailed Workflow**

**Gemini API Call Structure for "Others" Input:**

**Input Preparation:**

User Context Bundle:  
\- Age: \[user\_age\]  
\- Selected Symptoms: \[comma-separated list\]  
\- Diagnosed Conditions: \[if any selected\]  
\- Current Cycle Phase: \[if calculable\]  
\- Period Pattern: \[regular/irregular/etc\]  
\- Birth Control Status: \[yes/no/type\]

User "Others" Input: "\[free text from user\]"

**System Prompt (Sent to Gemini):**

ROLE: Clinical Hormone Scoring Assistant for Women's Health

CONTEXT:  
You are analyzing a custom health concern entered by a woman aged \[AGE\]   
in a hormone assessment application. Your task is to map this input to   
our hormone scoring system following established clinical heuristics.

USER PROFILE:  
\- Age: \[AGE\]  
\- Symptoms already reported: \[SYMPTOM\_LIST\]  
\- Diagnosed conditions: \[DIAGNOSIS\_LIST\]  
\- Cycle pattern: \[PATTERN\]  
\- Current phase: \[PHASE if available\]

HORMONES WE TRACK:  
1\. Estrogen (can be HIGH or LOW)  
2\. Progesterone (typically LOW)  
3\. Androgens (typically HIGH)  
4\. Insulin (typically HIGH)  
5\. Cortisol (can be HIGH or LOW)  
6\. Thyroid (typically LOW)

SCORING RULES YOU MUST FOLLOW:  
\[Insert complete heuristic rules from Section 2.5 and 2.7\]

CRITICAL REQUIREMENTS:  
\- Be conservative if input is vague or ambiguous  
\- Consider existing reported symptoms to avoid double-counting  
\- Flag if condition requires immediate medical attention  
\- Return ONLY valid JSON \- no markdown, no explanations outside JSON  
\- Use only these hormone names: estrogen, progesterone, androgens, insulin, cortisol, thyroid  
\- Use only these directions: high, low  
\- Score weights must be integers: 0, 1, 2, or 3

USER INPUT TO ANALYZE:  
"\[USER\_OTHERS\_INPUT\]"

REQUIRED JSON OUTPUT FORMAT:  
{  
  "hormone\_impacts": \[  
    {  
      "hormone": "hormone\_name",  
      "direction": "high or low",  
      "score\_weight": 0-3,  
      "reasoning": "Brief clinical rationale"  
    }  
  \],  
  "overall\_confidence": "high|medium|low",  
  "clinical\_flags": \["array of any concerns or recommendations"\],  
  "needs\_medical\_review": true|false  
}

**Response Validation (Pydantic Models):**

from pydantic import BaseModel, Field, validator  
from typing import List, Literal

class HormoneImpact(BaseModel):  
    hormone: Literal\["estrogen", "progesterone", "androgens", "insulin", "cortisol", "thyroid"\]  
    direction: Literal\["high", "low"\]  
    score\_weight: int \= Field(ge=0, le=3)  
    reasoning: str \= Field(min\_length=10, max\_length=500)  
      
    @validator('reasoning')  
    def reasoning\_must\_be\_clinical(cls, v):  
        if len(v.split()) \< 5:  
            raise ValueError('Reasoning must be substantive')  
        return v

class LLMScoringResponse(BaseModel):  
    hormone\_impacts: List\[HormoneImpact\]  
    overall\_confidence: Literal\["high", "medium", "low"\]  
    clinical\_flags: List\[str\] \= \[\]  
    needs\_medical\_review: bool  
      
    @validator('hormone\_impacts')  
    def no\_duplicate\_hormones(cls, v):  
        hormones \= \[impact.hormone for impact in v\]  
        if len(hormones) \!= len(set(hormones)):  
            raise ValueError('Cannot score same hormone twice')  
        return v  
      
    class Config:  
        extra \= 'forbid'  \# Reject any additional fields

**Error Handling Strategy:**

IF Gemini API Call Fails:  
1\. Log error details (API status, error message, user context)  
2\. Attempt retry once after 2-second delay  
3\. If retry fails:  
   \- Apply conservative keyword-based fallback scoring:  
     \* Scan input for keywords: "hair loss" → thyroid \+1, androgens \+1  
     \* "weight gain" → thyroid \+1, insulin \+1, cortisol \+1  
     \* "acne" → androgens \+1  
     \* etc.  
4\. Set confidence to "low"  
5\. Add flag: "Unable to fully analyze custom input \- please consult healthcare provider"  
6\. Continue assessment with available data

IF Gemini Returns Invalid JSON:  
1\. Attempt to parse with lenient JSON parser  
2\. If still fails, treat as API failure (use fallback)  
3\. Log malformed response for debugging

IF Pydantic Validation Fails:  
1\. Log validation errors  
2\. If only minor issues (e.g., reasoning too short), use data anyway but reduce confidence  
3\. If major issues (invalid hormone names, score out of range), reject and use fallback  
4\. Flag response for manual review

**Confidence Penalty Application:**

After receiving and validating LLM response:

IF overall\_confidence \== "high":  
    confidence\_score \+= 0  \# No penalty  
ELIF overall\_confidence \== "medium":  
    confidence\_score \-= 1  \# Moderate penalty  
ELIF overall\_confidence \== "low":  
    confidence\_score \-= 2  \# Significant penalty

IF needs\_medical\_review \== true:  
    Add to clinical\_flags: "Your reported condition requires professional medical evaluation. Please schedule an appointment with a healthcare provider."

---

**11.3 Lab Report Integration Workflow**

**Lab Upload Options:**

1. **PDF Upload**

   * Accept PDF file from mobile app

   * Use OCR (Optical Character Recognition) to extract text

   * Parse extracted text for lab value patterns

   * Match to expected lab tests (Section 6.1)

2. **Manual Entry**

   * Provide structured form with lab test fields

   * User enters values directly

   * Validate ranges on input

   * Store with timestamp

**Lab Value Extraction Logic:**

For PDF Processing:  
1\. Extract text using OCR library (e.g., Tesseract, Google Cloud Vision API)  
2\. Clean and normalize text (remove extra spaces, fix formatting)  
3\. Use regex patterns to identify lab values:  
   \- "TSH: 3.5 mIU/L" → Extract: TSH \= 3.5  
   \- "Free Testosterone 2.3 pg/mL" → Extract: Free T \= 2.3  
   \- "Fasting Insulin: 8 µIU/mL" → Extract: Fasting Insulin \= 8  
4\. Map extracted values to standardized lab test names  
5\. Validate extracted values against expected ranges  
6\. Flag any values outside normal ranges for user confirmation

Pattern Matching Examples:  
\- TSH: r'TSH\[:\\s\]+(\\d+\\.?\\d\*)\\s\*(mIU/L|uIU/mL)'  
\- Free T: r'Free\\s+Testosterone\[:\\s\]+(\\d+\\.?\\d\*)\\s\*(pg/mL|ng/dL)'  
\- Fasting Insulin: r'Fasting\\s+Insulin\[:\\s\]+(\\d+\\.?\\d\*)\\s\*(µIU/mL|uIU/mL)'

**Lab Scoring Application:**

For each extracted lab value:  
1\. Identify which hormone it relates to (per Section 6.1 table)  
2\. Check if value exceeds threshold  
3\. If yes, add score\_weight to hormone's "from\_labs" score  
4\. Track which labs were used in scoring

Example:  
IF TSH \> 2.5 AND TSH \<= 4.5:  
    thyroid.from\_labs \+= 2  \# Subclinical hypothyroidism  
ELIF TSH \> 4.5:  
    thyroid.from\_labs \+= 3  \# Overt hypothyroidism

IF Free\_Testosterone \> 2.0:  
    androgens.from\_labs \+= 2  \# Androgen excess

**Concordance Checking:**

After applying lab scores:

For each hormone with non-zero lab scores:  
    IF hormone has non-zero symptom scores:  
        \# Labs and symptoms agree  
        concordance \= "high"  
        confidence\_score \+= 2  
        Add note: "Lab results confirm reported symptoms"  
    ELSE:  
        \# Labs show issue but no symptoms reported  
        concordance \= "medium"  
        Add note: "Lab abnormality detected without corresponding symptoms \- may be subclinical"

For each hormone with non-zero symptom scores but zero lab scores:  
    IF labs were uploaded:  
        \# Symptoms present but labs normal  
        concordance \= "low"  
        confidence\_score \-= 2  
        Add conflict: "Symptoms suggest \[hormone\] imbalance but labs are normal"  
        Suggest additional testing or other causes

---

**SECTION 12: MOBILE APP SPECIFIC CONSIDERATIONS**

**12.1 Differences from Web Version**

**Key Adaptations for Mobile:**

1. **Question Flow**

   * Mobile uses progressive disclosure (one question at a time)

   * Web may show multiple questions per screen

   * Backend must handle partial completion and resume logic

   * Save state between questions for app crashes/interruptions

2. **Input Validation**

   * Mobile has native date pickers → Ensure backend accepts ISO 8601 format

   * Mobile may send GPS location → Use for timezone-aware cycle calculations

   * Mobile keyboard types affect input → Sanitize numeric vs text inputs differently

3. **Offline Capability Considerations**

   * Mobile app may queue responses when offline

   * Backend should handle batch processing of queued assessments

   * Timestamp validation to ensure data freshness

4. **File Upload Handling**

   * Mobile sends base64-encoded images/PDFs for lab reports

   * Larger file sizes than web due to phone camera resolution

   * Implement file size limits (e.g., 10MB max)

   * Compress images before processing

**12.2 Mobile API Endpoints**

**Recommended Endpoint Structure:**

POST /api/v1/assessment/start  
\- Initialize new assessment  
\- Return assessment\_id for subsequent calls  
\- Store user\_id and metadata

POST /api/v1/assessment/{assessment\_id}/question/{question\_number}  
\- Submit answer for specific question  
\- Validate and store response  
\- Return next question or completion status

POST /api/v1/assessment/{assessment\_id}/lab-upload  
\- Accept lab report file (base64 encoded)  
\- Process and extract values  
\- Return extracted values for user confirmation

GET /api/v1/assessment/{assessment\_id}/results  
\- Calculate final scores and confidence  
\- Generate explanations  
\- Return complete JSON response per Section 10

POST /api/v1/assessment/{assessment\_id}/validate-others  
\- Dedicated endpoint for LLM processing of "Others" input  
\- Can be called independently for faster feedback  
\- Returns hormone impacts for UI preview before final submission

**12.3 Response Time Optimization**

**Performance Targets:**

* Standard question validation: \<200ms

* LLM "Others" processing: \<3 seconds

* Lab report OCR: \<5 seconds

* Final results calculation: \<1 second

* Total assessment completion: \<15 seconds (excluding user think time)

**Optimization Strategies:**

1. **Caching:**

   * Cache common symptom → hormone mappings

   * Cache LLM responses for identical "Others" inputs (with user consent)

   * Cache explanation templates

2. **Async Processing:**

   * Process LLM calls asynchronously with loading indicator

   * OCR lab reports in background, show progress

   * Pre-calculate partial scores after each question

3. **API Rate Limiting:**

   * Implement token bucket for Gemini API calls

   * Queue requests if rate limit approached

   * Provide user feedback if delays expected

---

**SECTION 13: QUALITY ASSURANCE & TESTING**

**13.1 Test Cases for Scoring Logic**

**Critical Test Scenarios:**

**Test Case 1: Clear PCOS Presentation**

Input:  
\- Age: 26  
\- Periods: Irregular  
\- Cycle length: 35+ days  
\- Symptoms: Hirsutism, Adult Acne, Difficulty losing weight  
\- Top concern: Hirsutism  
\- Diagnosis: PCOS  
\- Birth control: None  
\- Labs: Free T \= 2.8 pg/mL, LH:FSH \= 3:1

Expected Output:  
\- Primary: Androgens (score \~15-18)  
\- Secondary: Insulin (score \~8-10)  
\- Confidence: HIGH (score 7-9)  
\- No major conflicts

**Test Case 2: Lean PCOS (Conflicting Signals)**

Input:  
\- Age: 24  
\- Periods: Regular  
\- Cycle length: 26-30 days  
\- Symptoms: Mood swings, Stress  
\- Top concern: Mood swings  
\- Diagnosis: PCOS  
\- Birth control: None  
\- Labs: None uploaded

Expected Output:  
\- Conflict detected: "PCOS diagnosed but no androgen symptoms present"  
\- Primary: Progesterone LOW (from mood symptoms)  
\- Secondary: Androgens (from diagnosis only)  
\- Confidence: LOW-MEDIUM (score 2-4)  
\- Flag: "Possible lean PCOS phenotype"

**Test Case 3: Hypothyroidism with High Concordance**

Input:  
\- Age: 32  
\- Periods: Regular  
\- Cycle length: 26-30 days  
\- Symptoms: Fatigue, Recent weight gain, Thinning of hair  
\- Top concern: Fatigue  
\- Diagnosis: Hashimoto's  
\- Birth control: None  
\- Labs: TSH \= 4.2, Free T3 \= 2.1

Expected Output:  
\- Primary: Thyroid LOW (score \~12-14)  
\- Confidence: HIGH (score 7-8)  
\- Note: "Lab results confirm reported symptoms"

**Test Case 4: Birth Control Masking**

Input:  
\- Age: 28  
\- Periods: Regular (on BC)  
\- Cycle length: 28 days  
\- Symptoms: Bloating, Mood swings  
\- Top concern: Bloating  
\- Diagnosis: None  
\- Birth control: Hormonal pills  
\- Labs: None

Expected Output:  
\- All scores reduced by 30%  
\- Confidence: MEDIUM-LOW (score 2-3)  
\- Note: "Birth control may be masking symptoms"  
\- Recommendation: "Consider assessment 3+ months off birth control"

**Test Case 5: LLM Integration \- Vague Input**

Input "Others": "I feel really tired all the time"

Expected LLM Response:  
{  
  "hormone\_impacts": \[  
    {"hormone": "thyroid", "direction": "low", "score\_weight": 2},  
    {"hormone": "cortisol", "direction": "high", "score\_weight": 1}  
  \],  
  "overall\_confidence": "medium",  
  "clinical\_flags": \["Recommend TSH testing", "Consider sleep quality assessment"\],  
  "needs\_medical\_review": false  
}

Confidence penalty: \-1

**13.2 Edge Cases to Handle**

1. **Conflicting Hormone Directions:**

   * User reports both heavy periods (high estrogen) and hot flashes (low estrogen)

   * System should flag conflict and recommend estradiol testing

2. **All Questions Marked "I'm Not Sure":**

   * Confidence score will be very low (0-1)

   * Flag: "Insufficient data for reliable assessment"

   * Recommendation: "Please track symptoms for 1-2 cycles and retake"

3. **Extreme Lab Values:**

   * TSH \= 15 (very high) → Flag for urgent medical attention

   * Glucose \= 140 (diabetes range) → Priority medical referral

   * Add urgency level to flags

4. **Age at Boundary:**

   * Age 18 or 40 may have different considerations

   * Age \<18 → Reject assessment, outside target population

   * Age \>40 → Consider perimenopausal patterns

5. **No Symptoms but Diagnosis:**

   * User selects PCOS but no symptoms

   * Either well-controlled or possible misdiagnosis

   * Lower confidence, note potential for medication management

**13.3 Validation Metrics**

**System Performance Monitoring:**

1. **Accuracy Metrics:**

   * Track % of assessments where primary hormone matches eventual lab diagnosis (if available)

   * Monitor confidence score calibration (are HIGH confidence assessments more accurate?)

   * Target: \>80% concordance for HIGH confidence assessments

2. **LLM Quality Metrics:**

   * Track % of "Others" inputs successfully mapped by LLM

   * Monitor fallback usage rate (should be \<5%)

   * Review manually flagged LLM responses weekly

3. **User Experience Metrics:**

   * Average time to complete assessment

   * % of assessments completed vs abandoned

   * User satisfaction with explanations (if feedback collected)

4. **Clinical Safety Metrics:**

   * Track % of urgent flags generated

   * Monitor false negative rate for serious conditions

   * Ensure no harmful recommendations generated

---

**SECTION 14: DATA PRIVACY & SECURITY**

**14.1 Sensitive Data Handling**

**Protected Health Information (PHI):**

All data collected in this assessment constitutes PHI under HIPAA and similar regulations:

* Personal identifiers (name, age)

* Health conditions and symptoms

* Menstrual cycle data

* Lab test results

**Security Requirements:**

1. **Encryption:**

   * All data encrypted in transit (TLS 1.3)

   * All data encrypted at rest (AES-256)

   * Lab report images/PDFs encrypted in storage

2. **Access Controls:**

   * Role-based access for backend staff

   * Audit logging of all data access

   * User data isolated by user\_id

3. **Data Retention:**

   * Store assessment results for medical continuity

   * Allow user deletion of data ("Right to be Forgotten")

   * Anonymize data after user deletion for analytics

4. **Third-Party Services:**

   * Gemini API calls must not store user data permanently

   * OCR services should process data in-memory only

   * No user data in error logs or monitoring tools

**SECTION 16: FUTURE ENHANCEMENTS**

**16.1 Planned Features**

**Phase 2 Enhancements:**

1. **Longitudinal Tracking:**

   * Allow users to retake assessment monthly

   * Track hormone score trends over time

   * Correlate changes with interventions (diet, supplements, medication)

   * Visualize improvement or deterioration

2. **Personalized Recommendations:**

   * Generate specific meal plans for hormone support

   * Recommend targeted supplements based on imbalances

   * Suggest exercises optimal for identified issues

   * Connect to telehealth providers specializing in hormones

3. **Advanced Lab Integration:**

   * Direct integration with lab company APIs (Quest, LabCorp)

   * Automated lab ordering based on assessment results

   * Track lab values over time in-app

     

4. **Integration with Smart Devices (Wearables):**  
     
   * Enable syncing with smartwatches, fitness trackers, and Oura Ring

   * Automatically collect sleep patterns, stress levels, heart rate variability, and activity data

   * Combine physiological data with symptom-based assessments for deeper hormonal insights  
       
5. **Gamification and Engagement Layer:**  
     
   * Introduce badges, streaks, and progress milestones to motivate consistent tracking

   * Add personal challenges (e.g., stress management goals, cycle tracking consistency)

   * Provide personalized achievement reports and gentle reminders to improve user engagement  
     

     
     
     
     
     
     
     
   

**APPENDIX A: QUICK REFERENCE TABLES**

**Symptom → Hormone Mapping Summary**

| Symptom Category | Primary Hormones | Score Weights |
| ----- | ----- | ----- |
| Irregular Periods | Androgens, Thyroid, Cortisol | \+2, \+1, \+1 |
| Heavy Periods | Estrogen HIGH, Progesterone LOW | \+2, \+1 |
| Light Periods | Estrogen LOW, Progesterone LOW | \+2, \+1 |
| Painful Periods | Progesterone LOW, Estrogen HIGH | \+2, \+1 |
| Hot Flashes | Estrogen LOW, Thyroid | \+3, \+1 |
| Hirsutism | Androgens | \+3 |
| Adult Acne | Androgens, Insulin | \+2, \+1 |
| Hair Thinning | Thyroid, Androgens | \+2, \+1 |
| Weight Gain | Thyroid, Cortisol, Insulin | \+2, \+1, \+1 |
| Stubborn Weight | Insulin, Cortisol, Thyroid | \+2, \+2, \+2 |
| Bloating | Estrogen HIGH, Cortisol | \+2, \+1 |
| Mood Swings | Progesterone LOW, Cortisol | \+2, \+1 |
| Fatigue | Thyroid, Cortisol, Insulin | \+2, \+2, \+1 |
| Stress | Cortisol HIGH | \+2 |

**Confidence Score Factors**

| Factor | Points | Type |
| ----- | ----- | ----- |
| Regular cycles | \+2 | Positive |
| Last period date provided | \+1 | Positive |
| Diagnosed condition | \+1 | Positive |
| Top concern selected | \+1 | Positive |
| 3+ symptoms in cluster | \+1 | Positive |
| Lab results uploaded | \+2 | Positive |
| Labs align with symptoms | \+2 | Positive |
| No birth control | \+1 | Positive |
| Irregular cycles | \-1 | Negative |
| "I'm not sure" cycle date | \-2 | Negative |
| On hormonal BC | \-1 | Negative |
| Conflicting symptoms | \-2 | Negative |
| Only diagnosis, no symptoms | \-1 | Negative |
| LLM low confidence | \-2 | Negative |
| No labs (high severity) | \-1 | Negative |
| Labs contradict symptoms | \-2 | Negative |

 

