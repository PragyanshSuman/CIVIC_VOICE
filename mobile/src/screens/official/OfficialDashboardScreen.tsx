import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, RefreshControl, ActivityIndicator, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Colors } from '../../constants/Colors';
import { API_URL } from '../../constants/Config';
import axios from 'axios';
import { ProblemService } from '../../services/ProblemService';
import { Problem } from '../../types';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { logout } from '../../store/slices/authSlice';
import { LinearGradient } from 'expo-linear-gradient';

const OfficialDashboardScreen = () => {
    const [problems, setProblems] = useState<Problem[]>([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [insights, setInsights] = useState<any>(null);
    const [activeTab, setActiveTab] = useState<'my' | 'queue' | 'insights'>('my');
    const navigation = useNavigation() as any;
    const dispatch = useAppDispatch();
    const { user, token } = useAppSelector((state) => state.auth);
    
    // Stats for summary
    const stats = {
        total: problems.length,
        active: problems.filter(p => p.status === 'REPORTED' || p.status === 'IN_PROGRESS').length,
        resolved: problems.filter(p => p.status === 'RESOLVED' || p.status === 'CLOSED').length
    };

    const loadData = async () => {
        try {
            setLoading(true);
            // Connect to ALL problems for the city queue
            const allProblems = await axios.get<Problem[]>(`${API_URL}/problems/`, {
                headers: { Authorization: `Bearer ${token}` } 
            }).then(res => res.data);
            
            if (activeTab === 'my') {
                // Problems assigned to ME or currently IN_PROGRESS
                setProblems(allProblems.filter(p => p.assigned_official_id === user?.id || p.status === 'IN_PROGRESS'));
            } else if (activeTab === 'queue') {
                // Show everything that is NOT resolved/closed to give full city visibility
                setProblems(allProblems.filter(p => p.status === 'REPORTED' || p.status === 'TRIAGED'));
            } else if (activeTab === 'insights') {
                const insightData = await axios.get(`${API_URL}/officials/insights`, {
                    headers: { Authorization: `Bearer ${token}` }
                }).then(res => res.data);
                setInsights(insightData);
            }
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useFocusEffect(
        useCallback(() => {
            loadData();
        }, [activeTab])
    );

    const onRefresh = () => {
        setRefreshing(true);
        loadData();
    };

    const handleUpdateStatus = async (problemId: string) => {
        Alert.alert(
            "Update Status",
            "Change the progress of this issue:",
            [
                { text: "In Progress", onPress: () => updateStatus(problemId, 'IN_PROGRESS') },
                { text: "Mark Resolved", onPress: () => updateStatus(problemId, 'RESOLVED') },
                { text: "Cancel", style: "cancel" }
            ]
        );
    };

    const updateStatus = async (id: string, status: string) => {
        try {
            await ProblemService.updateProblemStatus(id, status);
            Alert.alert("Success", `Status updated to ${status}`);
            loadData();
        } catch (error) {
            Alert.alert("Error", "Failed to update status");
        }
    };

    const renderItem = ({ item }: { item: Problem }) => (
        <TouchableOpacity 
            style={styles.card}
            onPress={() => navigation.navigate('ProblemDetail', { problemId: item.id })}
        >
            <View style={styles.header}>
                <Text style={styles.title} numberOfLines={1}>{item.title}</Text>
                <View style={[styles.badge, { backgroundColor: getStatusColor(item.status) }]}>
                    <Text style={styles.badgeText}>{item.status}</Text>
                </View>
            </View>
            <Text style={styles.desc} numberOfLines={2}>{item.description}</Text>
            <View style={styles.footer}>
                <Text style={styles.meta}>Priority: {item.escalation_level}</Text>
                <Text style={styles.meta}>Due: {item.sla_due_at ? new Date(item.sla_due_at).toLocaleDateString() : 'N/A'}</Text>
            </View>
            
            {/* Quick Actions */}
            <View style={styles.actions}>
                 <TouchableOpacity 
                    style={styles.actionBtn}
                    onPress={() => handleUpdateStatus(item.id)}
                 >
                    <Text style={styles.actionText}>UPDATE STATUS</Text>
                 </TouchableOpacity>
                 <TouchableOpacity 
                    style={[styles.actionBtn, { backgroundColor: Colors.secondary }]}
                    onPress={() => navigation.navigate('ProblemDetail', { problemId: item.id })}
                 >
                    <Text style={styles.actionText}>VIEW DETAILS</Text>
                 </TouchableOpacity>
            </View>
        </TouchableOpacity>
    );

    const getStatusColor = (status: string) => {
        switch(status) {
            case 'REPORTED': return Colors.danger;
            case 'IN_PROGRESS': return Colors.primary;
            case 'RESOLVED': return Colors.success;
            default: return Colors.textSecondary;
        }
    };

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.topBar}>
                <View>
                    <Text style={styles.headerTitle}>Pulse Room</Text>
                    <Text style={styles.officialName}>{user?.full_name || 'Official User'}</Text>
                </View>
                <View style={styles.topActions}>
                    <TouchableOpacity onPress={loadData} style={styles.iconBtn}>
                        <Ionicons name="reload" size={22} color={Colors.primary} />
                    </TouchableOpacity>
                    <TouchableOpacity 
                        onPress={() => {
                            Alert.alert("Logout", "Are you sure you want to exit the official workspace?", [
                                { text: "Cancel", style: "cancel" },
                                { text: "Logout", style: "destructive", onPress: () => dispatch(logout()) }
                            ]);
                        }} 
                        style={[styles.iconBtn, { backgroundColor: 'rgba(239, 68, 68, 0.1)' }]}
                    >
                        <Ionicons name="log-out-outline" size={22} color="#F87171" />
                    </TouchableOpacity>
                </View>
            </View>

            <View style={styles.statsBar}>
                <View style={styles.statBox}>
                    <Text style={styles.statVal}>{stats.active}</Text>
                    <Text style={styles.statLabel}>ACTIVE</Text>
                </View>
                <View style={styles.statDivider} />
                <View style={styles.statBox}>
                    <Text style={styles.statVal}>{stats.resolved}</Text>
                    <Text style={styles.statLabel}>SOLVED</Text>
                </View>
                <View style={styles.statDivider} />
                <View style={styles.statBox}>
                    <Text style={styles.statVal}>{stats.total}</Text>
                    <Text style={styles.statLabel}>TOTAL</Text>
                </View>
            </View>

            <View style={styles.tabBar}>
                <TouchableOpacity 
                    style={[styles.tab, activeTab === 'my' && styles.activeTab]}
                    onPress={() => setActiveTab('my')}
                >
                    <Text style={[styles.tabText, activeTab === 'my' && styles.activeTabText]}>MY TASKS</Text>
                </TouchableOpacity>
                <TouchableOpacity 
                    style={[styles.tab, activeTab === 'queue' && styles.activeTab]}
                    onPress={() => setActiveTab('queue')}
                >
                    <Text style={[styles.tabText, activeTab === 'queue' && styles.activeTabText]}>CITY QUEUE</Text>
                </TouchableOpacity>
                <TouchableOpacity 
                    style={[styles.tab, activeTab === 'insights' && styles.activeTab]}
                    onPress={() => setActiveTab('insights')}
                >
                    <Text style={[styles.tabText, activeTab === 'insights' && styles.activeTabText]}>INSIGHTS</Text>
                </TouchableOpacity>
            </View>

            {activeTab === 'insights' ? (
                <View style={styles.insightsContent}>
                    <View style={styles.insightCard}>
                        <MaterialCommunityIcons name="robot-outline" size={32} color={Colors.primary} />
                        <Text style={styles.insightTitle}>AI Smart Priority Engine</Text>
                        <Text style={styles.insightDesc}>
                            {insights?.ai_summary || "AI is analyzing city engagement patterns..."}
                        </Text>
                        <View style={styles.tagRow}>
                            {insights?.hotspots?.map((hs: any, idx: number) => (
                                <View key={idx} style={styles.tag}>
                                    <Text style={styles.tagText}>{hs.category}: {Math.round(hs.intensity)}</Text>
                                </View>
                            ))}
                        </View>
                    </View>
                    
                    <View style={[styles.insightCard, { borderColor: Colors.secondary }]}>
                        <MaterialCommunityIcons name="account-group-outline" size={32} color={Colors.secondary} />
                        <Text style={styles.insightTitle}>Citizen Sentiment</Text>
                        <Text style={styles.insightDesc}>{insights ? `${insights.city_sentiment}% of citizens are actively supporting city initiatives.` : "Loading sentiment analysis..."}</Text>
                    </View>
                    
                    <TouchableOpacity style={styles.broadcastBtn}>
                        <LinearGradient colors={[Colors.primary, '#4F46E5']} style={styles.broadcastGradient}>
                            <Text style={styles.broadcastText}>BROADCAST CITY UPDATE</Text>
                        </LinearGradient>
                    </TouchableOpacity>
                </View>
            ) : (
                <>
                    <View style={styles.ledgerHeader}>
                        <Text style={styles.ledgerTitle}>{activeTab === 'my' ? 'PERSONAL WORKLIST' : 'UNASSIGNED REPORTS'}</Text>
                    </View>

                    {loading ? (
                        <ActivityIndicator size="large" color={Colors.primary} />
                    ) : (
                        <FlatList
                            data={problems}
                            renderItem={renderItem}
                            keyExtractor={item => item.id}
                            contentContainerStyle={styles.list}
                            refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
                            ListEmptyComponent={
                                <View style={styles.empty}>
                                    <Text style={styles.emptyText}>No assigned tasks.</Text>
                                    <Text style={styles.emptySub}>Good job! You're all caught up.</Text>
                                </View>
                            }
                        />
                    )}
                </>
            )}

        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: Colors.background },
    topBar: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 20, paddingTop: 20, paddingBottom: 10 },
    headerTitle: { fontSize: 28, fontWeight: '900', color: Colors.text, letterSpacing: -0.5 },
    officialName: { fontSize: 13, color: Colors.textSecondary, fontWeight: '600', marginTop: -2 },
    topActions: { flexDirection: 'row', gap: 12 },
    iconBtn: { padding: 8, borderRadius: 12, backgroundColor: 'rgba(255,255,255,0.05)' },
    
    tabBar: { flexDirection: 'row', paddingHorizontal: 20, marginBottom: 15, gap: 10 },
    tab: { paddingVertical: 8, paddingHorizontal: 16, borderRadius: 20, backgroundColor: 'rgba(255,255,255,0.05)' },
    activeTab: { backgroundColor: Colors.primary },
    tabText: { fontSize: 11, fontWeight: '800', color: Colors.textSecondary },
    activeTabText: { color: 'white' },

    statsBar: { 
        flexDirection: 'row', 
        margin: 20, 
        backgroundColor: 'rgba(255,255,255,0.03)', 
        borderRadius: 20, 
        padding: 15,
        borderWidth: 1,
        borderColor: 'rgba(255,255,255,0.05)'
    },
    statBox: { flex: 1, alignItems: 'center' },
    statVal: { fontSize: 18, fontWeight: '900', color: Colors.text },
    statLabel: { fontSize: 10, fontWeight: '800', color: Colors.textSecondary, letterSpacing: 1 },
    statDivider: { width: 1, backgroundColor: 'rgba(255,255,255,0.1)', height: '100%' },

    ledgerHeader: { paddingHorizontal: 20, paddingBottom: 10, borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.05)', marginBottom: 5 },
    ledgerTitle: { fontSize: 12, fontWeight: '800', color: Colors.primary, letterSpacing: 2, textTransform: 'uppercase' },
    list: { padding: 16 },
    
    // Insights
    insightsContent: { padding: 20 },
    insightCard: { 
        padding: 24, 
        backgroundColor: 'rgba(255,255,255,0.03)', 
        borderRadius: 24, 
        marginBottom: 20,
        borderWidth: 1,
        borderColor: 'rgba(255,255,255,0.1)'
    },
    insightTitle: { fontSize: 20, fontWeight: '800', color: Colors.text, marginTop: 16, marginBottom: 8 },
    insightDesc: { fontSize: 14, color: Colors.textSecondary, lineHeight: 22, marginBottom: 16 },
    tagRow: { flexDirection: 'row', gap: 8 },
    tag: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8, backgroundColor: 'rgba(255,255,255,0.05)' },
    tagText: { fontSize: 10, fontWeight: '900', color: Colors.primary },
    broadcastBtn: { marginTop: 10, borderRadius: 16, overflow: 'hidden' },
    broadcastGradient: { paddingVertical: 18, alignItems: 'center' },
    broadcastText: { color: 'white', fontWeight: '900', letterSpacing: 1 },

    card: { 
        backgroundColor: Colors.card, 
        borderRadius: 12, 
        padding: 16, 
        marginBottom: 16,
        borderWidth: 1,
        borderColor: 'rgba(255,255,255,0.1)'
    },
    header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
    title: { fontSize: 18, fontWeight: 'bold', color: Colors.text, flex: 1, marginRight: 8 },
    badge: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 4 },
    badgeText: { fontSize: 10, fontWeight: 'bold', color: 'white' },
    desc: { fontSize: 14, color: Colors.textSecondary, marginBottom: 12 },
    footer: { flexDirection: 'row', gap: 16, marginBottom: 12 },
    meta: { fontSize: 12, color: Colors.textSecondary, fontWeight: '600' },
    actions: { flexDirection: 'row', gap: 8, borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.1)', paddingTop: 12 },
    actionBtn: { flex: 1, backgroundColor: Colors.primary, padding: 8, borderRadius: 8, alignItems: 'center' },
    actionText: { fontSize: 12, fontWeight: 'bold', color: 'white' },
    empty: { alignItems: 'center', marginTop: 100 },
    emptyText: { fontSize: 18, fontWeight: 'bold', color: Colors.text, marginBottom: 8 },
    emptySub: { fontSize: 14, color: Colors.textSecondary },
});

export default OfficialDashboardScreen;
