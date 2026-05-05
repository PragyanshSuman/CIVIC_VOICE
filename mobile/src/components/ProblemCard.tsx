import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Colors } from '../constants/Colors';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { Problem } from '../types';
import { useNavigation } from '@react-navigation/native';

interface ProblemCardProps {
    item: Problem;
    compact?: boolean; // Optional prop for a smaller view if needed
}

const getStatusInfo = (status: string) => {
    switch (status) {
        case 'submitted': return { color: Colors.textSecondary, label: 'Reported' };
        case 'acknowledged': return { color: Colors.primary, label: 'Seen' };
        case 'in_progress': return { color: Colors.warning, label: 'Working' };
        case 'solved': return { color: Colors.success, label: 'Resolved' };
        case 'rejected': return { color: Colors.danger, label: 'Closed' };
        default: return { color: Colors.textSecondary, label: status };
    }
};

const getCategoryIcon = (category: string) => {
    const cat = category.toLowerCase();
    if (cat.includes('pothole') || cat.includes('road')) return 'road-variant';
    if (cat.includes('light') || cat.includes('electric')) return 'lightbulb-on-outline';
    if (cat.includes('water') || cat.includes('pipe')) return 'water-pump';
    if (cat.includes('waste') || cat.includes('trash') || cat.includes('dumping')) return 'trash-can-outline';
    return 'alert-decagram-outline';
};

const ProblemCard: React.FC<ProblemCardProps> = ({ item, compact }) => {
    const navigation = useNavigation() as any;
    const statusInfo = getStatusInfo(item.status);

    return (
        <View style={styles.cardContainer}>
            <TouchableOpacity 
                style={styles.card}
                activeOpacity={0.9}
                onPress={() => navigation.navigate('ProblemDetail', { problemId: item.id })}
            >
                <LinearGradient
                    colors={[Colors.card, 'rgba(30, 41, 59, 0.4)']}
                    style={styles.cardGradient}
                >
                    <View style={styles.cardHeader}>
                        <View style={styles.categoryBadge}>
                            <MaterialCommunityIcons name={getCategoryIcon(item.category)} size={16} color={Colors.primary} />
                            <Text style={styles.categoryText}>{item.category}</Text>
                        </View>
                        <View style={[styles.statusBadge, { backgroundColor: statusInfo.color + '20' }]}>
                            <View style={[styles.statusDot, { backgroundColor: statusInfo.color }]} />
                            <Text style={[styles.statusText, { color: statusInfo.color }]}>{statusInfo.label}</Text>
                        </View>
                    </View>

                    <Text style={styles.title} numberOfLines={1}>{item.title}</Text>
                    <Text style={styles.description} numberOfLines={2}>{item.description}</Text>

                    <View style={styles.cardFooter}>
                        <TouchableOpacity style={styles.authorContainer} onPress={() => {
                            if (item.author?.id) {
                                navigation.navigate('Profile', { userId: item.author.id }); // Navigate to Public Profile
                            }
                        }}>
                            <MaterialCommunityIcons name="account-circle-outline" size={14} color={Colors.primary} />
                            <Text style={styles.authorText}>By {item.author?.full_name || 'Citizen'}</Text>
                        </TouchableOpacity>
                        <View style={styles.locationContainer}>
                            <MaterialCommunityIcons name="map-marker-outline" size={14} color={Colors.textSecondary} />
                            <Text style={styles.locationText} numberOfLines={1}>{item.address || 'Unspecified location'}</Text>
                        </View>
                        <View style={styles.voteSummary}>
                             <MaterialCommunityIcons name="heart-outline" size={14} color={Colors.primary} />
                             <Text style={styles.voteSummaryText}>{item.upvotes_count || 0}</Text>
                        </View>
                        {/* <Text style={styles.timeText}>2h ago</Text> */}
                    </View>
                </LinearGradient>
            </TouchableOpacity>
        </View>
    );
};

const styles = StyleSheet.create({
    cardContainer: {
        marginBottom: 16,
        paddingHorizontal: 24,
    },
    card: {
        borderRadius: 20,
        overflow: 'hidden',
        // boxShadow equivalent for Android/iOS
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.3,
        shadowRadius: 12,
        elevation: 8,
    },
    cardGradient: {
        padding: 20,
        borderRadius: 20,
        borderWidth: 1,
        borderColor: 'rgba(255,255,255,0.08)',
    },
    cardHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 12,
    },
    categoryBadge: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: 'rgba(99, 102, 241, 0.1)',
        paddingHorizontal: 10,
        paddingVertical: 6,
        borderRadius: 12,
        gap: 6,
    },
    categoryText: {
        color: Colors.primary,
        fontSize: 12,
        fontWeight: '700',
        textTransform: 'uppercase',
        letterSpacing: 0.5,
    },
    statusBadge: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: 10,
        paddingVertical: 6,
        borderRadius: 12,
        gap: 6,
    },
    statusDot: { width: 6, height: 6, borderRadius: 3 },
    statusText: { fontSize: 11, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 0.5 },
    
    title: {
        fontSize: 18,
        fontWeight: '700',
        color: Colors.text,
        marginBottom: 8,
        letterSpacing: 0.2,
    },
    description: {
        fontSize: 14,
        color: Colors.textSecondary,
        marginBottom: 16,
        lineHeight: 22,
    },
    
    cardFooter: {
        flexDirection: 'row',
        alignItems: 'center',
        marginTop: 4,
        paddingTop: 16,
        borderTopWidth: 1,
        borderTopColor: 'rgba(255,255,255,0.05)',
        justifyContent: 'space-between',
    },
    authorContainer: { flexDirection: 'row', alignItems: 'center', gap: 6 },
    authorText: { fontSize: 12, color: Colors.text, fontWeight: '600' },
    
    locationContainer: { flexDirection: 'row', alignItems: 'center', gap: 4, maxWidth: '40%' },
    locationText: { fontSize: 12, color: Colors.textSecondary },
    
    voteSummary: { flexDirection: 'row', alignItems: 'center', gap: 4 },
    voteSummaryText: { fontSize: 12, color: Colors.primary, fontWeight: '700' },
    
    timeText: { fontSize: 10, color: 'rgba(255,255,255,0.2)', fontWeight: '600' },
});

export default ProblemCard;
