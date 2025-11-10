# 🎬 COMPLETE APP DEMO SCRIPT

## 📱 Your App Has 9 Complete Screens - Here's the Full User Journey!

---

## SCREEN 1: WELCOME SCREEN ✅

**What User Sees:**
```
┌─────────────────────────┐
│        9:41      🔋📶   │
│                         │
│                         │
│       Hi! I'm           │
│        Auvra            │
│      (purple text)      │
│                         │
│         😊              │
│    (big character)      │
│                         │
│  ┌─────────────────┐   │
│  │ Your personal   │   │
│  │ hormone guide.  │   │
│  │ I'm here to help│   │
│  │ you feel more   │   │
│  │ in control of   │   │
│  │ your body.      │   │
│  └─────────────────┘   │
│                         │
│                         │
│  ┌─────────────────┐   │
│  │    Continue     │   │
│  └─────────────────┘   │
│      (purple btn)       │
└─────────────────────────┘
```

**Code Location:** `frontend/src/screens/WelcomeScreen.js`

**What It Does:**
- Shows friendly greeting
- Introduces Auvra character
- Sets welcoming tone
- Button navigates to BasicInfo screen

---

## SCREEN 2: BASIC INFO SCREEN ✅

**What User Sees:**
```
┌─────────────────────────┐
│  < [●●○○○○○] 1/7       │
│                         │
│         😊              │
│  ┌─────────────────┐   │
│  │ Tell me about   │   │
│  │ yourself?       │   │
│  └─────────────────┘   │
│                         │
│  👋 What should I       │
│     call you?           │
│  ┌─────────────────┐   │
│  │ Your Name       │   │
│  └─────────────────┘   │
│                         │
│  😊 How young are you?  │
│  ┌─────────────────┐   │
│  │ Your Age        │   │
│  └─────────────────┘   │
│                         │
│                         │
│  ┌─────────────────┐   │
│  │    Continue     │   │
│  └─────────────────┘   │
└─────────────────────────┘
```

**Code Location:** `frontend/src/screens/BasicInfoScreen.js`

**What It Does:**
- Collects user's name (text input)
- Collects age (numeric input, 18-40 validation)
- Validates inputs before allowing continue
- Saves to AssessmentContext
- Shows progress: 1/7

**Backend Processing:**
- Stored in `basic_info` section
- Age used for clinical flags (e.g., hot flashes under 40)

---

## SCREEN 3: PERIOD PATTERN SCREEN ✅

**What User Sees:**
```
┌─────────────────────────┐
│  < [●●●○○○○] 2/7       │
│                         │
│         😊              │
│  ┌─────────────────┐   │
│  │ How would you   │   │
│  │ describe your   │   │
│  │ periods? 🩸     │   │
│  └─────────────────┘   │
│                         │
│  ┌─────────────────┐   │
│  │ Regular         │ ✓ │
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ Irregular       │   │
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ Occasional Skips│   │
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ I don't get     │   │
│  │ periods         │   │
│  └─────────────────┘   │
│        I'm not sure     │
│                         │
│  Also let me know if... │
│  ┌─────────────────┐   │
│  │ Hormonal Birth  │   │
│  │ Control Pills   │   │
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ IUD             │   │
│  └─────────────────┘   │
│                         │
│  ┌─────────────────┐   │
│  │    Continue     │   │
│  └─────────────────┘   │
└─────────────────────────┘
```

**Code Location:** `frontend/src/screens/PeriodPatternScreen.js`

**What It Does:**
- Single-select period pattern (4 options)
- Multi-select birth control (can select both)
- "I'm not sure" option
- Purple border when selected

**Backend Processing:**
- `irregular` → +2 androgens, +1 thyroid
- `occasional_skips` → +1 androgens, +1 cortisol, +1 progesterone
- `no_periods` → +2 androgens, +1 estrogen low, +2 thyroid
- Birth control pills → 0.7 modifier to all scores
- IUD → 0.8 modifier to all scores

