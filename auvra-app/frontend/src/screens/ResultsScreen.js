import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { AuvraCharacter, PrimaryButton } from '../components/UIComponents';
import { useAssessment } from '../utils/AssessmentContext';

// Helper to truncate very long factor strings for UI cleanliness
function truncateFactor(factor) {
  if (!factor) return '';
  const max = 110; // character cap per line
  return factor.length > max ? factor.slice(0, max - 3) + '...' : factor;
}

// Hormone icons mapping
const HORMONE_ICONS = {
  Estrogen: '🌸',
  Progesterone: '🌺',
  Androgens: '⭐',
  Testosterone: '⭐',
  Insulin: '🍬',
  Cortisol: '😰',
  Thyroid: '🦋',
};

// Hormone colors
const HORMONE_COLORS = {
  Estrogen: '#FFB6C1',
  Progesterone: '#FF69B4',
  Androgens: '#FFD700',
  Testosterone: '#FFD700',
  Insulin: '#87CEEB',
  Cortisol: '#FFA07A',
  Thyroid: '#9370DB',
};

// Backend key → display name
const DISPLAY_NAME = {
  estrogen: 'Estrogen',
  progesterone: 'Progesterone',
  androgens: 'Testosterone',
  insulin: 'Insulin',
  cortisol: 'Cortisol',
  thyroid: 'Thyroid',
};

export default function ResultsScreen({ navigation }) {
  const { result, clearAssessment } = useAssessment();

  if (!result) {
    return (
      <LinearGradient colors={['#FFFFFF', '#F5E6F9']} style={styles.container}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>No results available</Text>
          <PrimaryButton
            title="Start New Assessment"
            onPress={() => {
              clearAssessment();
              navigation.navigate('Welcome');
            }}
          />
        </View>
      </LinearGradient>
    );
  }

  const { primary_imbalance, secondary_imbalances, confidence } = result;

  const handleStartOver = () => {
    Alert.alert(
      'Start New Assessment',
      'This will clear your current results. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Yes',
          onPress: () => {
            clearAssessment();
            navigation.navigate('Welcome');
          },
        },
      ]
    );
  };

  return (
    <LinearGradient colors={['#FFFFFF', '#F5E6F9']} style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <AuvraCharacter expression="happy" size={100} />
          <Text style={styles.headerTitle}>
            Some of your hormone{'\n'}buddies are feeling off
          </Text>
        </View>

        {/* Primary Hormone */}
        {primary_imbalance && (
          <HormoneCard
            hormone={primary_imbalance.hormone}
            direction={primary_imbalance.direction}
            explanation={primary_imbalance.explanation}
            contributingFactors={primary_imbalance.contributing_factors}
            recommendations={primary_imbalance.recommendations}
            isPrimary={true}
          />
        )}

        {/* Secondary Hormones */}
        {Array.isArray(secondary_imbalances) && secondary_imbalances.map((h, idx) => (
          <HormoneCard
            key={h.hormone + idx}
            hormone={h.hormone}
            direction={h.direction}
            explanation={h.explanation}
            contributingFactors={h.contributing_factors}
            recommendations={h.recommendations}
            isPrimary={false}
          />
        ))}

        {/* Confidence Level */}
        <View style={styles.confidenceContainer}>
          <Text style={styles.confidenceLabel}>Confidence Level</Text>
          <View style={[styles.confidenceBadge, getConfidenceStyle(confidence.level)]}>
            <Text style={styles.confidenceText}>{confidence.level.toUpperCase()}</Text>
          </View>
          {confidence.calculation_breakdown && confidence.calculation_breakdown.length > 0 && (
            <View style={{ marginTop: 8 }}>
              {confidence.calculation_breakdown.slice(0,5).map((f, i) => (
                <Text key={i} style={styles.confidenceFactors}>• {f.factor} ({f.points >= 0 ? '+' : ''}{f.points})</Text>
              ))}
            </View>
          )}
        </View>

        {/* Lab Upload CTA */}
        <TouchableOpacity style={styles.labUploadCard}>
          <View style={styles.labUploadContent}>
            <View style={styles.labUploadText}>
              <Text style={styles.labUploadTitle}>Upload your blood report →</Text>
              <Text style={styles.labUploadSubtitle}>For more precise analysis</Text>
            </View>
            <View style={styles.labIcon}>
              <Text style={styles.labIconText}>📄</Text>
              <Text style={styles.labIconBlood}>🩸</Text>
            </View>
          </View>
        </TouchableOpacity>

        {/* Actions */}
        <View style={styles.actionsContainer}>
          <PrimaryButton
            title="Start New Assessment"
            onPress={handleStartOver}
          />
        </View>
      </ScrollView>
    </LinearGradient>
  );
}

