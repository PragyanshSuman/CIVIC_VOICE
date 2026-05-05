
import React, { useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  TouchableOpacity, 
  TextInput, 
  ScrollView, 
  Alert,
  ActivityIndicator
} from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { Colors } from '../../constants/Colors';
import apiClient from '../../utils/api';

const STATUS_OPTIONS = [
  { label: 'Triage & Acknowledge', value: 'ACKNOWLEDGED', icon: 'eye-check' },
  { label: 'Mark In-Progress', value: 'IN_PROGRESS', icon: 'hammer-wrench' },
  { label: 'Resolve Problem', value: 'RESOLVED', icon: 'check-decagram' },
  { label: 'Close Report', value: 'CLOSED', icon: 'archive-lock' },
];

const CreateWorkOrderScreen = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const { problemId } = route.params as { problemId: string };

  const [status, setStatus] = useState('IN_PROGRESS');
  const [responseText, setResponseText] = useState('');
  const [actionPlan, setActionPlan] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!responseText.trim()) {
      Alert.alert('Required', 'Please provide an official response text.');
      return;
    }

    setLoading(true);
    try {
      await apiClient.post(`/problems/${problemId}/respond`, {
        problem_id: problemId,
        response_text: responseText,
        action_plan: actionPlan,
        new_status: status
      });
      
      Alert.alert('Success', 'Work order created and status updated!', [
        { text: 'OK', onPress: () => navigation.goBack() }
      ]);
    } catch (error: any) {
      console.error('Work Order Error:', error);
      Alert.alert('Error', error.response?.data?.detail || 'Failed to create work order');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={styles.title}>Dispatch Work Order</Text>
          <Text style={styles.subtitle}>Update the status and provide official feedback to citizens.</Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.label}>SELECT NEW STATUS</Text>
          <View style={styles.statusGrid}>
            {STATUS_OPTIONS.map((opt) => (
              <TouchableOpacity
                key={opt.value}
                style={[
                  styles.statusCard,
                  status === opt.value && styles.activeStatusCard
                ]}
                onPress={() => setStatus(opt.value)}
              >
                <MaterialCommunityIcons 
                  name={opt.icon as any} 
                  size={24} 
                  color={status === opt.value ? Colors.primary : Colors.textSecondary} 
                />
                <Text style={[
                  styles.statusLabel,
                  status === opt.value && styles.activeStatusLabel
                ]}>
                  {opt.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.label}>OFFICIAL RESPONSE</Text>
          <TextInput
            style={styles.textArea}
            placeholder="What is the current update for citizens?"
            placeholderTextColor="rgba(255,255,255,0.3)"
            multiline
            numberOfLines={4}
            value={responseText}
            onChangeText={setResponseText}
          />
        </View>

        <View style={styles.section}>
          <Text style={styles.label}>INTERNAL ACTION PLAN (OPTIONAL)</Text>
          <TextInput
            style={[styles.textArea, { height: 80 }]}
            placeholder="Steps being taken by the department..."
            placeholderTextColor="rgba(255,255,255,0.3)"
            multiline
            value={actionPlan}
            onChangeText={setActionPlan}
          />
        </View>

        <TouchableOpacity 
          style={styles.submitBtn} 
          onPress={handleSubmit}
          disabled={loading}
        >
          <LinearGradient 
            colors={[Colors.secondary, '#059669']} 
            style={styles.submitGradient}
          >
            {loading ? (
              <ActivityIndicator color={Colors.white} />
            ) : (
              <>
                <MaterialCommunityIcons name="send-lock" size={20} color={Colors.white} style={{ marginRight: 8 }} />
                <Text style={styles.submitBtnText}>DEPLOY UPDATES</Text>
              </>
            )}
          </LinearGradient>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  scrollContent: { padding: 24 },
  header: { marginBottom: 32 },
  title: { color: Colors.text, fontSize: 28, fontWeight: '800', marginBottom: 8 },
  subtitle: { color: Colors.textSecondary, fontSize: 15, lineHeight: 22 },
  
  section: { marginBottom: 32 },
  label: { color: Colors.primary, fontSize: 12, fontWeight: '800', letterSpacing: 1.5, marginBottom: 16 },
  
  statusGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  statusCard: { 
    width: '48%', 
    backgroundColor: 'rgba(255,255,255,0.03)', 
    borderRadius: 16, 
    padding: 16,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
    alignItems: 'center',
    justifyContent: 'center',
    height: 100
  },
  activeStatusCard: {
    backgroundColor: 'rgba(99, 102, 241, 0.1)',
    borderColor: Colors.primary,
  },
  statusLabel: { color: Colors.textSecondary, fontSize: 11, fontWeight: '700', marginTop: 8, textAlign: 'center' },
  activeStatusLabel: { color: Colors.primary },
  
  textArea: {
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderRadius: 16,
    padding: 16,
    color: Colors.text,
    fontSize: 15,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
    textAlignVertical: 'top',
    minHeight: 120
  },
  
  submitBtn: { borderRadius: 16, overflow: 'hidden', marginTop: 12 },
  submitGradient: { 
    paddingVertical: 18, 
    flexDirection: 'row', 
    justifyContent: 'center', 
    alignItems: 'center' 
  },
  submitBtnText: { color: Colors.white, fontSize: 16, fontWeight: '800', letterSpacing: 1 }
});

export default CreateWorkOrderScreen;
