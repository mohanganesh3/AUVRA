# 🌟 AUVRA - Hormone Assessment System

**AI-Powered Women's Health Application**

AUVRA is an intelligent hormone assessment system that combines symptom analysis, AI-powered natural language processing (Google Gemini), and laboratory data validation to provide comprehensive hormone imbalance insights for women.

---

## 📋 Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [How It Works](#how-it-works)
- [Example Usage](#example-usage)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

### Core Capabilities

- **🧬 6 Hormone Analysis**
  - Estrogen (HIGH/LOW)
  - Progesterone (LOW)
  - Androgens (HIGH)
  - Insulin (HIGH)
  - Cortisol (HIGH/LOW)
  - Thyroid (LOW)

- **🤖 AI-Powered Analysis**
  - Google Gemini 2.5 Flash integration
  - Natural language understanding for custom health inputs
  - Combined API calls (50% faster than sequential calls)
  - Intelligent duplicate merging

- **🧪 Laboratory Validation**
  - Evidence-based biomarker thresholds
  - Lab-symptom concordance calculation
  - Objective data validation

- **⚖️ Smart Conflict Resolution**
  - Priority hierarchy: Lab > Diagnosis > AI > Symptoms
  - Intelligent decision-making for contradictory inputs

- **📊 Confidence Scoring**
  - Transparent reliability assessment (0-10 scale)
  - HIGH/MEDIUM/LOW confidence levels
  - Multi-factor confidence calculation

- **📱 Mobile-First Design**
  - React Native frontend (Expo)
  - Cross-platform support (iOS/Android)
  - Intuitive 7-screen assessment flow

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Mobile Frontend (React Native/Expo)       │
│                                                              │
│  Screens:                                                    │
│  1. BasicInfo  2. PeriodPattern  3. CycleDetails            │
│  4. HealthConcerns  5. DiagnosedConditions                   │
│  6. LabResults  7. Results                                   │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/JSON
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  Backend (FastAPI + Python)                 │
│                                                              │
│  20-Step Assessment Pipeline:                               │
│  ├── Symptom Scoring (Clinical Heuristics)                  │
│  ├── Diagnosis Scoring (Fixed Weights)                      │
│  ├── AI Analysis (Google Gemini - Combined Call)            │
│  ├── Lab Scoring (Evidence-Based Thresholds)                │
│  ├── Conflict Detection & Resolution                        │
│  └── Confidence Calculation                                 │
│                                                              │
│  Services:                                                   │
│  ├── assessment_service.py (Main Logic)                     │
│  ├── llm_service.py (Gemini Integration)                    │
│  ├── scoring_service.py (Lab & Symptom Scoring)             │
│  └── validation.py (Pydantic Models)                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ API Call
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              Google Gemini 2.5 Flash API                    │
│                                                              │
│  Natural Language Understanding for:                         │
│  • Custom health concerns                                    │
│  • Diagnosed conditions "Others" field                       │
│  • Clinical reasoning & hormone scoring                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Prerequisites

### Required Software

- **Python 3.10+** (Backend)
- **Node.js 18+** (Frontend)
- **npm or yarn** (Package manager)
- **Expo CLI** (React Native development)

### API Keys

- **Google Gemini API Key** - Get it from [Google AI Studio](https://makersuite.google.com/app/apikey)

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AUVRA
```

### 2. Backend Setup

```bash
# Create Python virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows

# Install backend dependencies
pip install fastapi uvicorn pydantic pydantic-settings python-dotenv google-generativeai
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd auvra-app/frontend

# Install dependencies
npm install

# OR using yarn
yarn install
```

---

## ⚙️ Configuration

### Backend Configuration

Create a `.env` file in the project root:

```bash
cd /Users/mohanganesh/AUVRA
touch .env
```

Add the following environment variables:

```env
# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=models/gemini-2.5-flash

# Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=5055

# Environment
ENVIRONMENT=development
```

### Frontend Configuration

Update API endpoint in `auvra-app/frontend/config.js` (if exists) or directly in API calls:

```javascript
// Example: services/api.js or similar
const API_BASE_URL = 'http://localhost:5055';  // For local development
// const API_BASE_URL = 'http://YOUR_IP:5055';  // For mobile device testing
```

---

## 🚀 Running the Application

### Method 1: Separate Terminals (Recommended for Development)

#### Terminal 1: Start Backend

```bash
cd /Users/mohanganesh/AUVRA

# Activate virtual environment
source .venv/bin/activate

# Kill any existing server on port 5055
pkill -f 'uvicorn.*5055' || true

# Start FastAPI server
uvicorn --app-dir /Users/mohanganesh/AUVRA/auvra-app/backend app:app --host 0.0.0.0 --port 5055 --log-level info
```

**Expected Output:**
```
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
[LLM][INIT] Gemini configured. model=models/gemini-2.5-flash (api key present: yes)
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5055 (Press CTRL+C to quit)
```

#### Terminal 2: Start Frontend

```bash
cd /Users/mohanganesh/AUVRA/auvra-app/frontend

# Start Expo development server
npx expo start
```

**Expected Output:**
```
Starting Metro Bundler
› Metro waiting on exp://192.168.x.x:8081
› Scan the QR code above with Expo Go (Android) or Camera app (iOS)
```

### Method 2: Using Scripts (Optional)

Create a startup script `start.sh`:

```bash
#!/bin/bash

# Start backend in background
cd /Users/mohanganesh/AUVRA
source .venv/bin/activate
pkill -f 'uvicorn.*5055' || true
uvicorn --app-dir /Users/mohanganesh/AUVRA/auvra-app/backend app:app --host 0.0.0.0 --port 5055 --log-level info &

# Wait for backend to start
sleep 3

# Start frontend
cd auvra-app/frontend
npx expo start
```

Make executable and run:
```bash
chmod +x start.sh
./start.sh
```

---

## 📱 Testing the Application

### On Physical Device

1. Install **Expo Go** app from App Store (iOS) or Play Store (Android)
2. Scan the QR code from the Expo Metro Bundler
3. Make sure your phone and computer are on the same Wi-Fi network

### On Simulator/Emulator

**iOS Simulator:**
```bash
# Press 'i' in the Expo terminal
# OR
npx expo start --ios
```

**Android Emulator:**
```bash
# Press 'a' in the Expo terminal
# OR
npx expo start --android
```

### API Health Check

Test backend is running:
```bash
curl http://localhost:5055/health
```

Expected response:
```json
{"status": "healthy"}
```

---

## 📚 API Documentation

### Endpoints

#### Health Check
```
GET /health
Response: {"status": "healthy"}
```

#### Hormone Assessment
```
POST /api/v1/assess
Content-Type: application/json

Request Body:
{
  "basic_info": {
    "name": "Sarah",
    "age": 28
  },
  "period_pattern": {
    "period_pattern": "irregular",
    "birth_control": "none"
  },
  "cycle_details": {
    "last_period_date": "2025-10-20",
    "date_not_sure": false,
    "cycle_length": "26-30"
  },
  "health_concerns": {
    "period_concerns": ["irregular_periods"],
    "body_concerns": ["recent_weight_gain"],
    "skin_hair_concerns": ["adult_acne"],
    "mental_health_concerns": ["mood_swings"],
    "others": "Sleep issues and sugar cravings",
    "none": false
  },
  "top_concern": {
    "top_concern": "irregular_periods"
  },
  "diagnosed_conditions": {
    "conditions": ["pcos"],
    "others_input": "Vitamin D deficiency"
  },
  "lab_results": {
    "total_testosterone": 68.0,
    "free_testosterone": 2.5,
    "tsh": 4.8,
    "fasting_insulin": 18.5,
    "am_cortisol": 22.0
  }
}

Response:
{
  "primary_hormone": "androgens",
  "primary_direction": "high",
  "primary_score": 20,
  "secondary_imbalances": [...],
  "confidence_level": "high",
  "confidence_score": 7,
  "all_hormone_scores": {...},
  "next_steps": [...],
  "clinical_flags": [...]
}
```

### Interactive API Docs

Once backend is running, visit:
- **Swagger UI:** http://localhost:5055/docs
- **ReDoc:** http://localhost:5055/redoc

---

## 📁 Project Structure

```
AUVRA/
├── auvra-app/
│   ├── backend/
│   │   ├── app.py                    # FastAPI main application
│   │   ├── services/
│   │   │   ├── assessment_service.py # 20-step assessment pipeline
│   │   │   ├── llm_service.py        # Google Gemini integration
│   │   │   ├── scoring_service.py    # Lab & symptom scoring
│   │   │   └── validation.py         # Pydantic models
│   │   └── utils/
│   │       └── helpers.py            # Helper functions
│   │
│   └── frontend/
│       ├── screens/
│       │   ├── BasicInfoScreen.js
│       │   ├── PeriodPatternScreen.js
│       │   ├── CycleDetailsScreen.js
│       │   ├── HealthConcernsScreen.js
│       │   ├── DiagnosedConditionsScreen.js
│       │   ├── LabResultsScreen.js
│       │   └── ResultsScreen.js
│       ├── components/
│       │   └── HormoneCard.js        # Results display component
│       ├── App.js                    # Main app component
│       └── package.json
│
├── .venv/                            # Python virtual environment
├── .env                              # Environment variables (not in git)
├── README.md                         # This file
├── AUVRA_BACKEND_EXPLANATION.md      # Technical documentation
└── AUVRA_BACKEND_EXPLANATION.pdf     # PDF documentation
```

---

## 🛠️ Technologies Used

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation and settings management
- **Uvicorn** - ASGI server
- **Google Gemini 2.5 Flash** - AI language model
- **Python 3.10+** - Programming language

### Frontend
- **React Native** - Mobile app framework
- **Expo** - React Native development platform
- **JavaScript/ES6+** - Programming language
- **React Navigation** - Screen navigation

### DevOps
- **Git** - Version control
- **Virtual Environment** - Python dependency isolation

---

## 🔬 How It Works

### The 20-Step Assessment Pipeline

1. **Score Period Pattern** - Irregular/regular/absent
2. **Apply Birth Control Modifier** - Hormonal contraception adjustments
3. **Score Cycle Length** - Short/long cycle implications
4. **Calculate Cycle Context** - Menstrual phase determination
5. **Score Health Concerns** - Phase-aware symptom analysis
6. **Apply Top Concern Multiplier** - 1.5x weight for primary issue
7. **Score Diagnosed Conditions** - PCOS, hypothyroidism, etc.
8. **Process 'Others' Inputs with AI** - Gemini combined analysis ⭐
9. **Score Laboratory Results** - Evidence-based thresholds
10. **Calculate Final Scores** - Aggregate all sources
11. **Determine Primary/Secondary** - Rank hormones by score
12. **Count Symptoms by Cluster** - Pattern recognition
13. **Calculate Confidence Score** - Reliability assessment
14. **Detect Conflicts** - Contradictory signal identification
15. **Build Explanations** - Clinical narratives
16. **Generate Clinical Flags** - Safety alerts
17. **Generate Next Steps** - Actionable recommendations
18. **Compile Hormone Scores** - Complete breakdown
19. **Build User Profile** - Demographic context
20. **Finalize Assessment Response** - Package results

### Key Innovations

**🚀 Combined Gemini API Calls**
- **Before:** 2 separate calls = 6-10 seconds
- **After:** 1 combined call = 3-5 seconds
- **Result:** 50% performance improvement

**🧠 Intelligent Duplicate Merging**
- Handles when Gemini returns same hormone twice
- Takes maximum severity score
- Combines reasoning (up to 500 chars)
- Passes Pydantic validation

**⚖️ Smart Conflict Resolution**
- Priority: Lab > Diagnosis > AI > Symptoms
- Considers AI confidence levels
- Adjusts overall confidence score

---

## 💡 Example Usage

### Complete Assessment Flow

```python
# Example test case (Sarah Mitchell - PCOS)
{
  "basic_info": {"name": "Sarah", "age": 28},
  "period_pattern": {"period_pattern": "irregular", "birth_control": "none"},
  "cycle_details": {
    "last_period_date": "2025-10-20",
    "date_not_sure": false,
    "cycle_length": "26-30"
  },
  "health_concerns": {
    "period_concerns": ["irregular_periods", "painful_periods"],
    "body_concerns": ["recent_weight_gain", "bloating"],
    "skin_hair_concerns": ["adult_acne", "hair_thinning"],
    "mental_health_concerns": ["mood_swings"],
    "others": "Difficult sleeping and sugar cravings throughout the day",
    "none": false
  },
  "top_concern": {"top_concern": "irregular_periods"},
  "diagnosed_conditions": {
    "conditions": ["pcos", "hypothyroidism"],
    "others_input": "Adrenal fatigue and Vitamin D deficiency"
  },
  "lab_results": {
    "total_testosterone": 68.0,
    "free_testosterone": 2.5,
    "dhea_s": 385.0,
    "lh": 18.5,
    "fsh": 8.2,
    "tsh": 4.8,
    "free_t3": 2.4,
    "free_t4": 0.9,
    "fasting_insulin": 18.5,
    "hba1c": 5.6,
    "fasting_glucose": 96.0,
    "am_cortisol": 22.0,
    "estradiol": 85.0,
    "progesterone": 2.5,
    "shbg": 35.0
  }
}
```

### Expected Result

```json
{
  "primary_hormone": "androgens",
  "primary_direction": "high",
  "primary_score": 20,
  "secondary_imbalances": [
    {"hormone": "thyroid", "direction": "low", "score": 18},
    {"hormone": "cortisol", "direction": "high", "score": 15},
    {"hormone": "insulin", "direction": "high", "score": 11}
  ],
  "confidence_level": "high",
  "confidence_score": 7,
  "explanation": "Androgen excess is the primary driver (classic PCOS pattern)..."
}
```

---

## 🐛 Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`
```bash
# Solution: Activate virtual environment and install dependencies
source .venv/bin/activate
pip install fastapi uvicorn pydantic google-generativeai
```

**Problem:** `Port 5055 already in use`
```bash
# Solution: Kill existing process
pkill -f 'uvicorn.*5055'
# OR find and kill manually
lsof -ti:5055 | xargs kill -9
```

**Problem:** `Gemini API error: API key not valid`
```bash
# Solution: Check .env file has correct API key
cat .env | grep GEMINI_API_KEY
# Regenerate key from https://makersuite.google.com/app/apikey
```

### Frontend Issues

**Problem:** `Cannot connect to backend`
```bash
# Solution 1: Check backend is running
curl http://localhost:5055/health

# Solution 2: Update API endpoint to your computer's IP
# In API calls, use: http://192.168.x.x:5055 instead of localhost
```

**Problem:** `Expo app won't load`
```bash
# Solution: Clear cache and restart
npx expo start --clear
```

**Problem:** `QR code not scanning`
```bash
# Solution: Ensure same Wi-Fi network
# OR use tunnel mode: npx expo start --tunnel
```

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| Average response time (with AI) | 5-7 seconds |
| Average response time (no AI) | 2-3 seconds |
| Gemini API success rate | >99.5% |
| Pydantic validation error rate | <1% |
| Frontend timeout rate | 0% |

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is part of an internship and is for educational purposes.

---

## 📧 Contact

**Author:** Mohan Ganesh  
**Project:** AUVRA Hormone Assessment System  
**Date:** November 2025

---

## 🙏 Acknowledgments

- Google Gemini AI for natural language processing
- FastAPI framework for robust backend development
- Expo for simplified React Native development
- Clinical hormone assessment guidelines

---

## 📝 Additional Resources

- **Technical Documentation:** See `AUVRA_BACKEND_EXPLANATION.pdf`
- **API Docs:** http://localhost:5055/docs (when running)
- **Google Gemini API:** https://ai.google.dev/

---

**⚠️ Important Note:** AUVRA is a clinical decision support tool, not a diagnostic system. All results should be reviewed by qualified healthcare providers.
