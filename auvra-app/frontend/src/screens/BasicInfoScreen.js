import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  TextInput,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import {
  AuvraCharacter,
  PrimaryButton,
  MessageBubble,
  ProgressBar,
} from '../components/UIComponents';
import { useAssessment } from '../utils/AssessmentContext';

export default function BasicInfoScreen({ navigation }) {
  const { assessmentData, updateSection } = useAssessment();
  const [name, setName] = useState(assessmentData.basic_info?.name || '');
  const [age, setAge] = useState(assessmentData.basic_info?.age || '');

  const handleContinue = () => {
    // Validation
    if (!name.trim()) {
      Alert.alert('Required', 'Please enter your name');
      return;
    }

    const ageNum = parseInt(age);
    if (!age || isNaN(ageNum) || ageNum < 18 || ageNum > 40) {
      Alert.alert('Invalid Age', 'Please enter a valid age between 18 and 40');
      return;
    }

    // Save to context
    updateSection('basic_info', { name: name.trim(), age: ageNum });
    
    // Navigate to next screen
    navigation.navigate('PeriodPattern');
  };

  return (
    <LinearGradient colors={['#F5E6F9', '#E8D4F4']} style={styles.container}>
      <SafeAreaView style={{flex:1}}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardAvoid}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          {/* Progress Bar */}
          <ProgressBar progress={1} steps={8} />

          {/* Top Section with Character */}
          <View style={styles.topSection}>
            <AuvraCharacter expression="happy" size={120} />
            <MessageBubble text="Tell me about yourself?" />
          </View>

          {/* Form Section */}
          <View style={styles.formSection}>
            {/* Name Input */}
            <View style={styles.inputGroup}>
              <Text style={styles.label}>👋 What should I call you?</Text>
              <TextInput
                style={styles.input}
                placeholder="Your Name"
                placeholderTextColor="#C4C4C4"
                value={name}
                onChangeText={setName}
                autoCapitalize="words"
                returnKeyType="next"
              />
            </View>

            {/* Age Input */}
            <View style={styles.inputGroup}>
              <Text style={styles.label}>😊 How young are you?</Text>
              <TextInput
                style={styles.input}
                placeholder="Your Age"
                placeholderTextColor="#C4C4C4"
                value={age}
                onChangeText={setAge}
                keyboardType="number-pad"
                maxLength={2}
                returnKeyType="done"
                onSubmitEditing={handleContinue}
              />
            </View>
          </View>
        </ScrollView>

        {/* Bottom Button */}
        <View style={styles.bottomContainer}>
          <PrimaryButton
            title="Continue"
            onPress={handleContinue}
            disabled={!name.trim() || !age}
          />
        </View>
      </KeyboardAvoidingView>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  keyboardAvoid: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 60,
    paddingBottom: 100,
  },
  topSection: {
    alignItems: 'center',
    marginBottom: 40,
  },
  formSection: {
    gap: 32,
  },
  inputGroup: {
    gap: 12,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginLeft: 4,
  },
  input: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    fontSize: 16,
    color: '#333',
    borderWidth: 1,
    borderColor: '#E8E8E8',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
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
