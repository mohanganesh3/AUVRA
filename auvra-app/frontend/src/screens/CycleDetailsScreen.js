import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import DateTimePicker from '@react-native-community/datetimepicker';
import {
  AuvraCharacter,
  PrimaryButton,
  MessageBubble,
  ProgressBar,
  SelectionCard,
} from '../components/UIComponents';
import { useAssessment } from '../utils/AssessmentContext';

const CYCLE_LENGTH_OPTIONS = [
  { id: 'less_than_21', label: 'Less than 21 days', backendToken: '<21' },
  { id: '21_25', label: '21-25 days', backendToken: '21-25' },
  { id: '26_30', label: '26-30 days', backendToken: '26-30' },
  { id: '31_35', label: '31-35 days', backendToken: '31-35' },
  { id: '35_plus', label: '35+ days', backendToken: '35+' },
];

export default function CycleDetailsScreen({ navigation }) {
  const { assessmentData, updateSection } = useAssessment();
  
  const [lastPeriodDate, setLastPeriodDate] = useState(
    assessmentData.cycle_details?.last_period_date
      ? new Date(assessmentData.cycle_details.last_period_date)
      : new Date()
  );
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [dateNotSure, setDateNotSure] = useState(false);
  
  const [cycleLength, setCycleLength] = useState(
    assessmentData.cycle_details?.average_cycle_length || null
  );
  const [lengthNotSure, setLengthNotSure] = useState(false);

  const formatDate = (date) => {
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const year = date.getFullYear();
    return `${month} / ${day} / ${year}`;
  };

  const onDateChange = (event, selectedDate) => {
    setShowDatePicker(Platform.OS === 'ios');
    if (selectedDate) {
      setLastPeriodDate(selectedDate);
      setDateNotSure(false);
    }
  };

  const handleContinue = () => {
    // Transform cycle length to backend format
    const cycleLengthValue = lengthNotSure 
      ? 'not_sure' 
      : CYCLE_LENGTH_OPTIONS.find(opt => opt.id === cycleLength)?.backendToken || cycleLength;
    
    updateSection('cycle_details', {
      last_period_date: dateNotSure ? null : lastPeriodDate.toISOString().split('T')[0],
      date_not_sure: dateNotSure,
      cycle_length: cycleLengthValue,
    });
    navigation.navigate('HealthConcerns');
  };

  return (
    <LinearGradient colors={['#F5E6F9', '#E8D4F4']} style={styles.container}>
      <SafeAreaView style={{flex:1}}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Progress Bar */}
  <ProgressBar progress={3} steps={8} />

        {/* Top Section */}
        <View style={styles.topSection}>
          <AuvraCharacter expression="happy" size={120} />
          <MessageBubble text="Tell me more about your periods?" />
        </View>

        {/* Last Period Date */}
        <View style={styles.section}>
          <Text style={styles.questionText}>When did your last period start?</Text>
          <TouchableOpacity
            style={styles.dateInput}
            onPress={() => !dateNotSure && setShowDatePicker(true)}
            disabled={dateNotSure}
          >
            <Text style={[styles.dateText, dateNotSure && styles.dateTextDisabled]}>
              {dateNotSure ? 'Not sure' : formatDate(lastPeriodDate)}
            </Text>
            <View style={styles.calendarIcon}>
              <Text style={styles.calendarEmoji}>📅</Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.notSureButton}
            onPress={() => setDateNotSure(!dateNotSure)}
          >
            <Text style={[styles.notSureText, dateNotSure && styles.notSureTextActive]}>
              I'm not sure
            </Text>
          </TouchableOpacity>

          {showDatePicker && (
            <DateTimePicker
              value={lastPeriodDate}
              mode="date"
              display={Platform.OS === 'ios' ? 'spinner' : 'default'}
              onChange={onDateChange}
              maximumDate={new Date()}
              minimumDate={new Date(Date.now() - 120 * 24 * 60 * 60 * 1000)} // 120 days ago
            />
          )}
        </View>

        {/* Cycle Length */}
        <View style={styles.section}>
          <Text style={styles.questionText}>What is your average cycle length?</Text>
          <View style={styles.cycleLengthGrid}>
            {CYCLE_LENGTH_OPTIONS.map((option) => (
              <SelectionCard
                key={option.id}
                title={option.label}
                selected={cycleLength === option.id && !lengthNotSure}
                onPress={() => {
                  setCycleLength(option.id);
                  setLengthNotSure(false);
                }}
                compact
              />
            ))}
          </View>

          <TouchableOpacity
            style={styles.notSureButton}
            onPress={() => {
              setLengthNotSure(!lengthNotSure);
              if (!lengthNotSure) setCycleLength(null);
            }}
          >
            <Text style={[styles.notSureText, lengthNotSure && styles.notSureTextActive]}>
              I'm not sure
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>

      {/* Bottom Button */}
      <View style={styles.bottomContainer}>
        <PrimaryButton
          title="Continue"
          onPress={handleContinue}
          disabled={(!lastPeriodDate && !dateNotSure) || (!cycleLength && !lengthNotSure)}
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
  section: {
    marginBottom: 32,
  },
  questionText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  dateInput: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E8E8E8',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  dateText: {
    fontSize: 16,
    color: '#333',
  },
  dateTextDisabled: {
    color: '#C4C4C4',
  },
  calendarIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#F5F5F5',
    justifyContent: 'center',
    alignItems: 'center',
  },
  calendarEmoji: {
    fontSize: 18,
  },
  cycleLengthGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  notSureButton: {
    alignSelf: 'flex-end',
    paddingVertical: 8,
    paddingHorizontal: 4,
    marginTop: 8,
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