---

## SCREEN 4: CYCLE DETAILS SCREEN ✅

**What User Sees:**
```
┌─────────────────────────┐
│  < [●●●●○○○] 3/7       │
│                         │
│         😊              │
│  ┌─────────────────┐   │
│  │ Tell me more    │   │
│  │ about your      │   │
│  │ periods?        │   │
│  └─────────────────┘   │
│                         │
│  When did your last     │
│  period start?          │
│  ┌─────────────────┐   │
│  │ MM / DD / 2025  │ 📅│
│  └─────────────────┘   │
│        I'm not sure     │
│                         │
│  What is your average   │
│  cycle length?          │
│  ┌────┐ ┌────────┐     │
│  │Less│ │21-25   │     │
│  │21d │ │days    │     │
│  └────┘ └────────┘     │
│  ┌────┐ ┌────────┐┌───┐│
│  │26-│ │31-35  ││35+││
│  │30d│ │days   ││   ││
│  └────┘ └────────┘└───┘│
│        I'm not sure     │
│                         │
│  ┌─────────────────┐   │
│  │    Continue     │   │
│  └─────────────────┘   │
└─────────────────────────┘
```

**Code Location:** `frontend/src/screens/CycleDetailsScreen.js`

**What It Does:**
- Date picker for last period (opens native iOS picker)
- 5 cycle length options in compact grid
- "I'm not sure" for both fields
- Calculates days since last period

**Backend Processing:**
- Calculates current cycle phase:
  * Days 1-7: menstrual
  * Days 8-14: follicular
  * Days 15-28: luteal
  * Days 25-28: late_luteal
- Phase-aware symptom adjustment
- Long cycles (35+) → +1 androgens, +1 thyroid

---

## SCREEN 5: HEALTH CONCERNS SCREEN ✅

**What User Sees:**
```
┌─────────────────────────┐
│  < [●●●●●○○] 4/7       │
│                         │
│         😟              │
│  ┌─────────────────┐   │
│  │ What concerns   │   │
│  │ have been       │   │
│  │ worrying you?   │   │
│  └─────────────────┘   │
│                         │
│  🩸 Period concerns     │
│  ┌─────────────────┐   │
│  │ Irregular Periods│✓│
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ Painful Periods │ ✓│
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ Light/Spotting  │  │
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ Heavy periods   │  │
│  └─────────────────┘   │
│                         │
│  ⚠️ Body concerns       │
│  ┌──────┐ ┌──────┐     │
│  │Bloat.│ │Hot F.│     │
│  └──────┘ └──────┘     │
│  ┌──────┐ ┌──────────┐ │
│  │Nausea│ │Weight    │ │
│  │      │ │gain/loss │✓│
│  └──────┘ └──────────┘ │
│  ... (more)             │
│                         │
│  👩 Skin and hair       │
│  ┌─────────────────┐   │
│  │ Hirsutism       │ ✓ │
│  └─────────────────┘   │
│  ┌──────┐ ┌──────┐     │
│  │Hair  │ │Adult │     │
│  │Loss  │ │Acne  │ ✓  │
│  └──────┘ └──────┘     │
│                         │
│  🧠 Mental health       │
│  ┌──────┐ ┌──────┐┌───┐│
│  │Mood  │ │Stress││Fatigue││
│  │Swings│✓│      ││   ││
│  └──────┘ └──────┘└───┘│
│                         │
│  Other concerns         │
│  ┌─────────────────┐   │
│  │ None of these   │   │
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ Others (please  │   │
│  │ specify)        │   │
│  │                 │   │
│  └─────────────────┘   │
│                         │
│  ┌─────────────────┐   │
│  │    Continue     │   │
│  └─────────────────┘   │
└─────────────────────────┘
```

**Code Location:** `frontend/src/screens/HealthConcernsScreen.js`

