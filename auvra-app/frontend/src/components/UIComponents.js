// Reusable UI Components
// Beautiful, consistent components matching the app design

import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  ActivityIndicator,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

const { width } = Dimensions.get('window');

// Auvra Character Component
export const AuvraCharacter = ({ expression = 'happy', size = 120 }) => {
  const expressions = {
    happy: '😊',
    concerned: '😟',
    thinking: '🤔',
    excited: '🎉',
  };

  return (
    <View style={[styles.characterContainer, { width: size, height: size }]}>
      <LinearGradient
        colors={['#E6D4F5', '#C9A5E0']}
        style={styles.characterGradient}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <Text style={{ fontSize: size * 0.5 }}>{expressions[expression] || '😊'}</Text>
      </LinearGradient>
    </View>
  );
};

// Primary Button
export const PrimaryButton = ({ title, onPress, disabled = false, loading = false }) => {
  return (
    <TouchableOpacity
      style={[styles.primaryButton, disabled && styles.buttonDisabled]}
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.8}
    >
      <LinearGradient
        colors={disabled ? ['#CCC', '#999'] : ['#B565A7', '#8B4E99']}
        style={styles.buttonGradient}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 0 }}
      >
        {loading ? (
          <ActivityIndicator color="#FFF" />
        ) : (
          <Text style={styles.buttonText}>{title}</Text>
        )}
      </LinearGradient>
    </TouchableOpacity>
  );
};

// Selection Card (for multiple choice)
// Selection Card Component
export function SelectionCard({ title, subtitle, selected, onPress, compact = false }) {
  return (
    <TouchableOpacity
      style={[
        styles.selectionCard,
        selected && styles.selectionCardSelected,
        compact && styles.selectionCardCompact,
      ]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.selectionCardContent}>
        <View style={styles.selectionCardText}>
          <Text
            style={[
              styles.selectionCardTitle,
              selected && styles.selectionCardTitleSelected,
              compact && styles.selectionCardTitleCompact,
            ]}
            numberOfLines={2}
          >
            {title}
          </Text>
          {subtitle && (
            <Text style={styles.selectionCardSubtitle}>{subtitle}</Text>
          )}
        </View>
        {selected && (
          <View style={styles.checkmark}>
            <Text style={styles.checkmarkText}>✓</Text>
          </View>
        )}
      </View>
    </TouchableOpacity>
  );
}

// Progress Bar
export const ProgressBar = ({ progress, steps = 7 }) => {
  const progressPercentage = (progress / steps) * 100;

  return (
    <View style={styles.progressContainer}>
      <View style={styles.progressBackground}>
        <LinearGradient
          colors={['#B565A7', '#8B4E99']}
          style={[styles.progressFill, { width: `${progressPercentage}%` }]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
        />
      </View>
      <Text style={styles.progressText}>{progress}/{steps}</Text>
    </View>
  );
};

// Input Field
export const InputField = ({ placeholder, value, onChangeText, multiline = false }) => {
  return (
    <View style={styles.inputContainer}>
      <TextInput
        style={[styles.input, multiline && styles.inputMultiline]}
        placeholder={placeholder}
        placeholderTextColor="#999"
        value={value}
        onChangeText={onChangeText}
        multiline={multiline}
      />
    </View>
  );
};

// Message Bubble (Auvra speaking)
export const MessageBubble = ({ message, text }) => {
  return (
    <View style={styles.messageBubble}>
      <Text style={styles.messageText}>{message ?? text}</Text>
    </View>
  );
};

// Section Header
export const SectionHeader = ({ title, emoji }) => {
  return (
    <View style={styles.sectionHeader}>
      {emoji && <Text style={styles.sectionEmoji}>{emoji}</Text>}
      <Text style={styles.sectionTitle}>{title}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  // Character
  characterContainer: {
    alignSelf: 'center',
    marginVertical: 20,
  },
  characterGradient: {
    width: '100%',
    height: '100%',
    borderRadius: 100,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },

  // Primary Button
  primaryButton: {
    width: '100%',
    height: 56,
    borderRadius: 28,
    overflow: 'hidden',
    marginVertical: 10,
  },
  buttonGradient: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
  },
  buttonText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: '600',
  },
  buttonDisabled: {
    opacity: 0.5,
  },

  // Selection Card
  selectionCard: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 16,
    marginVertical: 8,
    borderWidth: 2,
    borderColor: '#E5E5E5',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  selectionCardCompact: {
    padding: 14,
    minWidth: '48%',
  },
  selectionCardSelected: {
    borderColor: '#B565A7',
    backgroundColor: '#F9F0FB',
  },
  selectionContent: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  selectionIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  selectionTextContainer: {
    flex: 1,
  },
  selectionTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
  },
  selectionTitleCompact: {
    fontSize: 14,
  },
  selectionSubtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  checkmark: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#B565A7',
    justifyContent: 'center',
    alignItems: 'center',
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
  },

  // Progress Bar
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 60,
    paddingBottom: 10,
  },
  progressBackground: {
    flex: 1,
    height: 8,
    backgroundColor: '#E5E5E5',
    borderRadius: 4,
    overflow: 'hidden',
    marginRight: 12,
  },
  progressFill: {
    height: '100%',
    borderRadius: 4,
  },
  progressText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },

  // Message Bubble
  messageBubble: {
    backgroundColor: '#E8D4F4',
    borderRadius: 20,
    padding: 16,
    marginHorizontal: 20,
    marginVertical: 10,
    alignSelf: 'flex-start',
    maxWidth: '80%',
  },
  messageText: {
    fontSize: 16,
    color: '#333',
    lineHeight: 22,
  },

  // Section Header
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionEmoji: {
    fontSize: 24,
    marginRight: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },

  // Input
  inputContainer: {
    marginVertical: 10,
  },
  input: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#E5E5E5',
  },
  inputMultiline: {
    minHeight: 100,
    textAlignVertical: 'top',
  },
});
