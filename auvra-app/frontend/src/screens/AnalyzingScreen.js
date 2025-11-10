import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { AuvraCharacter } from '../components/UIComponents';
import { useAssessment } from '../utils/AssessmentContext';
import { submitAssessment } from '../services/api';
import { validateRequest } from '../utils/requestValidation';

export default function AnalyzingScreen({ navigation }) {
  const { assessmentData, setResult } = useAssessment();
  const [pulseAnim] = useState(new Animated.Value(1));

  useEffect(() => {
    // Pulsing animation for character
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.1,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();

    // Submit assessment to backend
    performAnalysis();
  }, []);

  const performAnalysis = async () => {
    try {
      // ================= Schema Transformation =================
      // The backend (Pydantic) expects the CompleteAssessmentRequest shape:
      // {
      //   basic_info: { name, age },
      //   period_pattern: { period_pattern, birth_control },
      //   cycle_details: { last_period_date, date_not_sure, cycle_length },
      //   health_concerns: { period_concerns, body_concerns, skin_hair_concerns, mental_health_concerns },
      //   top_concern: { top_concern },
      //   diagnosed_conditions: { conditions, others_input },
      //   lab_results: { ... } | null
      // }

      const raw = assessmentData || {};

      // --- Helpers / mappers ---
      const cycleLengthMap = {
        '<21': '<21',
        '21_25': '21-25',
        '26_30': '26-30',
        '31_35': '31-35',
        '35_plus': '35+',
        '35+': '35+',
        'not_sure': 'not_sure'
      };

      const normalizeCycleLength = (val) => cycleLengthMap[val] || '26-30';

      // Frontend may store birth_control as array or single value; backend wants single Literal.
      const normalizeBirthControl = (val) => {
        if (!val) return 'none';
        if (Array.isArray(val)) {
          // Filter to known tokens; first valid wins
          const allowed = ['hormonal_pills', 'hormonal_iud', 'copper_iud', 'none'];
          const firstValid = val.find(v => allowed.includes(v));
          return firstValid || 'none';
        }
        // If a stray single character like 'h' got stored, treat as none
        if (val.length < 5) return 'none';
        return ['hormonal_pills', 'hormonal_iud', 'copper_iud', 'none'].includes(val) ? val : 'none';
      };

      // Map display labels (if any) to backend tokens
      // Robust mappers: case-insensitive + phrase-to-token conversion
      const toSnakeToken = (s) =>
        (s || '')
          .toString()
          .trim()
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, ' ')
          .trim()
          .replace(/\s+/g, '_');

      // Allowed tokens per category (must match backend Pydantic Literals)
      const ALLOWED = {
        period: new Set(['irregular_periods', 'painful_periods', 'light_periods', 'heavy_periods']),
        body: new Set(['bloating', 'hot_flashes', 'nausea', 'weight_difficulty', 'recent_weight_gain', 'menstrual_headaches']),
        skin_hair: new Set(['hirsutism', 'hair_thinning', 'adult_acne']),
        mental: new Set(['mood_swings', 'stress', 'fatigue']),
      };

      // Synonyms/variants to handle UI phrasing differences
      const SYNONYMS = {
        // period
        'light_periods_spotting': 'light_periods',
        'heavy_periods': 'heavy_periods',
        // body
        'difficulty_losing_weight_stubborn_belly_fat': 'weight_difficulty',
        'recent_weight_gain': 'recent_weight_gain',
        'menstrual_headache': 'menstrual_headaches',
        'menstrual_headaches': 'menstrual_headaches',
        // skin/hair
        'hair_thinning': 'hair_thinning',
        'thinning_of_hair': 'hair_thinning',
        // mental
        'mood_swings': 'mood_swings',
      };

      const mapSymptomsCategory = (arr, category) => {
        if (!Array.isArray(arr)) return [];
        const allowed = ALLOWED[category];
        return arr
          .map((s) => {
            if (!s) return null;
            // If already a valid token
            if (allowed.has(s)) return s;
            const snake = toSnakeToken(s);
            if (allowed.has(snake)) return snake;
            const viaSyn = SYNONYMS[snake];
            if (viaSyn && allowed.has(viaSyn)) return viaSyn;
            return null; // drop unknowns to satisfy Pydantic
          })
          .filter(Boolean);
      };

      // Diagnosed conditions mapping to expected lowercase tokens
      const conditionMap = {
        // Display label variants to canonical tokens
        'PCOS': 'pcos',
        'PCOD': 'pcod',
        'Endometriosis': 'endometriosis',
        'Dysmenorrhea (painful periods)': 'dysmenorrhea',
        'Dysmenorrhea': 'dysmenorrhea', // fallback without parentheses
        'Amenorrhea (absence of periods)': 'amenorrhea',
        'Amenorrhea': 'amenorrhea',
        'Menorrhagia (prolonged/heavy bleeding)': 'menorrhagia',
        'Menorrhagia': 'menorrhagia',
        'Metrorrhagia (irregular bleeding)': 'metrorrhagia',
        'Metrorrhagia': 'metrorrhagia',
        'Premenstrual Syndrome (PMS)': 'pms',
        'PMS': 'pms',
        'Premenstrual Dysphoric Disorder (PMDD)': 'pmdd',
        'PMDD': 'pmdd',
        'Hashimotos (thyroid autoimmunity)': 'hashimotos',
        'Hashimotos': 'hashimotos',
        'Hypothyroidism': 'hypothyroidism'
      };

      const ALLOWED_DIAGNOSES = new Set([
        'pcos','pcod','endometriosis','dysmenorrhea','amenorrhea','menorrhagia','metrorrhagia','pms','pmdd','hashimotos','hypothyroidism'
      ]);

      const sanitizeToken = (raw) => {
        if (!raw) return null;
        // Direct map
        if (conditionMap[raw]) return conditionMap[raw];
        // Attempt normalization: strip parentheses content, lower-case
        const base = raw
          .replace(/\([^)]*\)/g, '') // remove parenthetical notes
          .toLowerCase()
          .trim()
          .replace(/[^a-z0-9]+/g, '_')
          .replace(/^_+|_+$/g, '');
        // Known short forms mapping
        const shortMap = {
          'dysmenorrhea_painful_periods': 'dysmenorrhea',
          'amenorrhea_absence_of_periods': 'amenorrhea',
          'menorrhagia_prolonged_heavy_bleeding': 'menorrhagia',
          'metrorrhagia_irregular_bleeding': 'metrorrhagia',
          'premenstrual_syndrome_pms': 'pms',
          'premenstrual_dysphoric_disorder_pmdd': 'pmdd',
          'hashimotos_thyroid_autoimmunity': 'hashimotos'
        };
        const normalized = shortMap[base] || base;
        return ALLOWED_DIAGNOSES.has(normalized) ? normalized : null;
      };

      const mapConditions = (arr) => {
        if (!Array.isArray(arr)) return [];
        const mapped = arr
          .map(sanitizeToken)
          .filter(Boolean);
        return Array.from(new Set(mapped));
      };

      // Extract raw pieces
      const basicInfo = raw.basic_info || {};
      const periodPattern = raw.period_pattern || {};
      const cycleDetails = raw.cycle_details || {};
      const concerns = raw.health_concerns || {};
      const diagnosed = raw.diagnosed_conditions || {};

      // Map top concern to token if it's a display label
      const ALL_ALLOWED_TOP = new Set([
        ...ALLOWED.period,
        ...ALLOWED.body,
        ...ALLOWED.skin_hair,
        ...ALLOWED.mental,
        'none',
      ]);

      const normalizeTopConcern = (val) => {
        if (!val) return 'none';
        if (ALL_ALLOWED_TOP.has(val)) return val;
        const snake = toSnakeToken(val);
        // direct allowed
        if (ALL_ALLOWED_TOP.has(snake)) return snake;
        // try synonyms
        const viaSyn = SYNONYMS[snake];
        if (viaSyn && ALL_ALLOWED_TOP.has(viaSyn)) return viaSyn;
        return 'none';
      };

      const topConcernValue = typeof raw.top_concern === 'string'
        ? normalizeTopConcern(raw.top_concern)
        : normalizeTopConcern(raw.top_concern?.top_concern);

      const requestData = {
        basic_info: {
          name: basicInfo.name || 'User',
            // Coerce age to int within backend bounds
          age: (() => {
            const a = parseInt(basicInfo.age, 10);
            if (isNaN(a) || a < 18 || a > 40) return 25;
            return a;
          })()
        },
        period_pattern: {
          period_pattern: periodPattern.pattern || periodPattern.period_pattern || 'regular',
          birth_control: normalizeBirthControl(periodPattern.birth_control)
        },
        cycle_details: {
          last_period_date: cycleDetails.last_period_date || null,
          date_not_sure: cycleDetails.date_not_sure || !cycleDetails.last_period_date || false,
          cycle_length: cycleDetails.cycle_length || normalizeCycleLength(cycleDetails.average_cycle_length || '26_30')
        },
        health_concerns: {
          period_concerns: mapSymptomsCategory(concerns.period || concerns.period_concerns, 'period'),
          body_concerns: mapSymptomsCategory(concerns.body || concerns.body_concerns, 'body'),
          skin_hair_concerns: mapSymptomsCategory(concerns.skin_hair || concerns.skin_hair_concerns, 'skin_hair'),
          mental_health_concerns: mapSymptomsCategory(concerns.mental || concerns.mental_health_concerns, 'mental'),
          others: concerns.others || null,
          none: concerns.none || false
        },
        top_concern: { top_concern: topConcernValue || 'none' },
        diagnosed_conditions: {
          conditions: mapConditions(diagnosed.conditions),
          others_input: diagnosed.others || diagnosed.others_input || null
        },
        lab_results: raw.lab_results || null
      };

      console.log('Transformed assessment payload:', JSON.stringify(requestData, null, 2));

      const preflight = validateRequest(requestData);
      if (!preflight.ok) {
        console.warn('Preflight validation failed:', preflight.errors);
        Alert.alert(
          'Validation Issue',
          'Some answers need correction before analysis. Returning you to the previous screen.',
          [
            { text: 'Fix Now', onPress: () => navigation.goBack() }
          ]
        );
        return;
      }

      const response = await submitAssessment(requestData);

      console.log('Assessment result:', JSON.stringify(response, null, 2));

      // Save result to context
      setResult(response);

      // Small delay for better UX (minimum 2 seconds)
      setTimeout(() => {
        navigation.replace('Results');
      }, 2000);

    } catch (error) {
      console.error('Analysis error:', error);
      console.error('Error details:', {
        message: error.message,
        code: error.code,
        response: error.response?.data,
        status: error.response?.status,
      });
      
      // Determine error message based on error type
      let errorMessage = 'Unable to complete your hormone assessment. Please check your connection and try again.';
      
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'Request timed out. The server might be processing your assessment. Please try again.';
      } else if (error.message === 'Network Error') {
        errorMessage = 'Cannot reach the server. Please check:\n• Backend is running on port 5055\n• You are on the same WiFi network\n• Try restarting the app';
      } else if (error.response) {
        errorMessage = `Server error (${error.response.status}): ${error.response.data?.detail || 'Unknown error'}`;
      }
      
      Alert.alert(
        'Analysis Error',
        errorMessage,
        [
          {
            text: 'Retry',
            onPress: () => performAnalysis(),
          },
          {
            text: 'Go Back',
            onPress: () => navigation.goBack(),
            style: 'cancel',
          },
        ]
      );
    }
  };

  return (
    <LinearGradient colors={['#FFFFFF', '#F5E6F9']} style={styles.container}>
      <View style={styles.content}>
        {/* Animated Character */}
        <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
          <AuvraCharacter expression="happy" size={200} />
        </Animated.View>

        {/* Loading Text */}
        <Text style={styles.title}>Analyzing your{'\n'}root cause</Text>

        {/* Loading Dots */}
        <View style={styles.dotsContainer}>
          <LoadingDot delay={0} />
          <LoadingDot delay={200} />
          <LoadingDot delay={400} />
        </View>
      </View>
    </LinearGradient>
  );
}

// Animated loading dot component
function LoadingDot({ delay }) {
  const [opacity] = useState(new Animated.Value(0.3));

  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.delay(delay),
        Animated.timing(opacity, {
          toValue: 1,
          duration: 600,
          useNativeDriver: true,
        }),
        Animated.timing(opacity, {
          toValue: 0.3,
          duration: 600,
          useNativeDriver: true,
        }),
      ])
    ).start();
  }, []);

  return <Animated.View style={[styles.dot, { opacity }]} />;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    color: '#B565A7',
    textAlign: 'center',
    marginTop: 40,
    lineHeight: 42,
  },
  dotsContainer: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 32,
  },
  dot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#B565A7',
  },
});
