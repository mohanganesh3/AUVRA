// API Service for Auvra Backend
// Handles all HTTP requests to the FastAPI backend

import axios from 'axios';
import { Platform, NativeModules } from 'react-native';
import Constants from 'expo-constants';

// IMPORTANT: Backend base URL
// Android devices/emulators cannot reach "localhost" - that refers to the device itself.
// Solution: Use the host machine's actual local network IP.
// 
// QUICK FIX for Android:
// Set your machine's IP: EXPO_PUBLIC_API_URL="http://10.0.195.252:5055" npx expo start
// Or edit this file to hardcode your IP below.

const getDefaultBaseURL = () => {
  // If user explicitly set env var, use it
  if (process.env.EXPO_PUBLIC_API_URL) {
    console.log('[API] Using env EXPO_PUBLIC_API_URL:', process.env.EXPO_PUBLIC_API_URL);
    return process.env.EXPO_PUBLIC_API_URL;
  }

  // Platform-specific defaults
  if (Platform.OS === 'android') {
    // Try to derive the host IP from the Metro bundler URL
    try {
      // Preferred in Expo SDK 49+: Constants.expoConfig.hostUri or debuggerHost
      const expoHost = Constants?.expoConfig?.hostUri || Constants?.manifest?.debuggerHost || Constants?.manifest2?.extra?.expoGo?.developer?.host;
      let hostFromExpo = null;
      if (expoHost) {
        hostFromExpo = expoHost.split(':')[0];
      }

      // Fallback for bare RN: scriptURL from SourceCode
      const scriptURL = NativeModules?.SourceCode?.scriptURL;
      let hostFromScript = null;
      if (scriptURL) {
        const afterScheme = scriptURL.split('://')[1] || '';
        hostFromScript = afterScheme.split(':')[0];
      }

      const host = hostFromExpo || hostFromScript;
      if (host) {
        const url = `http://${host}:5055`;
        console.log('[API] Android detected, derived host IP from dev server:', url);
        return url;
      }
    } catch (e) {
      console.log('[API] Android host detection failed, falling back to defaults');
    }

    // As a last resort on Android, try 10.0.2.2 (Android emulator) else prompt to set env
    const emulatorURL = 'http://10.0.2.2:5055';
    console.log('[API] Android fallback using emulator URL:', emulatorURL);
    return emulatorURL;
  } else if (Platform.OS === 'ios') {
    // iOS simulator can reach localhost directly
    console.log('[API] iOS detected, using localhost');
    return 'http://localhost:5055';
  } else if (Platform.OS === 'web') {
    // Web can reach localhost
    console.log('[API] Web detected, using localhost');
    return 'http://localhost:5055';
  }

  // Fallback
  console.log('[API] Unknown platform, using localhost');
  return 'http://localhost:5055';
};

const API_BASE_URL = getDefaultBaseURL();
console.log('[API] Final API_BASE_URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds - increased for LLM processing
});

// Add request/response interceptors for better debugging
api.interceptors.request.use(
  (config) => {
    console.log(`[API REQUEST] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API REQUEST ERROR]', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    console.log(`[API RESPONSE] ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error(`[API ERROR] ${error.response.status} ${error.response.config.url}`, error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error('[API ERROR] No response received:', error.message);
      console.error('[API ERROR] Attempting to reach:', error.config?.baseURL);
    } else {
      // Something else happened
      console.error('[API ERROR] Request setup failed:', error.message);
    }
    return Promise.reject(error);
  }
);

// Health check
export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    console.log('[API] Health check successful:', response.data);
    return response.data;
  } catch (error) {
    console.error('[API] Health check failed:', error.message);
    throw error;
  }
};

// Complete hormone assessment
export const submitAssessment = async (assessmentData) => {
  try {
    console.log('Submitting assessment to:', `${API_BASE_URL}/api/v1/assess`);
    const response = await api.post('/api/v1/assess', assessmentData);
    return response.data;
  } catch (error) {
    console.error('Assessment submission failed:', error.response?.data || error.message);
    throw error;
  }
};

// Quick assessment (for testing)
export const submitQuickAssessment = async (quickData) => {
  try {
    const response = await api.post('/api/v1/assess/quick', quickData);
    return response.data;
  } catch (error) {
    console.error('Quick assessment failed:', error);
    throw error;
  }
};

// Validate custom "Others" input
export const validateOthersInput = async (input, context) => {
  try {
    const response = await api.post('/api/v1/validate/others', {
      input,
      context,
    });
    return response.data;
  } catch (error) {
    console.error('Others validation failed:', error);
    throw error;
  }
};

// Export the base URL for reference
export { API_BASE_URL };

export default api;
