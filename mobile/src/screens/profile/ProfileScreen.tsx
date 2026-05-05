import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, RefreshControl, Alert } from 'react-native';
import { useAppSelector, useAppDispatch } from '../../store/hooks';
import { logout } from '../../store/slices/authSlice';
import { Colors } from '../../constants/Colors';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import { UserService, UserStats } from '../../services/UserService';
import { Problem } from '../../types';
import ProblemCard from '../../components/ProblemCard';

import { useRoute, useNavigation } from '@react-navigation/native';

import QuestService, { Quest } from '../../services/QuestService';

const ProfileScreen = () => {
  const { user: currentUser } = useAppSelector((state) => state.auth);
  const route = useRoute() as any;
  const dispatch = useAppDispatch();
  const navigation = useNavigation();
  
  // If route params has userId, we are viewing public profile. Else my profile.
  const publicUserId = route.params?.userId;
  const isMyProfile = !publicUserId || (currentUser && publicUserId === currentUser.id);
  
  const [activeTab, setActiveTab] = useState<'stats' | 'history'>('stats');
  const [stats, setStats] = useState<UserStats | null>(null);
  const [history, setHistory] = useState<Problem[]>([]);
  const [userData, setUserData] = useState<any>(currentUser); // Local user data state
  const [refreshing, setRefreshing] = useState(false);

  const [quests, setQuests] = useState<Quest[]>([]);

  // Gamification Logic using `userData` (which could be public user)
  const currentLevel = userData?.level || 1;
  const currentXP = userData?.karma_points || 0;
  
  // Level Formula...
  const currentLevelMinXP = Math.pow(currentLevel * 5, 2);
  const nextLevelXP = Math.pow((currentLevel + 1) * 5, 2);
  const levelProgress = (currentXP - currentLevelMinXP) / (nextLevelXP - currentLevelMinXP);
  const progressPercent = Math.min(Math.max(levelProgress, 0), 1) * 100;

  const loadQuests = async () => {
    // Fetch Quests if my profile
    if (isMyProfile) {
        try {
            const qs = await QuestService.getAll();
            setQuests(qs);
        } catch (e) { console.log("Quest fetch failed"); }
    }
  };

  const loadProfileData = async () => {
    const targetUserId = publicUserId || currentUser?.id;
    if (!targetUserId) return;
    
    try {
      // Fetch stats, history, AND user profile if looking at someone else
      const promises: Promise<any>[] = [
        UserService.getStats(targetUserId),
        UserService.getUserProblems(targetUserId)
      ];
      
      if (!isMyProfile) {
        promises.push(UserService.getUser(targetUserId));
      }

      const results = await Promise.all(promises);
      setStats(results[0]);
      setHistory(results[1]);
      
      if (!isMyProfile) {
        setUserData(results[2]);
      } else {
        setUserData(currentUser);
      }
      
    } catch (error) {
      console.error('Failed to load profile data', error);
    }
  };

  const loadAllData = async () => {
      await Promise.all([loadQuests(), loadProfileData()]);
  };

  useEffect(() => {
    loadAllData();
    // If viewing self, keep userData synced with Redux
    if (isMyProfile && currentUser) {
        setUserData(currentUser);
    }
  }, [currentUser, publicUserId]);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadAllData();
    setRefreshing(false);
  };

  const handleClaimQuest = async (qid: string) => {
      // Demo logic
      try {
          await QuestService.claim(qid);
          Alert.alert("Quest Claimed!", "You earned XP!");
          loadAllData(); // Refresh to update progress
      } catch (e) {
          Alert.alert("Error", "Could not claim.");
      }
  };

  const renderQuests = () => (
      <View style={styles.questsContainer}>
          <Text style={styles.sectionTitle}>Daily Quests</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.questsList}>
              {quests.map(q => (
                  <LinearGradient 
                    key={q.id} 
                    colors={['#1e293b', '#0f172a']} 
                    style={styles.questCard}
                  >
                      <View style={styles.questHeader}>
                          <MaterialCommunityIcons name="star-four-points" size={16} color="#FBBF24" />
                          <Text style={styles.questXp}>{q.xp_reward} XP</Text>
                      </View>
                      <Text style={styles.questTitle}>{q.title}</Text>
                      <Text style={styles.questDesc}>{q.description}</Text>
                      <View style={styles.progressBarBg}>
                         <View style={[styles.progressBarFill, {width: '50%', backgroundColor: Colors.primary}]} />
                      </View>
                      <TouchableOpacity onPress={() => handleClaimQuest(q.id)} style={styles.claimBtn}>
                          <Text style={styles.claimText}>ACTIVE</Text>
                      </TouchableOpacity>
                  </LinearGradient>
              ))}
          </ScrollView>
      </View>
  );

  const renderTabs = () => (
    <View style={styles.tabContainer}>
      <TouchableOpacity 
        style={[styles.tabBtn, activeTab === 'stats' && styles.activeTabBtn]} 
        onPress={() => setActiveTab('stats')}
      >
        <Text style={[styles.tabText, activeTab === 'stats' && styles.activeTabText]}>Impact Stats</Text>
      </TouchableOpacity>
      <TouchableOpacity 
        style={[styles.tabBtn, activeTab === 'history' && styles.activeTabBtn]} 
        onPress={() => setActiveTab('history')}
      >
        <Text style={[styles.tabText, activeTab === 'history' && styles.activeTabText]}>My Contributions ({history.length})</Text>
      </TouchableOpacity>
    </View>
  );

  const renderStats = () => (
    <View style={styles.statsGrid}>
      {/* Accuracy Card */}
      <View style={styles.bigStatCard}>
        <LinearGradient colors={['rgba(16, 185, 129, 0.1)', 'rgba(16, 185, 129, 0.05)']} style={styles.statGradient}>
          <MaterialCommunityIcons name="shield-check" size={32} color={Colors.secondary} />
          <Text style={styles.bigStatValue}>{(stats?.verification_score || 0) * 100}%</Text>
          <Text style={styles.bigStatLabel}>Credibility Score</Text>
        </LinearGradient>
      </View>

      <View style={styles.row}>
        <View style={styles.smallStatCard}>
          <Text style={styles.statValue}>{stats?.reports_submitted || 0}</Text>
          <Text style={styles.statLabel}>Reports</Text>
        </View>
        <View style={styles.smallStatCard}>
          <Text style={[styles.statValue, { color: Colors.primary }]}>{stats?.issues_resolved || 0}</Text>
          <Text style={styles.statLabel}>Fixed</Text>
        </View>
        <View style={styles.smallStatCard}>
          <Text style={[styles.statValue, { color: Colors.warning }]}>{stats?.volunteered_count || 0}</Text>
          <Text style={styles.statLabel}>Volunteered</Text>
        </View>
      </View>
      
      <View style={styles.infoSection}>
        <Text style={styles.infoTitle}>Civic Rank</Text>
        <Text style={styles.rankName}>{stats?.impact_level || 'Citizen'}</Text>
        <Text style={styles.rankDesc}>Keep reporting and verifying issues to level up your status in the community.</Text>
      </View>
    </View>
  );

  const renderHistory = () => (
    <View style={styles.historyList}>
      {history.length === 0 ? (
        <View style={styles.emptyState}>
          <MaterialCommunityIcons name="file-document-outline" size={48} color="rgba(255,255,255,0.2)" />
          <Text style={styles.emptyText}>No contributions yet</Text>
        </View>
      ) : (
        history.map((item, index) => (
          <ProblemCard key={item.id} item={item} />
        ))
      )}
    </View>
  );

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      <LinearGradient colors={[Colors.background, '#1E293B']} style={StyleSheet.absoluteFill} />
      
      <ScrollView 
        contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.primary} />}
      >
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.avatarContainer}>
            <LinearGradient colors={[Colors.primary, '#4F46E5']} style={styles.avatarGradient}>
              <Text style={styles.avatarText}>{userData?.full_name?.charAt(0) || 'U'}</Text>
            </LinearGradient>
            <View style={styles.levelBadge}>
              <Text style={styles.levelText}>{currentLevel}</Text>
            </View>
          </View>
          
          <Text style={styles.name}>{userData?.full_name || 'Verified Citizen'}</Text>
          <Text style={styles.email}>{userData?.email}</Text>
          
          {/* XP Bar */}
          <View style={styles.xpContainer}>
            <View style={styles.xpInfo}>
              <Text style={styles.xpText}>Level {currentLevel}</Text>
              <Text style={styles.xpText}>{currentXP} XP</Text>
            </View>
            <View style={styles.progressBarBg}>
              <LinearGradient 
                colors={[Colors.secondary, '#34D399']} 
                start={{x: 0, y: 0}} end={{x: 1, y: 0}}
                style={[styles.progressBarFill, { width: `${progressPercent}%` }]} 
              />
            </View>
          </View>
        </View>

        {isMyProfile && renderQuests()}

        {/* Official Dashboard Access */}
        {isMyProfile && (['GOVERNMENT', 'ADMIN', 'government', 'admin'].includes(userData?.role)) && (
            <TouchableOpacity 
              style={styles.officialBtn}
              onPress={() => navigation.navigate('OfficialDashboard' as never)}
            >
                <MaterialCommunityIcons name="briefcase-account" size={20} color="white" />
                <Text style={styles.officialBtnText}>OPEN OFFICIAL WORKSPACE</Text>
            </TouchableOpacity>
        )}

        {renderTabs()}

        {activeTab === 'stats' ? renderStats() : renderHistory()}

        {/* Logout Button (Only show if my profile) */}
        {isMyProfile && (
            <TouchableOpacity 
            style={styles.logoutBtn} 
            onPress={() => dispatch(logout())}
            >
            <Text style={styles.logoutText}>Log Out</Text>
            </TouchableOpacity>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  content: { paddingTop: 60, paddingBottom: 40 },
  
  header: { alignItems: 'center', marginBottom: 24, paddingHorizontal: 24 },
  avatarContainer: { marginBottom: 16, position: 'relative' },
  avatarGradient: { width: 100, height: 100, borderRadius: 50, justifyContent: 'center', alignItems: 'center', borderWidth: 4, borderColor: 'rgba(255,255,255,0.05)' },
  avatarText: { color: Colors.white, fontSize: 40, fontWeight: '800' },
  
  levelBadge: { 
    position: 'absolute', bottom: 0, right: 0, 
    width: 32, height: 32, borderRadius: 16, 
    backgroundColor: Colors.secondary, 
    justifyContent: 'center', alignItems: 'center',
    borderWidth: 3, borderColor: '#0f172a',
  },
  levelText: { color: '#0f172a', fontWeight: '900', fontSize: 12 },
  
  name: { fontSize: 24, fontWeight: '800', color: Colors.text, marginBottom: 4 },
  email: { fontSize: 14, color: Colors.textSecondary, marginBottom: 16 },
  
  xpContainer: { width: '100%', maxWidth: 300, paddingHorizontal: 10 },
  xpInfo: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 },
  xpText: { color: Colors.textSecondary, fontSize: 10, fontWeight: '700', textTransform: 'uppercase' },
  progressBarBg: { height: 6, backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: 3, overflow: 'hidden' },
  progressBarFill: { height: '100%', borderRadius: 3 },

  tabContainer: { flexDirection: 'row', borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.1)', marginBottom: 24 },
  tabBtn: { flex: 1, alignItems: 'center', paddingVertical: 16 },
  activeTabBtn: { borderBottomWidth: 2, borderBottomColor: Colors.primary },
  tabText: { color: Colors.textSecondary, fontSize: 14, fontWeight: '600' },
  activeTabText: { color: Colors.primary, fontWeight: '700' },

  statsGrid: { paddingHorizontal: 24 },
  bigStatCard: { marginBottom: 16, borderRadius: 20, overflow: 'hidden' },
  statGradient: { padding: 24, alignItems: 'center', borderWidth: 1, borderColor: 'rgba(16, 185, 129, 0.2)', borderRadius: 20 },
  bigStatValue: { fontSize: 36, fontWeight: '800', color: Colors.text, marginVertical: 8 },
  bigStatLabel: { fontSize: 12, color: Colors.secondary, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 1 },

  row: { flexDirection: 'row', gap: 12, marginBottom: 24 },
  smallStatCard: { flex: 1, backgroundColor: 'rgba(255,255,255,0.03)', padding: 16, borderRadius: 16, alignItems: 'center', borderWidth: 1, borderColor: 'rgba(255,255,255,0.05)' },
  statValue: { fontSize: 20, fontWeight: '700', color: Colors.text, marginBottom: 4 },
  statLabel: { fontSize: 10, color: Colors.textSecondary, fontWeight: '600', textTransform: 'uppercase' },

  infoSection: { backgroundColor: 'rgba(99, 102, 241, 0.05)', padding: 20, borderRadius: 16, borderWidth: 1, borderColor: 'rgba(99, 102, 241, 0.1)' },
  infoTitle: { color: Colors.primary, fontSize: 12, fontWeight: '700', textTransform: 'uppercase', marginBottom: 8 },
  rankName: { color: Colors.text, fontSize: 24, fontWeight: '800', marginBottom: 8 },
  rankDesc: { color: Colors.textSecondary, fontSize: 14, lineHeight: 20 },

  historyList: { paddingTop: 8 },
  emptyState: { alignItems: 'center', padding: 40 },
  emptyText: { color: 'rgba(255,255,255,0.3)', marginTop: 16, fontWeight: '600' },

  logoutBtn: { margin: 24, padding: 16, alignItems: 'center', backgroundColor: 'rgba(239, 68, 68, 0.1)', borderRadius: 12 },
  logoutText: { color: Colors.danger, fontWeight: '700' },

  officialBtn: {
    marginHorizontal: 24, marginBottom: 24,
    backgroundColor: Colors.primary,
    padding: 16, borderRadius: 12,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 12,
    shadowColor: Colors.primary, shadowOpacity: 0.4, shadowRadius: 10, elevation: 5,
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.2)'
  },
  officialBtnText: { color: 'white', fontWeight: '800', fontSize: 14, letterSpacing: 1 },

  questsContainer: { marginBottom: 24, paddingLeft: 24 },
  sectionTitle: { color: '#FFF', fontSize: 18, fontWeight: '700', marginBottom: 16 },
  questsList: { flexDirection: 'row' },
  questCard: { width: 200, padding: 16, marginRight: 12, borderRadius: 16, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  questHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  questXp: { color: '#FBBF24', fontWeight: '700', fontSize: 12 },
  questTitle: { color: '#FFF', fontWeight: '700', fontSize: 14, marginBottom: 4 },
  questDesc: { color: Colors.textSecondary, fontSize: 11, marginBottom: 12, height: 32 },
  claimBtn: { marginTop: 12, backgroundColor: 'rgba(255,255,255,0.05)', padding: 8, borderRadius: 8, alignItems: 'center' },
  claimText: { color: Colors.primary, fontWeight: '700', fontSize: 10 }
});

export default ProfileScreen;
