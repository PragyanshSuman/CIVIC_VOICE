import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Alert, Text, TextInput, TouchableOpacity, ActivityIndicator, Dimensions } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { useAppSelector } from '../../store/hooks';
import axios from 'axios';
import { API_URL } from '../../constants/Config';
import { Colors } from '../../constants/Colors';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';

const { width } = Dimensions.get('window');

const SubmitSolutionScreen = () => {
  const [title, setTitle] = useState('');
  const [desc, setDesc] = useState('');
  const [loading, setLoading] = useState(false);
  const { token } = useAppSelector((state) => state.auth);
  const navigation = useNavigation();
  const route = useRoute();
  const { problemId } = route.params as { problemId: string };

  const handleSubmit = async () => {
    if (!title || !desc) {
      Alert.alert('Incomplete Fields', 'Please provide a title and description for your innovation.');
      return;
    }

    setLoading(true);
    try {
      const payload = {
        title,
        description: desc,
        problem_id: problemId
      };

      await axios.post(`${API_URL}/solutions/`, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      Alert.alert('Proposal Submitted', 'Your solution has been sent to the AI processing hub for impact and feasibility scoring.');
      navigation.goBack();
    } catch (error) {
       console.log(error);
       Alert.alert('Transmission Error', 'An error occurred while submitting your proposal.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      <LinearGradient colors={[Colors.background, '#1E293B']} style={StyleSheet.absoluteFill} />
      
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Propose Innovation</Text>
          <Text style={styles.headerSubtitle}>Propose a solution to fix this civic issue. Our AI will analyze your proposal's impact and feasibility.</Text>
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>INNOVATION TITLE</Text>
          <TextInput 
            style={styles.input} 
            value={title} 
            onChangeText={setTitle} 
            placeholder="E.g., Automated Waste Sorting Hubs"
            placeholderTextColor="rgba(255,255,255,0.3)"
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>SOLUTION STRATEGY</Text>
          <TextInput 
            style={[styles.input, styles.textArea]} 
            value={desc} 
            onChangeText={setDesc} 
            multiline 
            placeholder="Explain how this innovation works, the required resources, and the expected outcome..."
            placeholderTextColor="rgba(255,255,255,0.3)"
          />
        </View>

        <View style={styles.aiHintCard}>
          <LinearGradient colors={['rgba(99, 102, 241, 0.1)', 'rgba(99, 102, 241, 0.05)']} style={styles.aiHintGradient}>
            <MaterialCommunityIcons name="auto-fix" size={24} color={Colors.primary} />
            <View style={styles.aiHintContent}>
              <Text style={styles.aiHintTitle}>AI SCORING ENGINE</Text>
              <Text style={styles.aiHintText}>
                Be specific about technology, cost efficiency, and community impact to achieve a higher score.
              </Text>
            </View>
          </LinearGradient>
        </View>

        <TouchableOpacity 
          style={styles.actionBtn} 
          onPress={handleSubmit} 
          disabled={loading}
        >
          <LinearGradient colors={[Colors.primary, '#4F46E5']} style={styles.btnGradient}>
            {loading ? (
              <ActivityIndicator color={Colors.white} />
            ) : (
              <Text style={styles.btnText}>SUBMIT PROPOSAL</Text>
            )}
          </LinearGradient>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  content: { padding: 24, paddingBottom: 40 },
  header: { marginBottom: 32 },
  headerTitle: { fontSize: 28, fontWeight: '800', color: Colors.text, marginBottom: 8 },
  headerSubtitle: { fontSize: 14, color: Colors.textSecondary, lineHeight: 22 },
  
  formGroup: { marginBottom: 24 },
  label: { fontSize: 11, fontWeight: '900', color: Colors.textSecondary, marginBottom: 12, letterSpacing: 1 },
  
  input: { 
    backgroundColor: 'rgba(255,255,255,0.03)', 
    borderRadius: 16, 
    padding: 16, 
    color: Colors.text, 
    fontSize: 15, 
    borderWidth: 1, 
    borderColor: 'rgba(255,255,255,0.05)' 
  },
  textArea: { height: 180, textAlignVertical: 'top' },
  
  aiHintCard: { borderRadius: 20, overflow: 'hidden', marginBottom: 32 },
  aiHintGradient: { flexDirection: 'row', padding: 20, alignItems: 'center' },
  aiHintContent: { flex: 1, marginLeft: 16 },
  aiHintTitle: { fontSize: 11, fontWeight: '900', color: Colors.primary, marginBottom: 4, letterSpacing: 1 },
  aiHintText: { fontSize: 13, color: Colors.textSecondary, lineHeight: 18 },
  
  actionBtn: { borderRadius: 20, overflow: 'hidden' },
  btnGradient: { paddingVertical: 18, alignItems: 'center' },
  btnText: { color: Colors.white, fontSize: 15, fontWeight: '900', letterSpacing: 1 }
});

export default SubmitSolutionScreen;

