
import React from 'react';
import { Modal, View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../store';
import { closeLevelUpModal } from '../store/slices/authSlice';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { Colors } from '../constants/Colors';
import { BlurView } from 'expo-blur';

const LevelUpModal = () => {
    const dispatch = useDispatch<AppDispatch>();
    const { showLevelUpModal, newLevel } = useSelector((state: RootState) => state.auth);

    if (!showLevelUpModal || !newLevel) return null;

    const handleClose = () => {
        dispatch(closeLevelUpModal());
    };

    return (
        <Modal
            transparent={true}
            visible={showLevelUpModal}
            animationType="fade"
            onRequestClose={handleClose}
        >
            <View style={styles.overlay}>
                {/* Blur Background */}
                <BlurView intensity={20} style={StyleSheet.absoluteFill} tint="dark" />

                <LinearGradient
                    colors={['rgba(31, 41, 55, 0.95)', 'rgba(17, 24, 39, 0.98)']}
                    style={styles.container}
                >
                    <LinearGradient
                        colors={['rgba(245, 158, 11, 0.3)', 'transparent']}
                        style={styles.glow}
                    />

                    <View style={styles.iconContainer}>
                        <MaterialCommunityIcons name="trophy-award" size={80} color={Colors.warning} />
                        <MaterialCommunityIcons name="star-four-points" size={30} color="#FFF" style={styles.star1} />
                        <MaterialCommunityIcons name="star-four-points" size={20} color="#FFF" style={styles.star2} />
                    </View>
                    
                    <Text style={styles.subtitle}>CONGRATULATIONS!</Text>
                    <Text style={styles.title}>LEVEL {newLevel}</Text>
                    <Text style={styles.description}>
                        You've reached a new civic rank. accurate reports and verified contributions are paying off.
                    </Text>

                    <TouchableOpacity style={styles.button} onPress={handleClose}>
                        <LinearGradient
                            colors={[Colors.primary, '#4F46E5']}
                            style={styles.gradientBtn}
                        >
                            <Text style={styles.btnText}>AWESOME</Text>
                        </LinearGradient>
                    </TouchableOpacity>
                </LinearGradient>
            </View>
        </Modal>
    );
};

const styles = StyleSheet.create({
    overlay: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: 'rgba(0,0,0,0.6)',
    },
    container: {
        width: '85%',
        padding: 40,
        borderRadius: 32,
        alignItems: 'center',
        borderWidth: 1,
        borderColor: 'rgba(245, 158, 11, 0.3)',
        overflow: 'hidden',
    },
    glow: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: 150,
    },
    iconContainer: {
        marginBottom: 24,
        position: 'relative',
    },
    star1: { position: 'absolute', top: -10, right: -20, opacity: 0.8 },
    star2: { position: 'absolute', bottom: 0, left: -20, opacity: 0.6 },
    
    subtitle: {
        color: Colors.warning,
        fontWeight: '800',
        letterSpacing: 2,
        marginBottom: 8,
        fontSize: 14,
    },
    title: {
        color: '#FFF',
        fontSize: 48,
        fontWeight: '900',
        marginBottom: 16,
        textShadowColor: 'rgba(245, 158, 11, 0.5)',
        textShadowOffset: { width: 0, height: 4 },
        textShadowRadius: 10,
    },
    description: {
        color: Colors.textSecondary,
        textAlign: 'center',
        marginBottom: 32,
        lineHeight: 22,
        fontSize: 15,
    },
    button: {
        width: '100%',
        borderRadius: 16,
        overflow: 'hidden',
        shadowColor: Colors.primary,
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 12,
        elevation: 8,
    },
    gradientBtn: {
        paddingVertical: 16,
        alignItems: 'center',
    },
    btnText: {
        color: '#FFF',
        fontWeight: '800',
        fontSize: 16,
        letterSpacing: 1,
    },
});

export default LevelUpModal;
