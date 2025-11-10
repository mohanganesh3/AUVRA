// Main App Entry Point
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { StatusBar } from 'expo-status-bar';
import { AssessmentProvider } from './src/utils/AssessmentContext';
import AppStatusBanner from './src/components/AppStatusBanner';

// Import Screens
import WelcomeScreen from './src/screens/WelcomeScreen';
import BasicInfoScreen from './src/screens/BasicInfoScreen';
import PeriodPatternScreen from './src/screens/PeriodPatternScreen';
import CycleDetailsScreen from './src/screens/CycleDetailsScreen';
import HealthConcernsScreen from './src/screens/HealthConcernsScreen';
import TopConcernScreen from './src/screens/TopConcernScreen';
import DiagnosisScreen from './src/screens/DiagnosisScreen';
import LabResultsScreen from './src/screens/LabResultsScreen';
import AnalyzingScreen from './src/screens/AnalyzingScreen';
import ResultsScreen from './src/screens/ResultsScreen';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <AssessmentProvider>
      <NavigationContainer>
        <StatusBar style="dark" />
        <AppStatusBanner />
        <Stack.Navigator
          initialRouteName="Welcome"
          screenOptions={{
            headerShown: false,
            contentStyle: { backgroundColor: '#F5E6F9' },
            animation: 'slide_from_right',
          }}
        >
          <Stack.Screen name="Welcome" component={WelcomeScreen} />
          <Stack.Screen name="BasicInfo" component={BasicInfoScreen} />
          <Stack.Screen name="PeriodPattern" component={PeriodPatternScreen} />
          <Stack.Screen name="CycleDetails" component={CycleDetailsScreen} />
          <Stack.Screen name="HealthConcerns" component={HealthConcernsScreen} />
          <Stack.Screen name="TopConcern" component={TopConcernScreen} />
          <Stack.Screen name="Diagnosis" component={DiagnosisScreen} />
          <Stack.Screen name="LabResults" component={LabResultsScreen} />
          <Stack.Screen name="Analyzing" component={AnalyzingScreen} />
          <Stack.Screen name="Results" component={ResultsScreen} />
        </Stack.Navigator>
      </NavigationContainer>
    </AssessmentProvider>
  );
}