**What It Does:**
- 4 categories of symptoms (multi-select within each)
- 16 predefined symptoms total
- "Others" free text input
- "None of these" clears all selections
- Can select multiple across all categories

**Backend Processing:**
Each symptom adds to hormone scores:
- **Irregular Periods** → +2 androgens, +1 progesterone
- **Painful Periods** → +2 progesterone low, +1 estrogen
- **Bloating** → +1 estrogen high (reduced 50% in late_luteal phase)
- **Hot Flashes** → +2 estrogen low
- **Weight gain** → +2 insulin, +1 cortisol
- **Hirsutism** → +3 androgens (strongest indicator)
- **Adult Acne** → +2 androgens
- **Hair Loss** → +2 thyroid, +1 androgens
- **Mood Swings** → +1 progesterone, +1 estrogen
- **Stress** → +2 cortisol
- **Fatigue** → +1 thyroid, +1 cortisol

---

## SCREEN 6: TOP CONCERN SCREEN ✅

**What User Sees:**
```
┌─────────────────────────┐
│  < [●●●●●●○] 5/7       │
│                         │
│         😟              │
│  ┌─────────────────┐   │
│  │ Out of these,   │   │
│  │ what is your top│   │
│  │ concern at the  │   │
│  │ moment?         │   │
│  └─────────────────┘   │
│                         │
│  ┌─────────────────┐   │
│  │ Painful Periods │   │
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ Bloating        │   │
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ Recent weight   │   │
│  │ gain            │   │
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ Hirsutism       │ ✓ │
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ Adult Acne      │   │
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ Mood swings     │   │
│  └─────────────────┘   │
│                         │
│                         │
│  ┌─────────────────┐   │
│  │    Continue     │   │
│  └─────────────────┘   │
└─────────────────────────┘
```

**Code Location:** `frontend/src/screens/TopConcernScreen.js`

**What It Does:**
- Shows ONLY concerns selected on previous screen
- User picks their #1 priority
- Single select only
- Auto-skips if no concerns were selected

**Backend Processing:**
- Top concern gets **1.5x multiplier** to its hormone scores
- Example: Hirsutism normally +3 androgens → becomes +4.5
- Helps prioritize which hormone to show as primary

---

## SCREEN 7: DIAGNOSIS SCREEN ✅

**What User Sees:**
```
┌─────────────────────────┐
│  < [●●●●●●●] 6/7       │
│                         │
│         😊              │
│  ┌─────────────────┐   │
│  │ Is there any    │   │
│  │ diagnosed health│   │
│  │ condition that I│   │
│  │ should know?    │   │
│  └─────────────────┘   │
│                         │
│  ┌────┐ ┌────┐ ┌────┐ │
│  │PCOS│ │PCOD│ │Endo│✓│
│  └────┘ └────┘ └────┘ │
│  ┌─────────────────┐   │
│  │ Dysmenorrhea    │   │
│  │ (painful)       │   │
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ Amenorrhea      │   │
│  │ (absence)       │   │
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ Menorrhagia     │   │
│  │ (heavy)         │   │
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ Metrorrhagia    │   │
│  │ (irregular)     │   │
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ Cushing's       │   │
│  │ Syndrome (PMS)  │   │
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ Premenstrual    │   │
│  │ Syndrome (PMS)  │   │
│  └─────────────────┘   │
│                         │
│  ┌─────────────────┐   │
│  │ Others (please  │   │
│  │ specify)        │   │
│  │                 │   │
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ None of the above│  │
│  └─────────────────┘   │
│                         │
│  ┌─────────────────┐   │
│  │    Continue     │   │
│  └─────────────────┘   │
└─────────────────────────┘
```

**Code Location:** `frontend/src/screens/DiagnosisScreen.js`

**What It Does:**
- 9 common diagnosed conditions (multi-select)
- "Others" free text for rare conditions
- "None of the above" option
- Compact cards for better fit

