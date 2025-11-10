# Auvra Hormone Assessment Backend

Backend API for the Auvra mobile hormone assessment system.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 3. Run the Server

```bash
python app.py
```

Server will start on `http://localhost:5000`

## 📡 API Endpoints

### Health Check
```
GET /health
```

### Complete Assessment
```
POST /api/v1/assess
Content-Type: application/json

{
  "basic_info": {
    "name": "Jane",
    "age": 28
  },
  "period_pattern": {
    "period_pattern": "irregular",
    "birth_control": "none"
  },
  "cycle_details": {
    "last_period_date": "2025-10-15",
    "cycle_length": "35+",
    "date_not_sure": false
  },
  "health_concerns": {
    "period_concerns": ["irregular_periods"],
    "body_concerns": ["weight_difficulty"],
    "skin_hair_concerns": ["hirsutism", "adult_acne"],
    "mental_health_concerns": ["mood_swings"]
  },
  "top_concern": {
    "top_concern": "hirsutism"
  },
  "diagnosed_conditions": {
    "conditions": ["pcos"],
    "others_input": null
  },
  "lab_results": null
}
```

### Quick Assessment (Testing)
```
POST /api/v1/assess/quick
```

### Validate Custom Input
```
POST /api/v1/validate/others

{
  "input": "I have lean PCOS",
  "context": {
    "age": 28,
    "symptoms": ["mood_swings"],
    "diagnoses": []
  }
}
```

## 🏗️ Project Structure

```
backend/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── models/
│   └── schemas.py             # Pydantic models for validation
├── services/
│   ├── hormone_scorer.py      # Core scoring engine
│   ├── llm_service.py         # Gemini API integration
│   ├── cycle_calculator.py    # Cycle phase calculation
│   ├── confidence_calculator.py
│   ├── conflict_detector.py
│   ├── explanation_generator.py
│   └── assessment_service.py  # Main orchestrator
└── routes/
    └── (future route modules)
```

## 🔬 Core Features

- ✅ Heuristic-based hormone scoring (6 hormones)
- ✅ Cycle phase-aware symptom evaluation
- ✅ LLM integration for custom health concerns
- ✅ Confidence scoring system
- ✅ Conflict detection
- ✅ Clinical explanations with recommendations
- ✅ Lab result integration

## 🧪 Testing

### Test with curl:

```bash
# Health check
curl http://localhost:5000/health

# Quick assessment
curl -X POST http://localhost:5000/api/v1/assess/quick \
  -H "Content-Type: application/json" \
  -d '{
    "basic_info": {"name": "Test", "age": 28},
    "period_pattern": {"period_pattern": "irregular", "birth_control": "none"},
    "cycle_details": {"cycle_length": "35+", "date_not_sure": true},
    "health_concerns": {"period_concerns": ["irregular_periods"], "body_concerns": [], "skin_hair_concerns": ["hirsutism"], "mental_health_concerns": []},
    "top_concern": {"top_concern": "irregular_periods"},
    "diagnosed_conditions": {"conditions": ["pcos"]}
  }'
```

## 🔑 Getting Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy key to `.env` file

## 📱 Mobile App Integration

React Native app should call:
```javascript
const API_URL = 'http://YOUR_IP:5000';

const response = await fetch(`${API_URL}/api/v1/assess`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(assessmentData)
});

const result = await response.json();
```

## 🚢 Deployment

### Heroku
```bash
heroku create auvra-hormone-api
git push heroku main
heroku config:set GEMINI_API_KEY=your_key
```

### Railway
```bash
railway init
railway up
```

## 📊 Clinical Standards Referenced

- PCOS: Rotterdam Criteria
- Thyroid: Endocrine Society Guidelines (TSH >2.5 subclinical)
- PMDD: DSM-5 Criteria
- Insulin Resistance: Fasting insulin >6 µIU/mL

## 🛠️ Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run with auto-reload
FLASK_ENV=development python app.py

# The server will restart on code changes
```

## ⚠️ Important Notes

1. **API Key**: Never commit `.env` file with real API keys
2. **CORS**: Configured to allow all origins for development
3. **Production**: Add proper authentication and rate limiting
4. **Database**: Currently stateless, add database for user tracking

## 📞 Support

Built for HormoneInsight.ai evaluation
Version: 1.0
