import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Alert, Text, TouchableOpacity, Dimensions, TextInput, ActivityIndicator, Image } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useAppSelector, useAppDispatch } from '../../store/hooks';
import { refreshProfile } from '../../store/slices/authSlice';
import axios from 'axios';
import * as Location from 'expo-location';
import { API_URL } from '../../constants/Config';
import { Colors } from '../../constants/Colors';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';

const { width } = Dimensions.get('window');

const CATEGORIES = ['Roads', 'Lighting', 'Waste', 'Safety', 'Parks', 'Other'];

import * as ImagePicker from 'expo-image-picker';
import { Video, ResizeMode } from 'expo-av';

const SubmitProblemScreen = () => {
  const dispatch = useAppDispatch();
  const [title, setTitle] = useState('');
  const [desc, setDesc] = useState('');
  const [category, setCategory] = useState('Roads');
  const [media, setMedia] = useState<ImagePicker.ImagePickerAsset[]>([]);
  const [loading, setLoading] = useState(false);
  const { token } = useAppSelector((state) => state.auth);
  const navigation = useNavigation();

  const captureVerifiedMedia = async () => {
    // Request permissions first
    const { status: cameraStatus } = await ImagePicker.requestCameraPermissionsAsync();
    const { status: locationStatus } = await Location.requestForegroundPermissionsAsync();
    
    if (cameraStatus !== 'granted' || locationStatus !== 'granted') {
      Alert.alert('Permissions Required', 'Camera and Location access are mandatory for verified Civic Proof reporting.');
      return;
    }

    let result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.All,
      quality: 0.8,
      exif: true,
    });

    if (!result.canceled) {
      // Capture hardware snapshot of location at the moment of shutter press
      const location = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.High });
      
      const verifiedAsset = {
        ...result.assets[0],
        verifiedLocation: location.coords,
        isVerified: true,
        capturedAt: new Date().toISOString()
      };
      
      setMedia(current => [...current, verifiedAsset as any]);
    }
  };

  const pickFromGallery = async () => {
    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.All,
      allowsMultipleSelection: true,
      selectionLimit: 3,
      quality: 0.8,
    });

    if (!result.canceled) {
      const galleryAssets = result.assets.map(asset => ({
        ...asset,
        isVerified: false
      }));
      setMedia(current => [...current, ...galleryAssets as any]);
    }
  };

  const uploadMediaFiles = async () => {
    if (media.length === 0) return null;
    
    const formData = new FormData();
    media.forEach((asset, index) => {
      const uriParts = asset.uri.split('.');
      const fileType = uriParts[uriParts.length - 1];
      
      formData.append('files', {
        uri: asset.uri,
        name: `upload_${index}.${fileType}`,
        type: asset.type === 'video' ? `video/${fileType}` : `image/${fileType}`
      } as any);
    });

    try {
      const response = await axios.post(`${API_URL}/media/upload`, formData, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data; // Returns list of URLs
    } catch (err) {
      console.error('Media upload failed', err);
      throw new Error('Media upload failed');
    }
  };

  const handleSubmit = async () => {
    if (!title || !desc) {
      Alert.alert('Missing Info', 'Please fill in all required fields.');
      return;
    }

    setLoading(true);
    try {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission denied', 'Location access is required for report accuracy.');
        setLoading(false);
        return;
      }
      let location = await Location.getCurrentPositionAsync({});

      // Upload media
      let uploadedUrls: string[] = [];
      if (media.length > 0) {
        uploadedUrls = await uploadMediaFiles();
      }

      const payload = {
        title,
        description: desc,
        category, 
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
        address: "Current Location",
        image_url: uploadedUrls && uploadedUrls.length > 0 ? uploadedUrls[0] : null,
        media_attachments: media.map((asset: any, index) => ({
            file_url: uploadedUrls[index],
            media_type: asset.type === 'video' ? 'video' : 'image',
            latitude: asset.verifiedLocation?.latitude || location.coords.latitude,
            longitude: asset.verifiedLocation?.longitude || location.coords.longitude,
            is_verified_capture: asset.isVerified || false,
            device_info: "Mobile In-App Capture"
        }))
      };

      await axios.post(`${API_URL}/problems/`, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Refresh profile to get updated Karma
      dispatch(refreshProfile());
      
      Alert.alert('Report Verified', 'Your civic report has been successfully submitted to the innovation hub.');
      navigation.goBack();
    } catch (error) {
       Alert.alert('Submission Failed', 'An error occurred while transmitting your report.');
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
          <Text style={styles.headerTitle}>Report Civic Issue</Text>
          <Text style={styles.headerSubtitle}>Provide clear details to help our AI verify and prioritize the issue.</Text>
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>SELECT CATEGORY</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.categoryList}>
            {CATEGORIES.map(cat => (
              <TouchableOpacity 
                key={cat} 
                onPress={() => setCategory(cat)}
                style={[styles.catItem, category === cat && styles.catItemActive]}
              >
                <Text style={[styles.catText, category === cat && styles.catTextActive]}>{cat}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>PROBLEM TITLE</Text>
          <TextInput 
            style={styles.input} 
            value={title} 
            onChangeText={setTitle} 
            placeholder="E.g., Severe Pothole in Downtown"
            placeholderTextColor="rgba(255,255,255,0.3)"
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>DETAILED DESCRIPTION</Text>
          <TextInput 
            style={[styles.input, styles.textArea]} 
            value={desc} 
            onChangeText={setDesc} 
            multiline 
            placeholder="Describe the problem, its impact, and exact location..."
            placeholderTextColor="rgba(255,255,255,0.3)"
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>MEDIA EVIDENCE (CIVIC PROOF)</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.mediaList}>
            <TouchableOpacity style={styles.addMediaBtn} onPress={captureVerifiedMedia}>
              <MaterialCommunityIcons name="camera" size={28} color={Colors.primary} />
              <Text style={styles.addMediaText}>Camera</Text>
            </TouchableOpacity>

            <TouchableOpacity style={[styles.addMediaBtn, { borderStyle: 'solid' }]} onPress={pickFromGallery}>
              <MaterialCommunityIcons name="image-multiple" size={24} color={Colors.textSecondary} />
              <Text style={[styles.addMediaText, { color: Colors.textSecondary }]}>Gallery</Text>
            </TouchableOpacity>
            
            {media.map((asset: any, index) => (
              <View key={index} style={styles.mediaPreview}>
                {asset.type === 'video' ? (
                  <Video
                    source={{ uri: asset.uri }}
                    style={styles.mediaAssets}
                    resizeMode={ResizeMode.COVER}
                    isMuted
                  />
                ) : (
                  <Image source={{ uri: asset.uri }} style={styles.mediaAssets} />
                )}
                {asset.isVerified && (
                    <View style={styles.verifiedBadge}>
                        <MaterialCommunityIcons name="shield-check" size={14} color={Colors.white} />
                    </View>
                )}
              </View>
            ))}
          </ScrollView>
        </View>

        <View style={styles.infoCard}>
          <MaterialCommunityIcons name="information-outline" size={20} color={Colors.primary} />
          <Text style={styles.infoText}>
            Your GPS coordinates will be automatically shared to ensure the fastest verified response.
          </Text>
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
              <Text style={styles.btnText}>SUBMIT VERIFIED REPORT</Text>
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
  
  categoryList: { paddingRight: 20 },
  catItem: { paddingHorizontal: 16, paddingVertical: 8, borderRadius: 12, backgroundColor: 'rgba(255,255,255,0.05)', marginRight: 10, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  catItemActive: { backgroundColor: Colors.primary, borderColor: Colors.primary },
  catText: { color: Colors.textSecondary, fontSize: 13, fontWeight: '600' },
  catTextActive: { color: Colors.white },
  
  input: { 
    backgroundColor: 'rgba(255,255,255,0.03)', 
    borderRadius: 16, 
    padding: 16, 
    color: Colors.text, 
    fontSize: 15, 
    borderWidth: 1, 
    borderColor: 'rgba(255,255,255,0.05)' 
  },
  textArea: { height: 120, textAlignVertical: 'top' },
  
  infoCard: { flexDirection: 'row', alignItems: 'center', padding: 16, backgroundColor: 'rgba(99, 102, 241, 0.05)', borderRadius: 16, marginBottom: 32 },
  infoText: { flex: 1, marginLeft: 12, fontSize: 12, color: Colors.textSecondary, lineHeight: 18 },
  
  actionBtn: { borderRadius: 20, overflow: 'hidden' },
  btnGradient: { paddingVertical: 18, alignItems: 'center' },
  btnText: { color: Colors.white, fontSize: 15, fontWeight: '900', letterSpacing: 1 },

  // Media Styles
  mediaList: { paddingRight: 24, flexDirection: 'row' },
  addMediaBtn: {
    width: 90, height: 90,
    borderRadius: 12,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
    borderStyle: 'dashed',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12
  },
  addMediaText: { color: Colors.primary, fontSize: 11, fontWeight: '800', marginTop: 8 },
  mediaPreview: {
    width: 90, height: 90,
    borderRadius: 12,
    overflow: 'hidden',
    marginRight: 12,
    backgroundColor: '#000',
    position: 'relative'
  },
  mediaAssets: { width: '100%', height: '100%' },
  verifiedBadge: {
    position: 'absolute',
    top: 5,
    right: 5,
    backgroundColor: Colors.primary,
    borderRadius: 10,
    padding: 2,
    borderWidth: 1,
    borderColor: Colors.white
  }
});

export default SubmitProblemScreen;