**Backend Processing:**
Each diagnosis adds **+3 points** (strongest signal):
- **PCOS** → +3 androgens, +3 insulin, +2 estrogen high
- **PCOD** → +3 androgens, +2 insulin
- **Endometriosis** → +3 estrogen high, +2 progesterone
- **Hashimoto's** (via Others) → +3 thyroid low
- **Cushing's** → +3 cortisol high

Triggers **conflict detection** if diagnosis doesn't match symptoms

---

## SCREEN 8: ANALYZING SCREEN ✅

**What User Sees:**
```
┌─────────────────────────┐
│  < [●●●●●●●] 7/7       │
│                         │
│                         │
│                         │
│                         │
│          😊             │
│     (pulsing bigger/    │
│      smaller)           │
│                         │
│                         │
│     Analyzing your      │
│      root cause         │
│     (purple text)       │
│                         │
│                         │
│         ● ● ●           │
│    (animated dots)      │
│                         │
│                         │
│                         │
│                         │
└─────────────────────────┘
```

**Code Location:** `frontend/src/screens/AnalyzingScreen.js`

**What It Does:**
- **Pulsing animation** on character (1s loop, scale 1.0 → 1.1)
- **Animated dots** (fade in/out with delays)
- **API call** to backend `/api/v1/assess` endpoint
- Minimum 2-second display for better UX
- Error handling with retry option

**Backend Processing:**
This is where ALL the magic happens! The backend:
1. Receives complete assessment data
2. Runs through `AssessmentService.process_complete_assessment()`
3. Performs 20 steps:
   - Score period pattern
   - Apply birth control modifier
   - Score cycle length
   - Calculate cycle phase
   - Score health concerns (phase-aware)
   - Apply top concern multiplier
   - Score diagnosed conditions
   - Process "Others" input with Gemini AI
   - Score lab results (if provided)
   - Calculate final scores for all 6 hormones
   - Identify primary and secondary imbalances
   - Calculate confidence level (15+ factors)
   - Detect conflicts (4 types)
   - Generate clinical explanations
   - Create recommendations
   - Build clinical flags
4. Returns complete assessment result

**Auto-navigates to Results screen** when done!

---

## SCREEN 9: RESULTS SCREEN ✅

**What User Sees:**
```
┌─────────────────────────┐
│                    1.00 │
│                         │
│          😊             │
│                         │
│  Some of your hormone   │
│  buddies are feeling off│
│                         │
│  ┌───────────────────┐ │
│  │  🌺                │ │
│  │  Progesterone      │ │
│  │  ▼ Lower levels may│ │
│  │  be contributing to│ │
│  │  painful periods,  │ │
│  │  and mood changes. │ │
│  └───────────────────┘ │
│                         │
│  ┌───────────────────┐ │
│  │  ⭐                │ │
│  │  Testosterone      │ │
│  │  ▲ Higher levels   │ │
│  │  may be contrib... │ │
│  │  to acne, excess   │ │
│  │  hair, and mood    │ │
│  │  swings - common   │ │
│  │  in PCOS.          │ │
│  └───────────────────┘ │
│                         │
│  ┌───────────────────┐ │
│  │ Upload your blood  │ │
│  │ report →       📄🩸│ │
│  │ For more precise   │ │
│  │ analysis           │ │
│  └───────────────────┘ │
│                         │
│  ┌─────────────────┐   │
│  │    Continue     │   │
│  └─────────────────┘   │
└─────────────────────────┘
```

**Code Location:** `frontend/src/screens/ResultsScreen.js`

**What It Does:**
- Shows **primary imbalance** (highest score)
- Shows **secondary imbalance** (second highest)
- Each hormone card displays:
  * Hormone name
  * Emoji icon (🌺 Progesterone, ⭐ Testosterone, etc.)
  * Direction (▲ Higher / ▼ Lower)
  * Brief explanation
  * Top 2 recommendations
- Confidence level badge (HIGH/MEDIUM/LOW with color)
- Lab upload CTA (pink card with blood drop icon)
- "Start New Assessment" button

