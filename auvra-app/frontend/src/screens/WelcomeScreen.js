// Welcome Screen - First screen matching screenshot
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { AuvraCharacter, PrimaryButton, MessageBubble } from '../components/UIComponents';

export default function WelcomeScreen({ navigation }) {
  return (
    <LinearGradient
      colors={['#F5E6F9', '#E8D4F4']}
      style={styles.container}
      start={{ x: 0.5, y: 0 }}
      end={{ x: 0.5, y: 1 }}
    >
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.content}>
          <View style={styles.topSection}>
            <Text style={styles.versionText}>1.00</Text>
          </View>

          <View style={styles.middleSection}>
            <Text style={styles.greeting}>Hi! I'm</Text>
            <Text style={styles.appName}>Auvra</Text>
            
            <AuvraCharacter expression="happy" size={150} />
            
            <MessageBubble 
              message="Your personal hormone guide. I'm here to help you feel more in control of your body."
            />
          </View>

          <View style={styles.bottomSection}>
            <PrimaryButton
              title="Continue"
              onPress={() => navigation.navigate('BasicInfo')}
            />
          </View>
        </View>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
    justifyContent: 'space-between',
  },
  topSection: {
    paddingTop: 20,
    alignItems: 'flex-start',
  },
  versionText: {
    fontSize: 16,
    color: '#666',
    fontWeight: '500',
  },
  middleSection: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  greeting: {
    fontSize: 28,
    color: '#666',
    marginBottom: 4,
  },
  appName: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#B565A7',
    marginBottom: 30,
  },
  bottomSection: {
    paddingBottom: 40,
  },
});
