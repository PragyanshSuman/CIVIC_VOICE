
import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, Alert, ScrollView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import axios from 'axios';
import { API_URL } from '../../constants/Config';
import { useAppDispatch } from '../../store/hooks';
import { signupUser } from '../../store/slices/authSlice';

const SignupScreen = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState<'CITIZEN' | 'GOVERNMENT'>('CITIZEN');
  const [loading, setLoading] = useState(false);
  
  const dispatch = useAppDispatch();
  const navigation = useNavigation();

  const handleSignup = async () => {
    if (!email || !password || !fullName) {
        Alert.alert('Error', 'Please fill in all fields');
        return;
    }
    
    setLoading(true);
    try {
      const resultAction = await dispatch(signupUser({ 
        email, 
        password, 
        full_name: fullName,
        role: role
      }));
      if (signupUser.fulfilled.match(resultAction)) {
        Alert.alert('Success', 'Account created! Please login.', [
          { text: 'OK', onPress: () => navigation.navigate('Login' as never) }
        ]);
      } else {
        const errorMsg = resultAction.payload as string;
        Alert.alert('Signup Failed', errorMsg);
      }
    } catch (error: any) {
       Alert.alert('Signup Failed', error.message || 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Create Account</Text>
      <Text style={styles.subtitle}>Join Civic Voice</Text>
      
      <TextInput
        style={styles.input}
        placeholder="Full Name"
        value={fullName}
        onChangeText={setFullName}
        autoCapitalize="words"
      />
      <TextInput
        style={styles.input}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
      />
      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />

      <View style={styles.roleContainer}>
        <Text style={styles.roleLabel}>Sign up as:</Text>
        <View style={styles.roleButtons}>
          <TouchableOpacity 
            style={[styles.roleButton, role === 'CITIZEN' && styles.roleButtonActive]} 
            onPress={() => setRole('CITIZEN')}
          >
            <Text style={[styles.roleButtonText, role === 'CITIZEN' && styles.roleButtonTextActive]}>Citizen</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.roleButton, role === 'GOVERNMENT' && styles.roleButtonActive]} 
            onPress={() => setRole('GOVERNMENT')}
          >
            <Text style={[styles.roleButtonText, role === 'GOVERNMENT' && styles.roleButtonTextActive]}>Official</Text>
          </TouchableOpacity>
        </View>
      </View>
      
      {loading ? (
        <ActivityIndicator size="large" color="#2196F3" style={styles.loader} />
      ) : (
        <TouchableOpacity style={styles.button} onPress={handleSignup}>
          <Text style={styles.buttonText}>SIGN UP</Text>
        </TouchableOpacity>
      )}
      
      <TouchableOpacity 
        style={styles.linkContainer}
        onPress={() => navigation.navigate('Login' as never)}
      >
        <Text style={styles.linkText}>
          Already have an account? <Text style={styles.linkBold}>Login</Text>
        </Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 8,
    textAlign: 'center',
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    marginBottom: 30,
    textAlign: 'center',
    color: '#666',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    padding: 15,
    marginBottom: 15,
    borderRadius: 8,
    fontSize: 16,
    backgroundColor: '#f9f9f9',
  },
  roleContainer: {
    marginBottom: 20,
  },
  roleLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
    marginLeft: 4,
  },
  roleButtons: {
    flexDirection: 'row',
    gap: 10,
  },
  roleButton: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ddd',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  roleButtonActive: {
    backgroundColor: '#2196F3',
    borderColor: '#2196F3',
  },
  roleButtonText: {
    color: '#666',
    fontWeight: '600',
  },
  roleButtonTextActive: {
    color: '#fff',
  },
  button: {
    backgroundColor: '#2196F3',
    padding: 15,
    borderRadius: 8,
    marginTop: 10,
  },
  buttonText: {
    color: '#fff',
    textAlign: 'center',
    fontSize: 16,
    fontWeight: 'bold',
  },
  loader: {
    marginTop: 20,
  },
  linkContainer: {
    marginTop: 20,
    alignItems: 'center',
  },
  linkText: {
    color: '#666',
    fontSize: 14,
  },
  linkBold: {
    color: '#2196F3',
    fontWeight: 'bold',
  },
});

export default SignupScreen;
