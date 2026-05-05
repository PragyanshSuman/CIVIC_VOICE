import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Text, TouchableOpacity, Dimensions } from 'react-native';
import MapView, { Marker, PROVIDER_GOOGLE, Polygon } from 'react-native-maps';
import axios from 'axios';
import { useAppSelector } from '../../store/hooks';
import { API_URL } from '../../constants/Config';
import { Problem, Jurisdiction } from '../../types';
import { useNavigation } from '@react-navigation/native';
import { Colors } from '../../constants/Colors';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';

const { width } = Dimensions.get('window');

// Custom Dark Map Style
const MAP_STYLE = [
  { "elementType": "geometry", "stylers": [{ "color": "#1e293b" }] },
  { "elementType": "labels.text.fill", "stylers": [{ "color": "#94a3b8" }] },
  { "elementType": "labels.text.stroke", "stylers": [{ "color": "#1e293b" }] },
  { "featureType": "administrative", "elementType": "geometry", "stylers": [{ "color": "#334155" }] },
  { "featureType": "poi", "elementType": "geometry", "stylers": [{ "color": "#334155" }] },
  { "featureType": "road", "elementType": "geometry", "stylers": [{ "color": "#0f172a" }] },
  { "featureType": "transit", "elementType": "geometry", "stylers": [{ "color": "#334155" }] },
  { "featureType": "water", "elementType": "geometry", "stylers": [{ "color": "#020617" }] }
];

const MapScreen = () => {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [jurisdictions, setJurisdictions] = useState<Jurisdiction[]>([]);
  const { token } = useAppSelector((state) => state.auth);
  const navigation = useNavigation() as any;

  useEffect(() => {
    // Fetch Problems
    axios.get<Problem[]>(`${API_URL}/problems/`, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => setProblems(res.data))
      .catch(err => console.log('Map fetch error', err));

    // Fetch Jurisdictions
    axios.get<Jurisdiction[]>(`${API_URL}/jurisdictions/`, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => {
          // Filter out those without polygons and parse coordinates
          setJurisdictions(res.data.filter(j => j.boundary_polygon));
      })
      .catch(err => console.log('Jurisdiction fetch error', err));
  }, [token]);

  const initialRegion = problems.length > 0 
    ? {
        latitude: problems[0].latitude,
        longitude: problems[0].longitude,
        latitudeDelta: 0.05,
        longitudeDelta: 0.05,
      }
    : {
        latitude: 40.7128,
        longitude: -74.0060,
        latitudeDelta: 0.1,
        longitudeDelta: 0.1,
      };

  const getMarkerInfo = (category: string) => {
    const cat = category.toLowerCase();
    if (cat.includes('road')) return { icon: 'road-variant', color: Colors.primary };
    if (cat.includes('light')) return { icon: 'lightbulb-on', color: Colors.warning };
    if (cat.includes('waste')) return { icon: 'trash-can', color: Colors.danger };
    if (cat.includes('safety')) return { icon: 'security', color: Colors.danger };
    if (cat.includes('park')) return { icon: 'tree', color: Colors.secondary };
    return { icon: 'alert-decagram', color: Colors.primary };
  };

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      <MapView
        provider={PROVIDER_GOOGLE}
        style={styles.map}
        customMapStyle={MAP_STYLE}
        initialRegion={initialRegion}
      >
        {/* Render Jurisdiction Boundaries */}
        {jurisdictions.map(j => {
            if (!j.boundary_polygon || j.boundary_polygon.type !== 'Polygon') return null;
            
            // Transform GeoJSON coordinates [[lng, lat]] to RN Maps [{latitude, longitude}]
            const coords = (j.boundary_polygon.coordinates as number[][][])[0].map(c => ({
                latitude: c[1],
                longitude: c[0]
            }));

            return (
                <Polygon
                    key={j.id}
                    coordinates={coords}
                    fillColor="rgba(99, 102, 241, 0.15)"
                    strokeColor={Colors.primary}
                    strokeWidth={2}
                />
            );
        })}
        {problems.map(p => {
          const info = getMarkerInfo(p.category);
          return (
            <Marker
              key={p.id}
              coordinate={{ latitude: p.latitude, longitude: p.longitude }}
              onCalloutPress={() => navigation.navigate('ProblemDetail', { problemId: p.id })}
            >
              <View style={[styles.markerContainer, { borderColor: info.color }]}>
                <LinearGradient colors={[info.color, info.color + 'aa']} style={styles.markerGradient}>
                  <MaterialCommunityIcons name={info.icon as any} size={20} color={Colors.white} />
                </LinearGradient>
                <View style={[styles.markerArrow, { borderTopColor: info.color }]} />
              </View>
            </Marker>
          );
        })}
      </MapView>

      {/* Floating Header */}
      <View style={styles.floatingHeader}>
        <LinearGradient
          colors={[Colors.card, 'rgba(30, 41, 59, 0.7)']}
          style={styles.headerGradient}
        >
          <View style={styles.headerRow}>
            <MaterialCommunityIcons name="layers-outline" size={24} color={Colors.primary} />
            <View style={styles.headerTextContainer}>
              <Text style={styles.headerTitle}>Pulse Map (Spatial Insight)</Text>
              <Text style={styles.headerSubtitle}>{problems.length} Verified Issues Near You</Text>
            </View>
          </View>
        </LinearGradient>
      </View>

      {/* Report Button */}
      <TouchableOpacity 
        style={styles.reportBtn}
        onPress={() => navigation.navigate('SubmitProblem')}
      >
        <LinearGradient colors={[Colors.primary, '#4F46E5']} style={styles.btnGradient}>
          <MaterialCommunityIcons name="plus" size={28} color={Colors.white} />
          <Text style={styles.btnText}>REPORT HERE</Text>
        </LinearGradient>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f172a' },
  map: { width: '100%', height: '100%' },
  
  floatingHeader: { position: 'absolute', top: 60, left: 20, right: 20, borderRadius: 24, overflow: 'hidden', elevation: 10, shadowColor: '#000', shadowOpacity: 0.5, shadowRadius: 10 },
  headerGradient: { padding: 16, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  headerRow: { flexDirection: 'row', alignItems: 'center' },
  headerTextContainer: { marginLeft: 16 },
  headerTitle: { fontSize: 16, fontWeight: '800', color: Colors.text },
  headerSubtitle: { fontSize: 12, color: Colors.textSecondary },

  markerContainer: { alignItems: 'center', width: 44, height: 44 },
  markerGradient: { width: 36, height: 36, borderRadius: 18, justifyContent: 'center', alignItems: 'center', borderWidth: 2, borderColor: Colors.white },
  markerArrow: { width: 0, height: 0, borderLeftWidth: 6, borderLeftColor: 'transparent', borderRightWidth: 6, borderRightColor: 'transparent', borderTopWidth: 8, marginTop: -2 },

  reportBtn: { position: 'absolute', bottom: 30, alignSelf: 'center', borderRadius: 30, overflow: 'hidden', elevation: 8, shadowColor: Colors.primary, shadowOpacity: 0.4, shadowRadius: 10 },
  btnGradient: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 24, paddingVertical: 14 },
  btnText: { color: Colors.white, fontWeight: '900', fontSize: 14, marginLeft: 10, letterSpacing: 1 }
});

export default MapScreen;