// Hormone Card Component
function HormoneCard({ hormone, direction, explanation, contributingFactors = [], recommendations, isPrimary }) {
  const [isEvidenceExpanded, setIsEvidenceExpanded] = useState(false);
  const [isRecommendationsExpanded, setIsRecommendationsExpanded] = useState(false);
  
  const name = DISPLAY_NAME[hormone] || (hormone?.charAt(0).toUpperCase() + hormone?.slice(1)) || 'Hormone';
  const icon = HORMONE_ICONS[name] || '🔬';
  const color = HORMONE_COLORS[name] || '#B565A7';

  return (
    <View style={[styles.hormoneCard, { backgroundColor: color + '15' }]}>
      {/* Header */}
      <View style={styles.hormoneHeader}>
        <View style={[styles.hormoneIcon, { backgroundColor: color + '30' }]}>
          <Text style={styles.hormoneIconText}>{icon}</Text>
        </View>
        <View style={styles.hormoneHeaderText}>
          <Text style={styles.hormoneName}>{name}</Text>
          <Text style={[styles.hormoneDirection, { color }]}>
            {direction === 'high' ? '▲ Higher' : '▼ Lower'} levels may be contributing
          </Text>
        </View>
      </View>

      {/* Contributing Factors / Reasons */}
      {Array.isArray(contributingFactors) && contributingFactors.length > 0 && (
        <View style={styles.factorsContainer}>
          <Text style={styles.factorsTitle}>Based on:</Text>
          {contributingFactors.slice(0,5).map((f,i) => (
            <Text key={i} style={styles.factorItem}>• {truncateFactor(f)}</Text>
          ))}
          {contributingFactors.length > 5 && (
            <Text style={styles.factorItem}>• ...and {contributingFactors.length - 5} more indicators</Text>
          )}
        </View>
      )}

      {/* Explanation - Expandable */}
      {explanation && (
        <TouchableOpacity 
          style={styles.explanationContainer}
          onPress={() => setIsEvidenceExpanded(!isEvidenceExpanded)}
          activeOpacity={0.7}
        >
          <View style={styles.explanationHeader}>
            <Text style={styles.explanationTitle}>
              {explanation.includes('**Supporting Evidence:**') ? 'Supporting Evidence' : 'Details'}
            </Text>
            <Text style={styles.expandIcon}>{isEvidenceExpanded ? '▼' : '▶'}</Text>
          </View>
          
          <Text 
            style={styles.hormoneExplanation} 
            numberOfLines={isEvidenceExpanded ? undefined : 3}
          >
            {explanation.replace(/\*\*/g, '')}
          </Text>
          
          {!isEvidenceExpanded && (
            <Text style={styles.tapToExpand}>Tap to see more...</Text>
          )}
        </TouchableOpacity>
      )}

      {/* Recommendations Preview - Also Expandable */}
      {recommendations && (
        <TouchableOpacity 
          style={styles.recommendationsPreview}
          onPress={() => setIsRecommendationsExpanded(!isRecommendationsExpanded)}
          activeOpacity={0.7}
        >
          <View style={styles.recommendationsHeader}>
            <Text style={styles.recommendationsTitle}>Recommended Actions:</Text>
            <Text style={styles.expandIcon}>{isRecommendationsExpanded ? '▼' : '▶'}</Text>
          </View>
          
          {isRecommendationsExpanded ? (
            <>
              {recommendations.testing && recommendations.testing.length > 0 && (
                <View style={styles.recommendationSection}>
                  <Text style={styles.recommendationSectionTitle}>🔬 Testing:</Text>
                  {recommendations.testing.map((item, i) => (
                    <Text key={i} style={styles.recommendationItem}>• {item}</Text>
                  ))}
                </View>
              )}
              
              {recommendations.lifestyle && recommendations.lifestyle.length > 0 && (
                <View style={styles.recommendationSection}>
                  <Text style={styles.recommendationSectionTitle}>🌱 Lifestyle:</Text>
                  {recommendations.lifestyle.map((item, i) => (
                    <Text key={i} style={styles.recommendationItem}>• {item}</Text>
                  ))}
                </View>
              )}
              
              {recommendations.supplements && recommendations.supplements.length > 0 && (
                <View style={styles.recommendationSection}>
                  <Text style={styles.recommendationSectionTitle}>💊 Supplements:</Text>
                  {recommendations.supplements.map((item, i) => (
                    <Text key={i} style={styles.recommendationItem}>• {item}</Text>
                  ))}
                </View>
              )}
            </>
          ) : (
            <>
              {recommendations.testing && recommendations.testing.length > 0 && (
                <Text style={styles.recommendationItem}>
                  • {recommendations.testing[0]}
                </Text>
              )}
              {recommendations.lifestyle && recommendations.lifestyle.length > 0 && (
                <Text style={styles.recommendationItem}>
                  • {recommendations.lifestyle[0]}
                </Text>
              )}
              <Text style={styles.tapToExpand}>Tap to see all recommendations...</Text>
            </>
          )}
        </TouchableOpacity>
      )}
    </View>
  );
}

