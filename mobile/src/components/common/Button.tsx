import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator, TouchableOpacityProps } from 'react-native';

interface CustomButtonProps extends TouchableOpacityProps {
  title: string;
  loading?: boolean;
  variant?: 'primary' | 'secondary' | 'outline';
}

export const CustomButton: React.FC<CustomButtonProps> = ({ 
  title, 
  loading = false, 
  variant = 'primary', 
  style, 
  disabled,
  ...props 
}) => {
  const getBackgroundColor = () => {
    if (disabled) return '#A0A0A0';
    switch (variant) {
      case 'primary': return '#007AFF';
      case 'secondary': return '#34C759';
      case 'outline': return 'transparent';
      default: return '#007AFF';
    }
  };

  const getTextColor = () => {
    if (variant === 'outline') return '#007AFF';
    return '#FFFFFF';
  };

  return (
    <TouchableOpacity
      style={[
        styles.container, 
        { backgroundColor: getBackgroundColor(), borderColor: variant === 'outline' ? '#007AFF' : 'transparent', borderWidth: variant === 'outline' ? 1 : 0 }, 
        style
      ]}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <ActivityIndicator color={getTextColor()} />
      ) : (
        <Text style={[styles.text, { color: getTextColor() }]}>{title}</Text>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 8,
  },
  text: {
    fontSize: 16,
    fontWeight: '600',
  },
});
