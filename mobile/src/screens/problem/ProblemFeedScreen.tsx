import React, { useEffect, useState, useRef, useCallback } from 'react';
import { View, FlatList, StyleSheet, Text, RefreshControl, TouchableOpacity, Animated, Dimensions } from 'react-native';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { useAppSelector } from '../../store/hooks';
import axios from 'axios';
import { API_URL } from '../../constants/Config';
import { Problem, Notification } from '../../types';
import { Colors } from '../../constants/Colors';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import ProblemCard from '../../components/ProblemCard';

const { width } = Dimensions.get('window');

const ProblemFeedScreen = () => {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [loading, setLoading] = useState(true);
  const { token, user } = useAppSelector((state) => state.auth);
  const navigation = useNavigation() as any;

  const scrollY = useRef(new Animated.Value(0)).current;
  const bellScale = useRef(new Animated.Value(1)).current;
  const [hasUnread, setHasUnread] = useState(false);

  const fetchProblems = async () => {
    try {
      const response = await axios.get<Problem[]>(`${API_URL}/problems/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProblems(response.data);
    } catch (error) {
      console.log(error);
    } finally {
      setLoading(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      fetchProblems();
      checkNotifications();
    }, [token])
  );

  const checkNotifications = async () => {
    try {
      const response = await axios.get<Notification[]>(`${API_URL}/notifications/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const unread = response.data.some(n => !n.is_read);
      setHasUnread(unread);
      if (unread) {
        startBellAnimation();
      }
    } catch (error) {
      console.log('Error checking notifs', error);
    }
  };

  const startBellAnimation = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(bellScale, { toValue: 1.2, duration: 500, useNativeDriver: true }),
        Animated.timing(bellScale, { toValue: 1, duration: 500, useNativeDriver: true })
      ])
    ).start();
  };

  const getStatusInfo = (status: string) => {
    switch (status.toUpperCase()) {
      case 'REPORTED': return { color: Colors.danger, label: 'Reported' };
      case 'TRIAGED': return { color: Colors.warning, label: 'Triaged' };
      case 'ACKNOWLEDGED': return { color: Colors.primary, label: 'Acknow' };
      case 'IN_PROGRESS': return { color: Colors.primary, label: 'Fixing' };
      case 'RESOLVED': return { color: Colors.secondary, label: 'Resolved' };
      case 'CLOSED': return { color: Colors.secondary, label: 'Closed' };
      default: return { color: Colors.textSecondary, label: status };
    }
  };

  const getCategoryIcon = (category: string): any => {
    const cat = category.toLowerCase();
    if (cat.includes('road') || cat.includes('pothole')) return 'road-variant';
    if (cat.includes('light')) return 'lightbulb-on-outline';
    if (cat.includes('waste') || cat.includes('trash') || cat.includes('dumping')) return 'trash-can-outline';
    return 'alert-decagram-outline';
  };

  const renderHeader = () => (
    <View style={styles.headerContainer}>
      <View style={styles.headerTop}>
        <Text style={styles.welcomeText}>Hello, {user?.full_name?.split(' ')[0] || 'Citizen'}</Text>
        <TouchableOpacity onPress={() => navigation.navigate('Notifications')} style={styles.bellBtn}>
          <Animated.View style={{ transform: [{ scale: hasUnread ? bellScale : 1 }] }}>
            <MaterialCommunityIcons name={hasUnread ? "bell-ring" : "bell-outline"} size={24} color={hasUnread ? Colors.warning : Colors.white} />
          </Animated.View>
        </TouchableOpacity>
      </View>
      <Text style={styles.headerTitle}>The City Pulse</Text>
      
      <View style={styles.statsRow}>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{problems.length}</Text>
          <Text style={styles.statLabel}>Reports</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={[styles.statValue, { color: Colors.secondary }]}>
            {problems.filter(p => p.status === 'solved').length}
          </Text>
          <Text style={styles.statLabel}>Resolved</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={[styles.statValue, { color: Colors.primary }]}>
            {Math.floor(Math.random() * 50 + 50)}%
          </Text>
          <Text style={styles.statLabel}>Consensus</Text>
        </View>
      </View>
    </View>
  );

  const renderItem = ({ item, index }: { item: Problem, index: number }) => {
    return <ProblemCard item={item} />;
  };

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      <LinearGradient colors={[Colors.background, '#1E293B']} style={StyleSheet.absoluteFill} />
      
      <Animated.FlatList
        data={problems}
        renderItem={renderItem}
        keyExtractor={(item) => item.id}
        ListHeaderComponent={renderHeader}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl 
            refreshing={loading} 
            onRefresh={fetchProblems} 
            tintColor={Colors.white}
          />
        }
        onScroll={Animated.event(
          [{ nativeEvent: { contentOffset: { y: scrollY } } }],
          { useNativeDriver: true }
        )}
      />

      <TouchableOpacity 
        style={styles.fab} 
        onPress={() => navigation.navigate('SubmitProblem')}
      >
        <LinearGradient
          colors={[Colors.primary, '#4F46E5']}
          style={styles.fabGradient}
        >
          <MaterialCommunityIcons name="plus" size={30} color={Colors.white} />
        </LinearGradient>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  listContent: { padding: 20, paddingBottom: 100 },
  headerContainer: { marginBottom: 30, marginTop: 10 },
  headerTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 },
  welcomeText: { fontSize: 16, color: Colors.textSecondary },
  bellBtn: { padding: 8, backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 12 },
  headerTitle: { fontSize: 32, fontWeight: '800', color: Colors.text, marginBottom: 24, letterSpacing: -0.5 },
  statsRow: { flexDirection: 'row', justifyContent: 'space-between' },
  statCard: { 
    backgroundColor: 'rgba(255,255,255,0.05)', 
    padding: 16, 
    borderRadius: 16, 
    width: (width - 60) / 3,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)'
  },
  statValue: { fontSize: 20, fontWeight: 'bold', color: Colors.text, marginBottom: 4 },
  statLabel: { fontSize: 12, color: Colors.textSecondary, textTransform: 'uppercase', letterSpacing: 1 },
  
  cardContainer: { marginBottom: 16 },
  card: {
    borderRadius: 24,
    overflow: 'hidden',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  cardGradient: { padding: 20, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 16, alignItems: 'center' },
  categoryBadge: { flexDirection: 'row', alignItems: 'center', backgroundColor: 'rgba(99, 102, 241, 0.1)', paddingHorizontal: 10, paddingVertical: 6, borderRadius: 12 },
  categoryText: { color: Colors.primary, fontSize: 12, fontWeight: 'bold', marginLeft: 6, textTransform: 'uppercase' },
  statusBadge: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 10, paddingVertical: 6, borderRadius: 12 },
  statusDot: { width: 6, height: 6, borderRadius: 3, marginRight: 6 },
  statusText: { fontSize: 11, fontWeight: 'bold', textTransform: 'uppercase' },
  
  title: { fontSize: 20, fontWeight: 'bold', color: Colors.text, marginBottom: 8 },
  description: { fontSize: 14, color: Colors.textSecondary, lineHeight: 20, marginBottom: 20 },
  
  cardFooter: { flexDirection: 'column', gap: 12, paddingTop: 16, borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.05)' },
  authorContainer: { flexDirection: 'row', alignItems: 'center' },
  authorText: { fontSize: 13, fontWeight: '700', color: Colors.text, marginLeft: 4 },
  locationContainer: { flexDirection: 'row', alignItems: 'center', flex: 1, marginRight: 10 },
  locationText: { fontSize: 12, color: Colors.textSecondary, marginLeft: 4 },
  footerBottomRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  timeText: { fontSize: 12, color: '#475569' },
  
  fab: {
    position: 'absolute',
    right: 24,
    bottom: 30,
    borderRadius: 30,
    elevation: 8,
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 10,
  },
  fabGradient: { width: 64, height: 64, borderRadius: 32, justifyContent: 'center', alignItems: 'center' }
});

export default ProblemFeedScreen;

