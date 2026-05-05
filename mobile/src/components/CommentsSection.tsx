import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, FlatList, ActivityIndicator, Alert, Image } from 'react-native';
import { useAppSelector } from '../store/hooks';
import apiClient from '../utils/api';
import { Colors } from '../constants/Colors';
import { Comment } from '../types';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';

interface CommentsSectionProps {
  problemId: string;
}

const timeAgo = (dateString: string) => {
    const now = new Date();
    const past = new Date(dateString);
    const msPerMinute = 60 * 1000;
    const msPerHour = msPerMinute * 60;
    const msPerDay = msPerHour * 24;
    const elapsed = now.getTime() - past.getTime();

    if (elapsed < msPerMinute) return 'Just now';
    else if (elapsed < msPerHour) return Math.round(elapsed/msPerMinute) + 'm ago';
    else if (elapsed < msPerDay) return Math.round(elapsed/msPerHour) + 'h ago';
    else return Math.round(elapsed/msPerDay) + 'd ago';
};

const CommentsSection: React.FC<CommentsSectionProps> = ({ problemId }) => {
  const { token, user } = useAppSelector((state) => state.auth);
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [newComment, setNewComment] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchComments();
  }, [problemId]);

  const fetchComments = async () => {
    try {
      const response = await apiClient.get(`/comments/problem/${problemId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setComments(response.data);
    } catch (error) {
      console.log('Error fetching comments', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim()) return;
    setSubmitting(true);
    try {
      const response = await apiClient.post('/comments/', {
        content: newComment,
        problem_id: problemId
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setComments([...comments, response.data]);
      setNewComment('');
    } catch (error) {
      Alert.alert('Error', 'Failed to post comment.');
    } finally {
      setSubmitting(false);
    }
  };

  const renderItem = ({ item }: { item: Comment }) => (
    <View style={styles.commentItem}>
      <View style={styles.avatar}>
        <Text style={styles.avatarText}>{item.author?.full_name?.charAt(0) || 'U'}</Text>
      </View>
      <View style={styles.commentContent}>
        <View style={styles.commentHeader}>
          <Text style={styles.authorName}>{item.author?.full_name || 'User'}</Text>
          <Text style={styles.timestamp}>{timeAgo(item.created_at)}</Text>
        </View>
        <Text style={styles.commentText}>{item.content}</Text>
      </View>
    </View>
  );

  if (loading) return <ActivityIndicator size="small" color={Colors.primary} />;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Discussion ({comments.length})</Text>
      
      <FlatList
        data={comments}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        scrollEnabled={false} // Nested in ScrollView
        contentContainerStyle={styles.list}
        ListEmptyComponent={<Text style={styles.emptyText}>No comments yet. Be the first!</Text>}
      />

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Write a comment..."
          placeholderTextColor={Colors.textSecondary}
          value={newComment}
          onChangeText={setNewComment}
          multiline
        />
        <TouchableOpacity style={styles.sendBtn} onPress={handleAddComment} disabled={submitting}>
          {submitting ? (
             <ActivityIndicator size="small" color={Colors.white} />
          ) : (
             <MaterialCommunityIcons name="send" size={20} color={Colors.white} />
          )}
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { marginTop: 24, paddingVertical: 16 },
  title: { fontSize: 18, fontWeight: '700', color: Colors.text, marginBottom: 12 },
  list: { marginBottom: 16 },
  emptyText: { color: Colors.textSecondary, fontStyle: 'italic', marginBottom: 10 },
  
  commentItem: { flexDirection: 'row', marginBottom: 16 },
  avatar: { 
    width: 32, height: 32, borderRadius: 16, backgroundColor: Colors.primary, 
    justifyContent: 'center', alignItems: 'center', marginRight: 10 
  },
  avatarText: { color: Colors.white, fontWeight: 'bold', fontSize: 14 },
  
  commentContent: { flex: 1, backgroundColor: 'rgba(255,255,255,0.05)', padding: 10, borderRadius: 12 },
  commentHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 },
  authorName: { color: Colors.text, fontWeight: '700', fontSize: 14 },
  timestamp: { color: Colors.textSecondary, fontSize: 12 },
  commentText: { color: Colors.text, fontSize: 14, lineHeight: 20 },
  
  inputContainer: { flexDirection: 'row', alignItems: 'center' },
  input: { 
    flex: 1, backgroundColor: 'rgba(255,255,255,0.05)', color: Colors.text, 
    borderRadius: 20, paddingHorizontal: 16, paddingVertical: 10, marginRight: 10,
    borderWidth: 1, borderColor: Colors.border
  },
  sendBtn: { 
    width: 40, height: 40, borderRadius: 20, backgroundColor: Colors.primary, 
    justifyContent: 'center', alignItems: 'center' 
  }
});

export default CommentsSection;
