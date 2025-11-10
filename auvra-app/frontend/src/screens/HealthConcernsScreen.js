import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
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

const HEALTH_CONCERNS = {
  period: {
    title: '🩸 Period concerns',
    options: [
      'Irregular Periods',
      'Painful Periods',
      'Light periods / Spotting',
      'Heavy periods',
    ],
  },
  body: {
    title: '⚠️ Body concerns',
    options: [
      'Bloating',
      'Hot Flashes',
      'Nausea',
      'Difficulty losing weight / stubborn belly fat',
      'Recent weight gain',
      'Menstrual headaches',
    ],
  },
  skin_hair: {
    title: '👩 Skin and hair concerns',
    options: [
      'Hirsutism (hair growth on chin, nipples etc)',
      'Thinning of hair',
      'Adult Acne',
    ],
  },
  mental: {
    title: '🧠 Mental health concerns',
    options: ['Mood swings', 'Stress', 'Fatigue'],
  },
};

// NOTE: Raw human-readable labels are stored. Token mapping performed later during submission.

export default function HealthConcernsScreen({ navigation }) {
  const { assessmentData, updateSection } = useAssessment();
  
  const [selectedConcerns, setSelectedConcerns] = useState({
    period: assessmentData.health_concerns?.period || [],
    body: assessmentData.health_concerns?.body || [],
    skin_hair: assessmentData.health_concerns?.skin_hair || [],
    mental: assessmentData.health_concerns?.mental || [],
  });
  
  const [othersText, setOthersText] = useState(
    assessmentData.health_concerns?.others || ''
  );

  // Legacy compatibility: some hot-reload states may still reference setNoneSelected.
  // Provide a harmless no-op to avoid transient ReferenceErrors after code removal.
  const setNoneSelected = () => {}; // NO-OP safeguard

  const toggleConcern = (category, concern) => {
    setSelectedConcerns((prev) => ({
      ...prev,
      [category]: prev[category].includes(concern)
        ? prev[category].filter((item) => item !== concern)
        : [...prev[category], concern],
    }));
  };

  // Removed 'None of these' option to reduce confusion. User can simply leave section empty.

  const getTotalSelected = () => {
    return Object.values(selectedConcerns).reduce(
      (sum, arr) => sum + arr.length,
      0
    );
  };

  const handleContinue = () => {
    updateSection('health_concerns', {
      ...selectedConcerns,
      others: othersText.trim(),
      none: false,
    });
    
    navigation.navigate('TopConcern');
  };

  return (
    <LinearGradient colors={['#F5E6F9', '#E8D4F4']} style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Progress Bar */}
  <ProgressBar progress={4} steps={8} />

        {/* Top Section */}
        <View style={styles.topSection}>
          <AuvraCharacter expression="concerned" size={120} />
          <MessageBubble text="What concerns have been worrying you down?" />
        </View>

        {/* Health Concerns Categories */}
        {Object.entries(HEALTH_CONCERNS).map(([category, data]) => (
          <View key={category} style={styles.categorySection}>
            <Text style={styles.categoryTitle}>{data.title}</Text>
            <View style={styles.optionsGrid}>
              {data.options.map((option) => (
                <SelectionCard
                  key={option}
                  title={option}
                  selected={selectedConcerns[category].includes(option)}
                  onPress={() => toggleConcern(category, option)}
                  compact={data.options.length > 3}
                />
              ))}
            </View>
          </View>
        ))}

        {/* Other Concerns */}
        <View style={styles.categorySection}>
          <Text style={styles.categoryTitle}>Other concerns</Text>
          
          <TextInput
            style={[styles.othersInput]}
            placeholder="Others (please specify)"
            placeholderTextColor="#C4C4C4"
            value={othersText}
            onChangeText={setOthersText}
            multiline
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
    marginBottom: 24,
  },
  categorySection: {
    marginBottom: 24,
  },
  categoryTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#333',
    marginBottom: 12,
  },
  optionsGrid: {
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
