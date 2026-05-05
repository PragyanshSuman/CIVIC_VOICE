import React, { useEffect, useState } from 'react';
import { View, StyleSheet, Text, FlatList, TouchableOpacity, RefreshControl } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import axios from 'axios';
import { API_URL } from '../../constants/Config';
import { Colors } from '../../constants/Colors';
import { useAppSelector } from '../../store/hooks';
import { Notification } from '../../types';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';

const NotificationScreen = () => {
  const navigation = useNavigation();
  const { token } = useAppSelector((state) => state.auth);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchNotifications = async () => {
    try {
      const response = await axios.get(`${API_URL}/notifications/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNotifications(response.data);
    } catch (error) {
      console.log('Error fetching notifications', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const markAsRead = async (id: string) => {
    try {
      await axios.post(`${API_URL}/notifications/${id}/read`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      // Update local state
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
    } catch (error) {
      console.log('Error marking read', error);
    }
  };

  const handleNotificationPress = async (item: Notification) => {
    if (!item.is_read) {
      markAsRead(item.id);
    }
    
    if (item.resource_type === 'problem' && item.resource_id) {
      (navigation as any).navigate('ProblemDetail', { problemId: item.resource_id });
    } else if (item.resource_type === 'solution' && item.resource_id) {
       // Logic for solution navigation if needed
    }
  };

  const renderItem = ({ item }: { item: Notification }) => (
    <TouchableOpacity onPress={() => handleNotificationPress(item)} activeOpacity={0.8}>
      <LinearGradient
        colors={item.is_read 
          ? ['rgba(255,255,255,0.02)', 'rgba(255,255,255,0.01)'] 
          : ['rgba(99, 102, 241, 0.15)', 'rgba(99, 102, 241, 0.05)']}
        style={[styles.card, !item.is_read && styles.unreadCard]}
      >
        <View style={styles.iconContainer}>
          <MaterialCommunityIcons 
            name={item.is_read ? "bell-outline" : "bell-ring"} 
            size={24} 
            color={item.is_read ? Colors.textSecondary : Colors.primary} 
          />
        </View>
        <View style={styles.content}>
          <Text style={[styles.cardTitle, !item.is_read && styles.unreadText]}>{item.title}</Text>
          <Text style={styles.cardMessage}>{item.message}</Text>
          <Text style={styles.timestamp}>{new Date(item.created_at).toLocaleDateString()}</Text>
        </View>
        {!item.is_read && <View style={styles.dot} />}
      </LinearGradient>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      <LinearGradient colors={[Colors.background, '#1E293B']} style={StyleSheet.absoluteFill} />
      
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
            <MaterialCommunityIcons name="arrow-left" size={24} color={Colors.white} />
        </TouchableOpacity>
        <Text style={styles.title}>Notifications</Text>
      </View>

      <FlatList
        data={notifications}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); fetchNotifications(); }} tintColor={Colors.primary} />
        }
        ListEmptyComponent={
          !loading ? (
            <View style={styles.center}>
              <MaterialCommunityIcons name="bell-sleep-outline" size={48} color={Colors.textSecondary} />
              <Text style={styles.emptyText}>No notifications yet</Text>
            </View>
          ) : null
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  header: { 
    paddingTop: 60, paddingBottom: 20, paddingHorizontal: 24, 
    flexDirection: 'row', alignItems: 'center' 
  },
  backBtn: { marginRight: 16 },
  title: { fontSize: 24, fontWeight: '800', color: Colors.white },
  
  list: { padding: 20 },
  center: { alignItems: 'center', marginTop: 100, gap: 16 },
  emptyText: { color: Colors.textSecondary, fontSize: 16 },

  card: {
    flexDirection: 'row', alignItems: 'center',
    padding: 16, marginBottom: 12, borderRadius: 16,
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.05)'
  },
  unreadCard: { borderColor: 'rgba(99, 102, 241, 0.3)' },
  
  iconContainer: { 
    width: 40, height: 40, borderRadius: 20, 
    backgroundColor: 'rgba(255,255,255,0.05)', 
    justifyContent: 'center', alignItems: 'center', marginRight: 16 
  },
  
  content: { flex: 1 },
  cardTitle: { color: Colors.text, fontSize: 16, fontWeight: '600', marginBottom: 4 },
  unreadText: { color: Colors.white, fontWeight: '800' },
  cardMessage: { color: Colors.textSecondary, fontSize: 14, lineHeight: 20 },
  timestamp: { color: Colors.textSecondary, fontSize: 10, marginTop: 6 },
  
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: Colors.primary, marginLeft: 8 }
});

export default NotificationScreen;
