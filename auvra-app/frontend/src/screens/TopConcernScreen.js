import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
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

export default function TopConcernScreen({ navigation }) {
  const { assessmentData, updateSection } = useAssessment();
  const [selectedConcern, setSelectedConcern] = useState(
    assessmentData.top_concern || null
  );
  const [allConcerns, setAllConcerns] = useState([]);
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Gather all selected concerns from previous screen
    const concerns = [];
    const healthConcerns = assessmentData.health_concerns || {};
    
    console.log('[TopConcern] Health concerns data:', healthConcerns);
    
    ['period', 'body', 'skin_hair', 'mental'].forEach((category) => {
      if (healthConcerns[category] && healthConcerns[category].length > 0) {
        console.log(`[TopConcern] ${category}:`, healthConcerns[category]);
        concerns.push(...healthConcerns[category]);
      }
    });

    // Add "Others" text if provided
    if (healthConcerns.others && healthConcerns.others.trim()) {
      console.log('[TopConcern] Others text:', healthConcerns.others);
      concerns.push(`Other: ${healthConcerns.others.trim()}`);
    }

    console.log('[TopConcern] Total concerns found:', concerns.length, concerns);
    setAllConcerns(concerns);
    
    // Only auto-skip on FIRST load if truly no concerns were selected
    if (!isInitialized) {
      setIsInitialized(true);
      if (concerns.length === 0) {
        console.log('[TopConcern] No concerns selected, auto-skipping to Diagnosis');
        updateSection('top_concern', { top_concern: 'none' });
        navigation.navigate('Diagnosis');
      }
    }
  }, [assessmentData]);

  const handleContinue = () => {
    if (!selectedConcern) {
      Alert.alert('Required', 'Please select your top concern');
      return;
    }

    // Backend expects { top_concern: "string" }
    updateSection('top_concern', { top_concern: selectedConcern });
    navigation.navigate('Diagnosis');
  };

  return (
    <LinearGradient colors={['#F5E6F9', '#E8D4F4']} style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Progress Bar */}
  <ProgressBar progress={5} steps={8} />

        {/* Top Section */}
        <View style={styles.topSection}>
          <AuvraCharacter expression="concerned" size={120} />
          <MessageBubble text="Out of these, what is your top concern at the moment?" />
        </View>

        {/* All Concerns List */}
        <View style={styles.concernsContainer}>
          {allConcerns.map((concern, index) => (
            <SelectionCard
              key={`${concern}-${index}`}
              title={concern}
              selected={selectedConcern === concern}
              onPress={() => setSelectedConcern(concern)}
            />
          ))}
        </View>
      </ScrollView>

      {/* Bottom Button */}
      <View style={styles.bottomContainer}>
        <PrimaryButton
          title="Continue"
          onPress={handleContinue}
          disabled={!selectedConcern}
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
  concernsContainer: {
    gap: 12,
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
