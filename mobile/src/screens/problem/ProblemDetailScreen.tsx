import React, { useEffect, useState, useMemo } from 'react';
import { View, StyleSheet, Text, ScrollView, ActivityIndicator, TouchableOpacity, Alert, Dimensions, Image, Modal, TouchableWithoutFeedback, Share } from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { Video, ResizeMode } from 'expo-av';
import { useAppSelector, useAppDispatch } from '../../store/hooks';
import { refreshProfile } from '../../store/slices/authSlice';
import { Problem, Solution, GovernmentResponse, User } from '../../types';
import { ProblemService } from '../../services/ProblemService';
import axios from 'axios';
import { API_URL } from '../../constants/Config';
import { Colors } from '../../constants/Colors';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import CommentsSection from '../../components/CommentsSection';
import { StatusBar } from 'expo-status-bar';

const { width } = Dimensions.get('window');

const ProblemDetailScreen = () => {
  const route = useRoute();
  const dispatch = useAppDispatch();
  const navigation = useNavigation() as any;
  const { user } = useAppSelector((state) => state.auth);

  const { problemId } = route.params as { problemId: string };
  const { token } = useAppSelector((state) => state.auth);
  const [problem, setProblem] = useState<Problem | null>(null);
  const [solutions, setSolutions] = useState<Solution[]>([]);
  const [governmentResponses, setGovernmentResponses] = useState<GovernmentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  
  // Action Squad State
  const [squad, setSquad] = useState<User[]>([]);
  const [joining, setJoining] = useState(false);
  const isVolunteering = useMemo(() => {
    if (!user) return false;
    return squad.some(u => u.id === user?.id);
  }, [squad, user]);

  const fetchData = async () => {
    try {
      const [probRes, solRes, govRes] = await Promise.all([
        axios.get(`${API_URL}/problems/${problemId}`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/solutions/problem/${problemId}`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/problems/${problemId}/responses`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);

      setProblem(probRes.data);
      setSolutions(solRes.data);
      setGovernmentResponses(govRes.data);
    } catch (error) {
      console.log(error);
      Alert.alert('Error', 'Failed to fetch details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [problemId]);

  const handleVote = async (id: string, type: 'UPVOTE' | 'DOWNVOTE', target: 'problem' | 'solution' = 'solution') => {
    try {
      const endpoint = target === 'problem' ? `${API_URL}/problems/${id}/vote` : `${API_URL}/solutions/${id}/vote`;
      const response = await axios.post(endpoint, null, {
        params: { vote_type: type },
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (target === 'problem') {
        setProblem(response.data);
      } else {
        setSolutions(prev => prev.map(s => s.id === id ? response.data : s));
      }
      
      dispatch(refreshProfile());
    } catch (error) {
      console.log(error);
      Alert.alert('Error', 'Voting failed.');
    }
  };

  const handleShare = async () => {
    if (!problem) return;
    try {
      await Share.share({
        message: `Check out this issue on Civic Hub: ${problem.title}\n\n${problem.description}\n\nHelp us solve it by voting! 🗳️`,
      });
    } catch (error) {
      console.log(error);
    }
  };


  const handleVolunteer = async () => {
    try {
        setJoining(true);
        const res = await ProblemService.joinSquad(problemId);
        
        if (res.joined) {
            // Add self to squad
             if (user) setSquad(prev => [...prev, user]);
             Alert.alert("Success", "You joined the Action Squad! Thank you for volunteering.");
        } else {
            // Remove self
            if (user) setSquad(prev => prev.filter(u => u.id !== user.id));
            Alert.alert("Status Updated", "You have left the squad.");
        }
    } catch (error) {
        Alert.alert("Error", "Failed to update volunteer status.");
    } finally {
        setJoining(false);
    }
  };

  const [verified, setVerified] = useState(false);

  const handleVerifyResolution = async (isResolved: boolean) => {
    try {
        const res = await ProblemService.verifyResolution(problemId, isResolved);
        setVerified(true);
        Alert.alert("Verified!", res.message);
        dispatch(refreshProfile());
        // Reload problem to show CLOSED status
        fetchData();
    } catch (error) {
        Alert.alert("Error", "Failed to submit verification.");
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={Colors.primary} />
      </View>
    );
  }

  if (!problem) return null;

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      <LinearGradient colors={[Colors.background, '#1E293B']} style={StyleSheet.absoluteFill} />
      
      <ScrollView contentContainerStyle={styles.content}>
        {/* Main Problem Card */}
        <LinearGradient
          colors={[Colors.card, 'rgba(30, 41, 59, 0.5)']}
          style={styles.mainCard}
        >
          <View style={styles.cardHeader}>
            <Text style={styles.category}>{problem.category}</Text>
            <View style={styles.statusBadge}>
              <Text style={styles.statusText}>{problem.status.replace('_', ' ')}</Text>
            </View>
            <TouchableOpacity onPress={handleShare} style={styles.shareBtn}>
              <MaterialCommunityIcons name="share-variant-outline" size={20} color={Colors.primary} />
            </TouchableOpacity>
          </View>
          
          <Text style={styles.title}>{problem.title}</Text>
          <Text style={styles.description}>{problem.description}</Text>
          
          <View style={styles.locationContainer}>
            <MaterialCommunityIcons name="map-marker-radius-outline" size={18} color={Colors.primary} />
            <Text style={styles.locationText}>{problem.address || 'Central District'}</Text>
          </View>

          {/* Citizen Consensus Voting */}
          <View style={styles.problemVoteBar}>
            <TouchableOpacity 
              onPress={() => handleVote(problemId, 'UPVOTE', 'problem')} 
              style={[styles.probVoteBtn, { backgroundColor: 'rgba(99, 102, 241, 0.1)' }]}
            >
              <MaterialCommunityIcons name="arrow-up-bold-outline" size={24} color={Colors.primary} />
              <Text style={styles.probVoteCount}>{problem.upvotes_count || 0}</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              onPress={() => handleVote(problemId, 'DOWNVOTE', 'problem')} 
              style={[styles.probVoteBtn, { backgroundColor: 'rgba(239, 68, 68, 0.1)' }]}
            >
              <MaterialCommunityIcons name="arrow-down-bold-outline" size={24} color={Colors.danger} />
              <Text style={styles.probVoteCount}>{problem.downvotes_count || 0}</Text>
            </TouchableOpacity>
            
            <View style={styles.consensusIndicator}>
                <Text style={styles.consensusLabel}>COMMUNITY CONSENSUS</Text>
                <View style={styles.consensusTrack}>
                    <View style={[styles.consensusFill, { width: `${Math.round((problem.upvotes_count / (problem.upvotes_count + problem.downvotes_count + 1)) * 100)}%` }]} />
                </View>
            </View>
          </View>

          {/* Media Section */}
          {(problem.image_url || (problem.media_attachments && problem.media_attachments.length > 0)) && (
            <View style={styles.mediaContainer}>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.mediaScroll}>
                {problem.image_url && !problem.media_attachments?.length && (
                   <TouchableOpacity onPress={() => setSelectedImage(problem.image_url!.startsWith('http') ? problem.image_url! : `${API_URL.replace('/api/v1', '')}${problem.image_url!}`)}>
                     <Image 
                      source={{ uri: problem.image_url!.startsWith('http') ? problem.image_url : `${API_URL.replace('/api/v1', '')}${problem.image_url}` }} 
                      style={styles.mediaItem} 
                     />
                   </TouchableOpacity>
                )}
                
                {problem.media_attachments?.map((media, index) => {
                  const fullUrl = media.file_url.startsWith('http') ? media.file_url : `${API_URL.replace('/api/v1', '')}${media.file_url}`;
                  return (
                    <View key={index} style={styles.mediaWrapper}>
                      {media.media_type === 'video' ? (
                        <Video
                          source={{ uri: fullUrl }}
                          style={styles.mediaItem}
                          resizeMode={ResizeMode.COVER}
                          useNativeControls
                          isLooping
                        />
                      ) : (
                        <TouchableOpacity onPress={() => setSelectedImage(fullUrl)}>
                          <Image source={{ uri: fullUrl }} style={styles.mediaItem} />
                        </TouchableOpacity>
                      )}
                    </View>
                  );
                })}
              </ScrollView>
            </View>
          )}
        </LinearGradient>

        {/* Image Modal */}
        <Modal visible={!!selectedImage} transparent={true} animationType="fade" onRequestClose={() => setSelectedImage(null)}>
          <TouchableWithoutFeedback onPress={() => setSelectedImage(null)}>
            <View style={styles.modalContainer}>
              <Image source={{ uri: selectedImage || '' }} style={styles.fullImage} resizeMode="contain" />
            </View>
          </TouchableWithoutFeedback>
        </Modal>

        {/* Official Response Section */}
        {governmentResponses.length > 0 && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <MaterialCommunityIcons name="shield-check-outline" size={24} color={Colors.secondary} />
              <Text style={styles.sectionTitle}>Official Feedback</Text>
            </View>
            
            {governmentResponses.map(resp => (
              <LinearGradient
                key={resp.id}
                colors={['rgba(16, 185, 129, 0.1)', 'rgba(16, 185, 129, 0.05)']}
                style={styles.govResponseCard}
              >
                <Text style={styles.govText}>{resp.response_text}</Text>
                {resp.action_plan && (
                  <View style={styles.actionPlanContainer}>
                    <Text style={styles.actionPlanTitle}>ACTION PLAN</Text>
                    <Text style={styles.actionPlanText}>{resp.action_plan}</Text>
                  </View>
                )}
                <Text style={styles.govMeta}>Verified Official • 1d ago</Text>
              </LinearGradient>
            ))}
          </View>
        )}

        {/* Resolution Verification (For Reporter) */}
        {problem.status === 'RESOLVED' && user?.id === problem.user_id && (
           <View style={styles.section}>
             <LinearGradient
                 colors={['rgba(16, 185, 129, 0.1)', 'rgba(16, 185, 129, 0.05)']}
                 style={styles.verifyCard}
             >
                 <View style={styles.verifyHeader}>
                     <MaterialCommunityIcons name="check-decagram" size={24} color="#10B981" />
                     <View style={styles.verifyTextContainer}>
                         <Text style={[styles.verifyTitle, { color: '#10B981' }]}>RESOLUTION VERIFICATION</Text>
                         <Text style={styles.verifySubtitle}>The official has marked this as resolved. Is it fixed?</Text>
                     </View>
                 </View>
                 
                 <View style={styles.verifyActions}>
                     <TouchableOpacity 
                         style={[styles.verifyBtn, { backgroundColor: 'rgba(16, 185, 129, 0.2)' }]}
                         onPress={() => handleVerifyResolution(true)}
                     >
                         <Text style={[styles.verifyBtnText, { color: '#34D399' }]}>YES, IT'S FIXED</Text>
                     </TouchableOpacity>
                     
                     <TouchableOpacity 
                         style={[styles.verifyBtn, { backgroundColor: 'rgba(239, 68, 68, 0.2)' }]}
                         onPress={() => handleVerifyResolution(false)}
                     >
                         <Text style={[styles.verifyBtnText, { color: '#F87171' }]}>NO, STILL BROKEN</Text>
                     </TouchableOpacity>
                 </View>
             </LinearGradient>
           </View>
        )}


        {/* Solutions Section */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <MaterialCommunityIcons name="lightbulb-group-outline" size={24} color={Colors.primary} />
            <Text style={styles.sectionTitle}>Proposed Solutions ({solutions.length})</Text>
          </View>
          
          {solutions.length === 0 ? (
            <Text style={styles.emptyText}>Be the first to propose a solution.</Text>
          ) : (
            solutions.map((sol) => (
              <LinearGradient
                key={sol.id}
                colors={['rgba(255,255,255,0.03)', 'rgba(255,255,255,0.01)']}
                style={styles.solCard}
              >
                <View style={styles.solHeader}>
                  <Text style={styles.solTitle}>{sol.title}</Text>
                  <View style={styles.consensusBadge}>
                    <Text style={styles.consensusText}>
                      {Math.round((sol.upvotes_count / (sol.upvotes_count + sol.downvotes_count + 1)) * 100)}% Match
                    </Text>
                  </View>
                </View>

                <Text style={styles.solDesc}>{sol.description}</Text>

                {/* AI Score Breakdown */}
                <View style={styles.aiContainer}>
                  <Text style={styles.aiTitle}>AI TRANSFORMATION IMPACT</Text>
                  <View style={styles.aiGrid}>
                    <View style={styles.aiItem}>
                      <Text style={styles.aiLabel}>Feasibility</Text>
                      <View style={styles.aiBarBg}>
                        <View style={[styles.aiBarFill, { width: `${sol.ai_score_feasibility * 10}%` }]} />
                      </View>
                    </View>
                    <View style={styles.aiItem}>
                      <Text style={styles.aiLabel}>Social Impact</Text>
                      <View style={styles.aiBarBg}>
                        <View style={[styles.aiBarFill, { width: `${sol.ai_score_impact * 10}%`, backgroundColor: Colors.secondary }]} />
                      </View>
                    </View>
                  </View>
                </View>

                {/* Voting Footer */}
                <View style={styles.solFooter}>
                  <View style={styles.voteContainer}>
                    <TouchableOpacity onPress={() => handleVote(sol.id, 'UPVOTE', 'solution')} style={styles.voteBtn}>
                      <MaterialCommunityIcons name="heart-outline" size={20} color={Colors.primary} />
                      <Text style={styles.voteCount}>{sol.upvotes_count}</Text>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={() => handleVote(sol.id, 'DOWNVOTE', 'solution')} style={styles.voteBtn}>
                      <MaterialCommunityIcons name="heart-broken-outline" size={20} color={Colors.danger} />
                      <Text style={styles.voteCount}>{sol.downvotes_count}</Text>
                    </TouchableOpacity>
                  </View>
                  <TouchableOpacity style={styles.commentBtn}>
                    <MaterialCommunityIcons name="chat-outline" size={18} color={Colors.textSecondary} />
                  </TouchableOpacity>
                </View>
              </LinearGradient>
            ))
          )}
        </View>

        {/* Official Actions */}
        {user && (user.role === 'GOVERNMENT' || user.role === 'ADMIN' || user.role === 'government') && (
            <TouchableOpacity 
              style={[styles.submitBtn, { backgroundColor: Colors.secondary, marginBottom: 16 }]}
              onPress={() => navigation.navigate('CreateWorkOrder', { problemId })}
            >
              <LinearGradient colors={[Colors.secondary, '#059669']} style={styles.submitGradient}>
                <Text style={styles.submitBtnText}>CREATE WORK ORDER</Text>
              </LinearGradient>
            </TouchableOpacity>
        )}

        <TouchableOpacity 
          style={styles.submitBtn}
          onPress={() => navigation.navigate('SubmitSolution', { problemId })}
        >
          <LinearGradient colors={[Colors.primary, '#4F46E5']} style={styles.submitGradient}>
            <Text style={styles.submitBtnText}>PROPOSE INNOVATION</Text>
          </LinearGradient>
        </TouchableOpacity>

        {/* Community Discussion */}
        <CommentsSection problemId={problemId} />
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  
  squadCard: { padding: 20, borderRadius: 16, borderWidth: 1, borderColor: 'rgba(245, 158, 11, 0.2)', marginBottom: 16 },
  squadHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  squadTitle: { color: Colors.warning, fontWeight: '800', letterSpacing: 1, fontSize: 12, marginBottom: 4 },
  squadSubtitle: { color: Colors.textSecondary, fontSize: 13, maxWidth: 200 },
  joinBtn: { backgroundColor: Colors.warning, paddingVertical: 10, paddingHorizontal: 16, borderRadius: 12, width: 120, alignItems: 'center' },
  leaveBtn: { backgroundColor: 'rgba(255,255,255,0.1)' },
  joinedBtn: { backgroundColor: '#10B981', borderWidth: 1, borderColor: '#34D399' },
  joinBtnText: { color: Colors.background, fontWeight: '800', fontSize: 11 },
  memberAvatars: { flexDirection: 'row', paddingLeft: 12 },
  memberAvatar: { width: 36, height: 36, borderRadius: 18, overflow: 'hidden', borderWidth: 2, borderColor: '#0f172a' },
  avatarGradient: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  avatarText: { color: Colors.white, fontWeight: '800', fontSize: 14 },
  moreText: { color: Colors.white, fontWeight: '700', fontSize: 10 },

  verifyCard: { padding: 20, borderRadius: 16, borderWidth: 1, borderColor: 'rgba(59, 130, 246, 0.2)', marginBottom: 16 },
  verifyHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  verifyTextContainer: { marginLeft: 12 },
  verifyTitle: { color: '#60A5FA', fontWeight: '800', letterSpacing: 1, fontSize: 12 },
  verifySubtitle: { color: Colors.textSecondary, fontSize: 11 },
  verifyQuestion: { color: Colors.text, fontSize: 16, fontWeight: '600', marginBottom: 16 },
  verifyActions: { flexDirection: 'row', gap: 12 },
  verifyBtn: { flex: 1, paddingVertical: 12, borderRadius: 12, alignItems: 'center' },
  verifyBtnText: { fontWeight: '700', fontSize: 13 },
  verifiedSuccess: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 10, backgroundColor: 'rgba(16, 185, 129, 0.1)', borderRadius: 12 },
  verifiedText: { color: '#34D399', fontWeight: '800', marginLeft: 8, fontSize: 14 },

  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  content: { padding: 20, paddingBottom: 40 },
  
  mainCard: { 
    padding: 24, 
    borderRadius: 32, 
    marginBottom: 32, 
    borderWidth: 1, 
    borderColor: 'rgba(255,255,255,0.1)' 
  },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 16 },
  category: { color: Colors.primary, fontSize: 13, fontWeight: '800', textTransform: 'uppercase', letterSpacing: 1 },
  statusBadge: { backgroundColor: 'rgba(255,255,255,0.05)', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20 },
  statusText: { color: Colors.text, fontSize: 11, fontWeight: 'bold', textTransform: 'uppercase' },
  shareBtn: { padding: 8, backgroundColor: 'rgba(99, 102, 241, 0.1)', borderRadius: 20, marginLeft: 8 },
  
  title: { fontSize: 28, fontWeight: '800', color: Colors.text, marginBottom: 16, lineHeight: 34 },
  description: { fontSize: 16, color: Colors.textSecondary, lineHeight: 26, marginBottom: 20 },
  locationContainer: { flexDirection: 'row', alignItems: 'center' },
  locationText: { color: Colors.text, fontSize: 14, marginLeft: 8 },

  mediaContainer: { marginTop: 24 },
  mediaScroll: { paddingRight: 20 },
  mediaWrapper: { marginRight: 16, borderRadius: 16, overflow: 'hidden', backgroundColor: '#000' },
  mediaItem: { width: 280, height: 180, borderRadius: 16 },

  section: { marginBottom: 32 },
  sectionHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 16 },
  sectionTitle: { fontSize: 20, fontWeight: 'bold', color: Colors.text, marginLeft: 12 },
  
  govResponseCard: { padding: 20, borderRadius: 24, borderLeftWidth: 4, borderLeftColor: Colors.secondary },
  govText: { fontSize: 15, color: Colors.text, lineHeight: 22, fontWeight: '500' },
  actionPlanContainer: { marginTop: 16, padding: 16, backgroundColor: 'rgba(0,0,0,0.2)', borderRadius: 16 },
  actionPlanTitle: { fontSize: 11, fontWeight: '900', color: Colors.secondary, marginBottom: 8, letterSpacing: 1 },
  actionPlanText: { fontSize: 14, color: Colors.textSecondary, lineHeight: 20 },
  govMeta: { marginTop: 16, fontSize: 12, color: Colors.textSecondary, fontStyle: 'italic' },

  solCard: { padding: 20, borderRadius: 24, marginBottom: 16, borderWidth: 1, borderColor: 'rgba(255,255,255,0.05)' },
  solHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 },
  solTitle: { fontSize: 18, fontWeight: 'bold', color: Colors.text, flex: 1, marginRight: 10 },
  consensusBadge: { backgroundColor: 'rgba(99, 102, 241, 0.1)', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 8 },
  consensusText: { color: Colors.primary, fontSize: 10, fontWeight: '900' },
  solDesc: { fontSize: 14, color: Colors.textSecondary, lineHeight: 20, marginBottom: 20 },

  aiContainer: { backgroundColor: 'rgba(255,255,255,0.03)', padding: 16, borderRadius: 16, marginBottom: 20 },
  aiTitle: { fontSize: 10, fontWeight: '900', color: Colors.textSecondary, marginBottom: 12, letterSpacing: 1 },
  aiGrid: { gap: 12 },
  aiItem: { gap: 8 },
  aiLabel: { fontSize: 12, color: Colors.text, fontWeight: '600' },
  aiBarBg: { height: 6, backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: 3, overflow: 'hidden' },
  aiBarFill: { height: '100%', backgroundColor: Colors.primary, borderRadius: 3 },

  solFooter: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  voteContainer: { flexDirection: 'row', gap: 16 },
  voteBtn: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  voteCount: { color: Colors.text, fontSize: 13, fontWeight: '600' },
  commentBtn: { padding: 4 },

  emptyText: { color: Colors.textSecondary, fontStyle: 'italic', textAlign: 'center', marginVertical: 20 },
  submitBtn: { borderRadius: 24, overflow: 'hidden', marginTop: 10 },
  submitGradient: { paddingVertical: 18, alignItems: 'center' },
  submitBtnText: { color: Colors.white, fontSize: 16, fontWeight: '900', letterSpacing: 1 },

  // Voting & Consensus Styles
  problemVoteBar: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    marginTop: 24, 
    gap: 12,
    backgroundColor: 'rgba(255,255,255,0.02)',
    padding: 12,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)'
  },
  probVoteBtn: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    paddingHorizontal: 12, 
    paddingVertical: 8, 
    borderRadius: 12, 
    gap: 8 
  },
  probVoteCount: { color: Colors.text, fontWeight: '800', fontSize: 16 },
  consensusIndicator: { flex: 1, marginLeft: 8 },
  consensusLabel: { color: Colors.textSecondary, fontSize: 9, fontWeight: '900', letterSpacing: 1, marginBottom: 6 },
  consensusTrack: { height: 4, backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: 2, overflow: 'hidden' },
  consensusFill: { height: '100%', backgroundColor: Colors.primary },

  // Modal
  modalContainer: { flex: 1, backgroundColor: 'rgba(0,0,0,0.95)', justifyContent: 'center', alignItems: 'center' },
  fullImage: { width: '100%', height: '80%' }
});

export default ProblemDetailScreen;

