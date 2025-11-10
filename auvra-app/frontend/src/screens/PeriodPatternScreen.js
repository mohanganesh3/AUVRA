import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import {
  AuvraCharacter,
  PrimaryButton,
  MessageBubble,
  ProgressBar,
  SelectionCard,
} from '../components/UIComponents';
import { useAssessment } from '../utils/AssessmentContext';

const PERIOD_PATTERNS = [
  { id: 'regular', label: 'Regular' },
  { id: 'irregular', label: 'Irregular' },
  { id: 'occasional_skips', label: 'Occasional Skips' },
  { id: 'no_periods', label: "I don't get periods" },
];

const BIRTH_CONTROL_OPTIONS = [
  { id: 'hormonal_pills', label: 'Hormonal Birth Control Pills' },
  { id: 'hormonal_iud', label: 'Hormonal IUD' },
  { id: 'copper_iud', label: 'Copper IUD (non-hormonal)' },
  { id: 'none', label: 'None' },
];

export default function PeriodPatternScreen({ navigation }) {
  const { assessmentData, updateSection } = useAssessment();
  const [selectedPattern, setSelectedPattern] = useState(
    assessmentData.period_pattern?.period_pattern || null
  );
  const [selectedBirthControl, setSelectedBirthControl] = useState(() => {
    const bc = assessmentData.period_pattern?.birth_control;
    if (!bc) return [];
    return Array.isArray(bc) ? bc : [bc];
  });
  const [notSure, setNotSure] = useState(false);

  const toggleBirthControl = (id) => {
    // Single-select behavior; selecting one replaces previous.
    // 'None' behaves as clear selection.
    if (id === 'none') {
      setSelectedBirthControl([]);
      return;
    }
    setSelectedBirthControl([id]);
  };

  const handleContinue = () => {
    // Backend expects birth_control as a single string, not an array
    // If multiple selected, use the first one; if none, use 'none'
    const birthControlValue = selectedBirthControl.length > 0 
      ? selectedBirthControl[0] 
      : 'none';
    
    updateSection('period_pattern', {
      period_pattern: notSure ? 'not_sure' : selectedPattern,
      birth_control: birthControlValue,
    });
    navigation.navigate('CycleDetails');
  };

  return (
    <LinearGradient colors={['#F5E6F9', '#E8D4F4']} style={styles.container}>
      <SafeAreaView style={{flex:1}}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Progress Bar */}
  <ProgressBar progress={2} steps={8} />

        {/* Top Section */}
        <View style={styles.topSection}>
          <AuvraCharacter expression="happy" size={120} />
          <MessageBubble text="How would you describe your periods? 🩸" />
        </View>

        {/* Period Pattern Selection */}
        <View style={styles.optionsContainer}>
          {PERIOD_PATTERNS.map((pattern) => (
            <SelectionCard
              key={pattern.id}
              title={pattern.label}
              selected={selectedPattern === pattern.id && !notSure}
              onPress={() => {
                setSelectedPattern(pattern.id);
                setNotSure(false);
              }}
            />
          ))}
        </View>

        {/* Not Sure Option */}
        <TouchableOpacity
          style={styles.notSureButton}
          onPress={() => {
            setNotSure(!notSure);
            if (!notSure) setSelectedPattern(null);
          }}
        >
          <Text style={[styles.notSureText, notSure && styles.notSureTextActive]}>
            I'm not sure
          </Text>
        </TouchableOpacity>

        {/* Birth Control Section */}
        <View style={styles.birthControlSection}>
          <Text style={styles.sectionTitle}>Also let me know if you use... (choose one)</Text>
          {BIRTH_CONTROL_OPTIONS.map((option) => (
            <SelectionCard
              key={option.id}
              title={option.label}
              selected={option.id === 'none' ? selectedBirthControl.length === 0 : selectedBirthControl.includes(option.id)}
              onPress={() => toggleBirthControl(option.id)}
            />
          ))}
        </View>
      </ScrollView>

      {/* Bottom Button */}
      <View style={styles.bottomContainer}>
        <PrimaryButton
          title="Continue"
          onPress={handleContinue}
          disabled={!selectedPattern && !notSure}
        />
      </View>
      </SafeAreaView>
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
  optionsContainer: {
    gap: 12,
    marginBottom: 8,
  },
  notSureButton: {
    alignSelf: 'flex-end',
    paddingVertical: 8,
    paddingHorizontal: 4,
    marginBottom: 32,
  },
  notSureText: {
    fontSize: 14,
    color: '#999',
    textDecorationLine: 'underline',
  },
  notSureTextActive: {
    color: '#B565A7',
    fontWeight: '600',
  },
  birthControlSection: {
    gap: 12,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666',
    marginBottom: 8,
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