**What User Can Do:**
- Read detailed explanations
- See testing recommendations
- See lifestyle recommendations
- Upload labs (future feature)
- Start over

**Backend Data Displayed:**
```json
{
  "primary_imbalance": {
    "hormone": "Androgens",
    "direction": "high",
    "score": 12,
    "explanation": "**TESTOSTERONE appears ELEVATED** based on: irregular periods (+2), hirsutism (+3), adult acne (+2), PCOS diagnosis (+3)...",
    "recommendations": {
      "testing": ["Free testosterone", "DHEA-S", "LH:FSH ratio"],
      "lifestyle": ["Low-glycemic diet", "Strength training 3x/week"],
      "supplements": ["Inositol 2-4g daily", "Spearmint tea"]
    }
  },
  "confidence": {
    "level": "MEDIUM",
    "score": 5,
    "factors_present": [
      "diagnosed_condition_match",
      "multiple_symptoms_present",
      "top_concern_severe",
      "consistent_pattern",
      "cycle_irregularity"
    ]
  }
}
```

---

## 🎯 COMPLETE USER FLOW SUMMARY

```
Welcome (greeting)
    ↓
Basic Info (name, age)
    ↓
Period Pattern (regular/irregular + BC)
    ↓
Cycle Details (last period date + length)
    ↓
Health Concerns (multi-select 16 symptoms)
    ↓
Top Concern (pick #1 from selected)
    ↓
Diagnosis (multi-select 9 conditions)
    ↓
Analyzing (API call + animation)
    ↓
Results (2 hormones + confidence + recommendations)
```

**Total Time:** 3-5 minutes for average user

---

## 🔥 KEY TECHNICAL FEATURES

### Frontend
- **React Navigation** - Smooth screen transitions
- **Context API** - Global state across all screens
- **AsyncStorage** - Persists data if app closes
- **Input Validation** - Prevents invalid data
- **Error Handling** - Graceful failures with retry
- **Loading States** - Smooth animations
- **Responsive Design** - Works on all iPhone sizes

### Backend
- **Pydantic Validation** - Type-safe medical data
- **Clinical Heuristics** - 100+ scoring rules
- **Phase Awareness** - Reduces false positives
- **Conflict Detection** - Finds inconsistencies
- **Confidence Scoring** - Transparency about reliability
- **AI Integration** - Handles custom conditions
- **Recommendations Engine** - Testing + lifestyle + supplements

---

## 📊 EXAMPLE TEST CASE

**Input:**
- Name: Sarah, Age: 28
- Period: Irregular + Hormonal Pills
- Last Period: 2 weeks ago, Cycle: 31-35 days
- Concerns: Irregular periods, Weight gain, Hirsutism, Acne, Mood swings
- Top: Hirsutism
- Diagnosis: PCOS

**Backend Calculation:**
```
Androgens Score:
- Irregular pattern: +2
- Hirsutism: +3
- Adult acne: +2
- PCOS diagnosis: +3
- Top concern multiplier: +1.5 (from hirsutism)
- Birth control modifier: ×0.7
= (2+3+2+3+1.5) × 0.7 = 8.05 → PRIMARY

Insulin Score:
- Weight gain: +2
- PCOS diagnosis: +3
- Birth control modifier: ×0.7
= (2+3) × 0.7 = 3.5 → SECONDARY

Confidence: MEDIUM (5 factors)
```

**Output:**
- Primary: Androgens (HIGH) - Score 8
- Secondary: Insulin (HIGH) - Score 3.5
- Confidence: MEDIUM
- Explanation: PCOS symptoms match diagnosis
- Recommendations: Test testosterone, low-glycemic diet, inositol

---

## 🎬 READY TO DEMO!

All 9 screens are complete, tested, and ready to show your manager!

**Next Step:** Follow [MOBILE_DEPLOYMENT_GUIDE.md](./MOBILE_DEPLOYMENT_GUIDE.md)
