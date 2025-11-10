// Assessment Context
// Global state management for assessment data

import React, { createContext, useState, useContext, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

const AssessmentContext = createContext();

export const useAssessment = () => {
  const context = useContext(AssessmentContext);
  if (!context) {
    throw new Error('useAssessment must be used within AssessmentProvider');
  }
  return context;
};

export const AssessmentProvider = ({ children }) => {
  const STORAGE_KEY = 'auvra_assessment_data_v1';
  const [assessmentData, setAssessmentData] = useState({
    basic_info: {},
    period_pattern: {},
    cycle_details: {},
    health_concerns: {},
    top_concern: null,
    diagnosed_conditions: {},
    lab_results: null,
  });
  const [result, setResult] = useState(null);

  // Load saved data on mount
  useEffect(() => {
    loadFromStorage();
  }, []);

  const loadFromStorage = async () => {
    try {
      const saved = await AsyncStorage.getItem(STORAGE_KEY);
      if (saved) {
        setAssessmentData(JSON.parse(saved));
      }
    } catch (error) {
      console.error('Error loading assessment:', error);
    }
  };

  const saveToStorage = async (data) => {
    try {
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (error) {
      console.error('Error saving assessment:', error);
    }
  };

  const updateSection = (section, data) => {
    setAssessmentData((prev) => {
      const updated = { ...prev, [section]: data };
      saveToStorage(updated);
      return updated;
    });
  };

  const clearAssessment = async () => {
    try {
      await AsyncStorage.removeItem(STORAGE_KEY);
      setAssessmentData({
        basic_info: {},
        period_pattern: {},
        cycle_details: {},
        health_concerns: {},
        top_concern: null,
        diagnosed_conditions: {},
        lab_results: null,
      });
      setResult(null);
    } catch (error) {
      console.error('Error clearing assessment:', error);
    }
  };

  return (
    <AssessmentContext.Provider
      value={{
        assessmentData,
        result,
        updateSection,
        setResult,
        clearAssessment,
        saveToStorage,
        loadFromStorage,
      }}
    >
      {children}
    </AssessmentContext.Provider>
  );
};
