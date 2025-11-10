import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import {
  AuvraCharacter,
  PrimaryButton,
  MessageBubble,
  ProgressBar,
  SelectionCard,
} from '../components/UIComponents';
import { useAssessment } from '../utils/AssessmentContext';

const DIAGNOSES = [
  'PCOS',
  'PCOD',
  'Endometriosis',
  'Dysmenorrhea (painful periods)',
  'Amenorrhea (absence of periods)',
  'Menorrhagia (prolonged/heavy bleeding)',
  'Metrorrhagia (irregular bleeding)',
  'Premenstrual Syndrome (PMS)',
  'Premenstrual Dysphoric Disorder (PMDD)',
  'Hashimotos (thyroid autoimmunity)',
  'Hypothyroidism'
];

// Mapping from display labels to backend tokens
const DIAGNOSIS_TOKEN_MAP = {
  'PCOS': 'pcos',
  'PCOD': 'pcod',
  'Endometriosis': 'endometriosis',
  'Dysmenorrhea (painful periods)': 'dysmenorrhea',
  'Amenorrhea (absence of periods)': 'amenorrhea',
  'Menorrhagia (prolonged/heavy bleeding)': 'menorrhagia',
  'Metrorrhagia (irregular bleeding)': 'metrorrhagia',
  'Premenstrual Syndrome (PMS)': 'pms',
  'Premenstrual Dysphoric Disorder (PMDD)': 'pmdd',
  'Hashimotos (thyroid autoimmunity)': 'hashimotos',
  'Hypothyroidism': 'hypothyroidism'
};

export default function DiagnosisScreen({ navigation }) {
  const { assessmentData, updateSection } = useAssessment();
  
  // Ensure we store DISPLAY LABELS in state, not tokens.
  const tokenToLabel = Object.entries(DIAGNOSIS_TOKEN_MAP).reduce((acc, [label, token]) => {
    acc[token] = label;
    return acc;
  }, {});

  const [selectedDiagnoses, setSelectedDiagnoses] = useState(() => {
    const tokens = assessmentData.diagnosed_conditions?.conditions || [];
    // Map tokens back to display labels; drop unknowns
    return tokens.map(t => tokenToLabel[t] || t).filter(Boolean);
  });
  const [noneSelected, setNoneSelected] = useState(false);
  const [othersText, setOthersText] = useState(
    assessmentData.diagnosed_conditions?.others || ''
  );

  const toggleDiagnosis = (diagnosis) => {
    setNoneSelected(false);
    setSelectedDiagnoses((prev) =>
      prev.includes(diagnosis)
        ? prev.filter((item) => item !== diagnosis)
        : [...prev, diagnosis]
    );
  };

  const handleNoneOfAbove = () => {
    if (!noneSelected) {
      setSelectedDiagnoses([]);
      setOthersText('');
    }
    setNoneSelected(!noneSelected);
  };

  const handleContinue = () => {
    // Transform display labels to backend tokens and de-duplicate
    const transformedConditions = Array.from(new Set(
      selectedDiagnoses.map(
        diagnosis => DIAGNOSIS_TOKEN_MAP[diagnosis] || diagnosis.toLowerCase()
      )
    ));
    
    updateSection('diagnosed_conditions', {
      conditions: transformedConditions,
      others: othersText.trim(),
      none: noneSelected,
    });
    
    navigation.navigate('LabResults');
  };

  return (
    <LinearGradient colors={['#F5E6F9', '#E8D4F4']} style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Progress Bar */}
  <ProgressBar progress={6} steps={8} />

        {/* Top Section */}
        <View style={styles.topSection}>
          <AuvraCharacter expression="happy" size={120} />
          <MessageBubble text="Is there any diagnosed health condition that I should know about?" />
        </View>

        {/* Diagnoses List */}
        <View style={styles.diagnosesContainer}>
          {DIAGNOSES.map((diagnosis) => (
            <SelectionCard
              key={diagnosis}
              title={diagnosis}
              selected={selectedDiagnoses.includes(diagnosis) && !noneSelected}
              onPress={() => toggleDiagnosis(diagnosis)}
              compact
            />
          ))}
        </View>

        {/* Others and None Options */}
        <View style={styles.bottomOptions}>
          <TextInput
            style={[styles.othersInput, noneSelected && styles.othersInputDisabled]}
            placeholder="Others (please specify)"
            placeholderTextColor="#C4C4C4"
            value={othersText}
            onChangeText={setOthersText}
            multiline
            editable={!noneSelected}
          />

          <SelectionCard
            title="None of the above"
            selected={noneSelected}
            onPress={handleNoneOfAbove}
          />
        </View>
      </ScrollView>

      {/* Bottom Button */}
      <View style={styles.bottomContainer}>
        <PrimaryButton
          title="Continue"
          onPress={handleContinue}
        />
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 60,
    paddingBottom: 120,
  },
  topSection: {
    alignItems: 'center',
    marginBottom: 32,
  },
  diagnosesContainer: {
    gap: 12,
    marginBottom: 24,
  },
  bottomOptions: {
    gap: 12,
  },
  othersInput: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    fontSize: 16,
    color: '#333',
    borderWidth: 1,
    borderColor: '#E8E8E8',
    minHeight: 80,
    textAlignVertical: 'top',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  othersInputDisabled: {
    backgroundColor: '#F5F5F5',
    color: '#C4C4C4',
  },
  bottomContainer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    paddingHorizontal: 24,
    paddingBottom: 40,
    paddingTop: 16,
    backgroundColor: 'transparent',
  },
});
