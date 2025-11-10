import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { AuvraCharacter, MessageBubble, ProgressBar } from '../components/UIComponents';
import { useAssessment } from '../utils/AssessmentContext';

export default function LabResultsScreen({ navigation }) {
  const { assessmentData, updateSection } = useAssessment();

  // State for all lab values
  const [labValues, setLabValues] = useState({
    // Androgen Panel
    total_testosterone: assessmentData.lab_results?.total_testosterone || '',
    free_testosterone: assessmentData.lab_results?.free_testosterone || '',
    dhea_s: assessmentData.lab_results?.dhea_s || '',
    
    // LH/FSH
    lh: assessmentData.lab_results?.lh || '',
    fsh: assessmentData.lab_results?.fsh || '',
    
    // Thyroid Panel
    tsh: assessmentData.lab_results?.tsh || '',
    free_t3: assessmentData.lab_results?.free_t3 || '',
    free_t4: assessmentData.lab_results?.free_t4 || '',
    
    // Insulin/Glucose
    fasting_insulin: assessmentData.lab_results?.fasting_insulin || '',
    hba1c: assessmentData.lab_results?.hba1c || '',
    fasting_glucose: assessmentData.lab_results?.fasting_glucose || '',
    
    // Cortisol
    am_cortisol: assessmentData.lab_results?.am_cortisol || '',
    
    // Sex Hormones
    estradiol: assessmentData.lab_results?.estradiol || '',
    progesterone: assessmentData.lab_results?.progesterone || '',
    
    // SHBG
    shbg: assessmentData.lab_results?.shbg || '',
  });

  const handleValueChange = (field, value) => {
    // Only allow numbers and decimal point
    const sanitized = value.replace(/[^0-9.]/g, '');
    setLabValues({ ...labValues, [field]: sanitized });
  };

  const validateAndProceed = () => {
    // Check if user has entered ANY lab values
    const hasValues = Object.values(labValues).some(val => val !== '');

    if (!hasValues) {
      // User wants to skip - that's fine
      Alert.alert(
        'Skip Lab Results?',
        'Lab results help improve accuracy. You can add them later in your profile.',
        [
          {
            text: 'Add Labs',
            style: 'cancel',
          },
          {
            text: 'Skip for Now',
            onPress: () => {
              updateSection('lab_results', null);
              navigation.navigate('Analyzing');
            },
          },
        ]
      );
      return;
    }

    // Convert string values to numbers (or null if empty)
    const processedLabs = {};
    Object.keys(labValues).forEach(key => {
      const val = labValues[key];
      processedLabs[key] = val !== '' ? parseFloat(val) : null;
    });

    // Validate entered values against normal ranges
    const warnings = validateLabRanges(processedLabs);

    if (warnings.length > 0) {
      Alert.alert(
        'Review Lab Values',
        `Some values are outside normal ranges:\n\n${warnings.join('\n')}\n\nPlease double-check your entries.`,
        [
          {
            text: 'Review',
            style: 'cancel',
          },
          {
            text: 'Continue Anyway',
            onPress: () => {
              updateSection('lab_results', processedLabs);
              navigation.navigate('Analyzing');
            },
          },
        ]
      );
    } else {
      // All good - proceed
      updateSection('lab_results', processedLabs);
      navigation.navigate('Analyzing');
    }
  };

  const validateLabRanges = (labs) => {
    const warnings = [];

    // Based on Section 6.1 table
    if (labs.total_testosterone !== null) {
      if (labs.total_testosterone > 100) {
        warnings.push('• Total Testosterone is very high (normal: <50 ng/dL)');
      }
    }

    if (labs.free_testosterone !== null) {
      if (labs.free_testosterone > 5) {
        warnings.push('• Free Testosterone is very high (normal: <2.0 pg/mL)');
      }
    }

    if (labs.dhea_s !== null) {
      if (labs.dhea_s > 600 || labs.dhea_s < 20) {
        warnings.push('• DHEA-S is outside normal range (35-430 µg/dL)');
      }
    }

    if (labs.tsh !== null) {
      if (labs.tsh > 10) {
        warnings.push('• TSH is very elevated (normal: 0.4-4.5 mIU/L) - seek medical attention');
      } else if (labs.tsh < 0.1) {
        warnings.push('• TSH is very low - possible hyperthyroidism');
      }
    }

    if (labs.fasting_insulin !== null) {
      if (labs.fasting_insulin > 30) {
        warnings.push('• Fasting Insulin is very high (normal: 2-20 µIU/mL)');
      }
    }

    if (labs.hba1c !== null) {
      if (labs.hba1c > 6.5) {
        warnings.push('• HbA1c indicates diabetes range (>6.5%) - seek medical attention');
      }
    }

    if (labs.fasting_glucose !== null) {
      if (labs.fasting_glucose > 126) {
        warnings.push('• Fasting Glucose indicates diabetes (>126 mg/dL) - seek medical attention');
      }
    }

    return warnings;
  };

  const skipLabs = () => {
    Alert.alert(
      'Skip Lab Results?',
      'Your assessment will be based on symptoms and diagnoses only. You can add lab results later.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Skip',
          onPress: () => {
            updateSection('lab_results', null);
            navigation.navigate('Analyzing');
          },
        },
      ]
    );
  };

  return (
    <LinearGradient colors={['#FFFFFF', '#F5E6F9']} style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        {/* Top bar with progress and Skip for now */}
        <View style={styles.topBar}>
          <ProgressBar progress={7} steps={8} />
          <TouchableOpacity onPress={skipLabs} style={styles.topSkipButton}>
            <Text style={styles.topSkipText}>Skip for now</Text>
          </TouchableOpacity>
        </View>

        <ScrollView 
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          <AuvraCharacter expression="happy" size={120} />

          <MessageBubble text="Do you have any recent blood test results? (Optional)" />

          <Text style={styles.subtitle}>
            Lab results help improve accuracy. Enter any values you have:
          </Text>

          {/* Androgen Panel */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>🔬 Androgen Panel</Text>
            
            <LabInput
              label="Total Testosterone"
              unit="ng/dL"
              normalRange="<50"
              value={labValues.total_testosterone}
              onChangeText={(val) => handleValueChange('total_testosterone', val)}
              placeholder="e.g., 45"
            />
            
            <LabInput
              label="Free Testosterone"
              unit="pg/mL"
              normalRange="<2.0"
              value={labValues.free_testosterone}
              onChangeText={(val) => handleValueChange('free_testosterone', val)}
              placeholder="e.g., 1.5"
            />
            
            <LabInput
              label="DHEA-S"
              unit="µg/dL"
              normalRange="35-430"
              value={labValues.dhea_s}
              onChangeText={(val) => handleValueChange('dhea_s', val)}
              placeholder="e.g., 250"
            />
          </View>

          {/* LH/FSH */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>🧬 LH & FSH</Text>
            
            <LabInput
              label="LH (Luteinizing Hormone)"
              unit="mIU/mL"
              normalRange="2-20"
              value={labValues.lh}
              onChangeText={(val) => handleValueChange('lh', val)}
              placeholder="e.g., 8"
            />
            
            <LabInput
              label="FSH (Follicle Stimulating)"
              unit="mIU/mL"
              normalRange="2-10"
              value={labValues.fsh}
              onChangeText={(val) => handleValueChange('fsh', val)}
              placeholder="e.g., 5"
            />
          </View>

          {/* Thyroid Panel */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>🦋 Thyroid Panel</Text>
            
            <LabInput
              label="TSH"
              unit="mIU/L"
              normalRange="0.4-4.5"
              optimalRange="<2.5"
              value={labValues.tsh}
              onChangeText={(val) => handleValueChange('tsh', val)}
              placeholder="e.g., 2.0"
            />
            
            <LabInput
              label="Free T3"
              unit="pg/mL"
              normalRange="2.3-4.2"
              value={labValues.free_t3}
              onChangeText={(val) => handleValueChange('free_t3', val)}
              placeholder="e.g., 3.0"
            />
            
            <LabInput
              label="Free T4"
              unit="ng/dL"
              normalRange="0.8-1.8"
              value={labValues.free_t4}
              onChangeText={(val) => handleValueChange('free_t4', val)}
              placeholder="e.g., 1.2"
            />
          </View>

          {/* Insulin/Glucose */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>📊 Insulin & Glucose</Text>
            
            <LabInput
              label="Fasting Insulin"
              unit="µIU/mL"
              normalRange="2-20"
              optimalRange="<6"
              value={labValues.fasting_insulin}
              onChangeText={(val) => handleValueChange('fasting_insulin', val)}
              placeholder="e.g., 5"
            />
            
            <LabInput
              label="HbA1c"
              unit="%"
              normalRange="<5.7"
              value={labValues.hba1c}
              onChangeText={(val) => handleValueChange('hba1c', val)}
              placeholder="e.g., 5.2"
            />
            
            <LabInput
              label="Fasting Glucose"
              unit="mg/dL"
              normalRange="70-99"
              value={labValues.fasting_glucose}
              onChangeText={(val) => handleValueChange('fasting_glucose', val)}
              placeholder="e.g., 85"
            />
          </View>

          {/* Cortisol */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>⚡ Cortisol</Text>
            
            <LabInput
              label="AM Cortisol (morning)"
              unit="µg/dL"
              normalRange="6-23"
              value={labValues.am_cortisol}
              onChangeText={(val) => handleValueChange('am_cortisol', val)}
              placeholder="e.g., 12"
            />
          </View>

          {/* Sex Hormones */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>💕 Sex Hormones</Text>
            
            <LabInput
              label="Estradiol (E2)"
              unit="pg/mL"
              normalRange="30-100 (Day 3)"
              value={labValues.estradiol}
              onChangeText={(val) => handleValueChange('estradiol', val)}
              placeholder="e.g., 50"
              helper="Should be tested on Day 3-5 of cycle"
            />
            
            <LabInput
              label="Progesterone"
              unit="ng/mL"
              normalRange=">10 (Luteal)"
              value={labValues.progesterone}
              onChangeText={(val) => handleValueChange('progesterone', val)}
              placeholder="e.g., 12"
              helper="Should be tested on Day 19-22 of cycle"
            />
          </View>

          {/* SHBG */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>🔗 SHBG</Text>
            
            <LabInput
              label="SHBG"
              unit="nmol/L"
              normalRange="20-100"
              value={labValues.shbg}
              onChangeText={(val) => handleValueChange('shbg', val)}
              placeholder="e.g., 50"
            />
          </View>

          <View style={styles.buttonContainer}>
            <TouchableOpacity 
              style={styles.continueButton} 
              onPress={validateAndProceed}
            >
              <Text style={styles.continueButtonText}>Continue</Text>
            </TouchableOpacity>
          </View>

          <Text style={styles.footerNote}>
            💡 Tip: You can add more lab results later in your profile
          </Text>
        </ScrollView>
      </SafeAreaView>
    </LinearGradient>
  );
}

// Reusable Lab Input Component
function LabInput({ label, unit, normalRange, optimalRange, value, onChangeText, placeholder, helper }) {
  return (
    <View style={styles.labInputContainer}>
      <View style={styles.labHeader}>
        <Text style={styles.labLabel}>{label}</Text>
        <Text style={styles.labUnit}>{unit}</Text>
      </View>
      
      <TextInput
        style={styles.labInput}
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor="#999"
        keyboardType="decimal-pad"
        returnKeyType="done"
      />
      
      <View style={styles.rangeInfo}>
        <Text style={styles.rangeText}>
          Normal: {normalRange}
          {optimalRange && ` • Optimal: ${optimalRange}`}
        </Text>
      </View>
      
      {helper && (
        <Text style={styles.helperText}>ℹ️ {helper}</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
  },
  topBar: {
    paddingHorizontal: 16,
    paddingTop: 4,
  },
  topSkipButton: {
    alignSelf: 'flex-end',
    paddingVertical: 8,
    paddingHorizontal: 8,
  },
  topSkipText: {
    color: '#8B4E99',
    fontWeight: '600',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 24,
    paddingBottom: 40,
    paddingTop: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 24,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#B565A7',
    marginBottom: 16,
  },
  labInputContainer: {
    marginBottom: 20,
  },
  labHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  labLabel: {
    fontSize: 15,
    fontWeight: '600',
    color: '#333',
  },
  labUnit: {
    fontSize: 13,
    color: '#666',
    fontStyle: 'italic',
  },
  labInput: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    color: '#333',
    borderWidth: 2,
    borderColor: '#E5D4F1',
  },
  rangeInfo: {
    marginTop: 6,
  },
  rangeText: {
    fontSize: 12,
    color: '#888',
  },
  helperText: {
    fontSize: 12,
    color: '#B565A7',
    marginTop: 4,
    fontStyle: 'italic',
  },
  buttonContainer: {
    marginTop: 32,
  },
  continueButton: {
    width: '100%',
    backgroundColor: '#B565A7',
    borderRadius: 25,
    paddingVertical: 16,
    alignItems: 'center',
  },
  continueButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
  },
  footerNote: {
    textAlign: 'center',
    fontSize: 13,
    color: '#888',
    marginTop: 16,
    fontStyle: 'italic',
  },
});