// Helper function for confidence styling
function getConfidenceStyle(level) {
  switch (level.toLowerCase()) {
    case 'high':
      return { backgroundColor: '#4CAF50' };
    case 'medium':
      return { backgroundColor: '#FF9800' };
    case 'low':
      return { backgroundColor: '#F44336' };
    default:
      return { backgroundColor: '#999' };
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 60,
    paddingBottom: 40,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  errorText: {
    fontSize: 18,
    color: '#666',
    marginBottom: 24,
  },
  header: {
    alignItems: 'center',
    marginBottom: 32,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#B565A7',
    textAlign: 'center',
    marginTop: 16,
    lineHeight: 32,
  },
  hormoneCard: {
    borderRadius: 20,
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#E8E8E8',
  },
  hormoneHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  hormoneIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  hormoneIconText: {
    fontSize: 28,
  },
  hormoneHeaderText: {
    flex: 1,
  },
  hormoneName: {
    fontSize: 20,
    fontWeight: '700',
    color: '#333',
    marginBottom: 4,
  },
  hormoneDirection: {
    fontSize: 14,
    fontWeight: '600',
  },
  hormoneExplanation: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 12,
  },
  explanationContainer: {
    marginTop: 8,
    marginBottom: 8,
  },
  explanationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  explanationTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  expandIcon: {
    fontSize: 12,
    color: '#B565A7',
    fontWeight: '600',
  },
  tapToExpand: {
    fontSize: 12,
    color: '#B565A7',
    fontStyle: 'italic',
    marginTop: 4,
  },
  factorsContainer: {
    marginBottom: 10,
  },
  factorsTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  factorItem: {
    fontSize: 12,
    color: '#555',
    lineHeight: 18,
  },
  recommendationsPreview: {
    marginTop: 8,
  },
  recommendationsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  recommendationsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  recommendationSection: {
    marginTop: 8,
  },
  recommendationSectionTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: '#444',
    marginBottom: 4,
  },
  recommendationItem: {
    fontSize: 13,
    color: '#555',
    lineHeight: 20,
    marginBottom: 2,
  },
  confidenceContainer: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#E8E8E8',
  },
  confidenceLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  confidenceBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 12,
    marginBottom: 8,
  },
  confidenceText: {
    fontSize: 14,
    fontWeight: '700',
    color: 'white',
  },
  confidenceFactors: {
    fontSize: 12,
    color: '#666',
    fontStyle: 'italic',
  },
  labUploadCard: {
    backgroundColor: '#FFE5E5',
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: '#FFD0D0',
  },
  labUploadContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  labUploadText: {
    flex: 1,
  },
  labUploadTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#D84848',
    marginBottom: 4,
  },
  labUploadSubtitle: {
    fontSize: 13,
    color: '#999',
  },
  labIcon: {
    position: 'relative',
    width: 56,
    height: 56,
    justifyContent: 'center',
    alignItems: 'center',
  },
  labIconText: {
    fontSize: 36,
  },
  labIconBlood: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    fontSize: 20,
  },
  actionsContainer: {
    marginTop: 8,
  },
});
