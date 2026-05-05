
import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';
import apiClient from '../../utils/api';
import { User } from '../../types';

interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    loading: boolean;
    error: string | null;
    showLevelUpModal: boolean;
    newLevel: number | null;
}

const initialState: AuthState = {
    user: null,
    token: null,
    isAuthenticated: false,
    loading: false,
    error: null,
    showLevelUpModal: false,
    newLevel: null,
};

// Async Thunk for Login
export const loginUser = createAsyncThunk(
    'auth/login',
    async (credentials: any, { rejectWithValue }) => {
        try {
            // 1. Get Token
            const formData = new FormData();
            formData.append('username', credentials.email);
            formData.append('password', credentials.password);

            const response = await apiClient.post('/auth/login', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            const { access_token } = response.data;

            // 2. Get User Profile using the new token
            const userResponse = await apiClient.get('/users/me', {
                headers: { Authorization: `Bearer ${access_token}` }
            });

            return { token: access_token, user: userResponse.data };
        } catch (err: any) {
            return rejectWithValue(err.response?.data?.detail || 'Login failed');
        }
    }
);

// Async Thunk to Refresh Profile (for Gamification updates)
export const refreshProfile = createAsyncThunk(
    'auth/refresh',
    async (_, { getItem, getState, rejectWithValue }: any) => {
        try {
            const state = getState();
            const token = state.auth.token;
            if (!token) return rejectWithValue('No token');

            const response = await apiClient.get('/users/me', {
                headers: { Authorization: `Bearer ${token}` }
            });
            return response.data;
        } catch (err: any) {
            return rejectWithValue(err.message);
        }
    }
);

// Async Thunk for Signup
export const signupUser = createAsyncThunk(
    'auth/signup',
    async (userData: any, { rejectWithValue }) => {
        try {
            const response = await apiClient.post('/users/signup', userData);
            return response.data;
        } catch (err: any) {
            return rejectWithValue(err.response?.data?.detail || 'Signup failed');
        }
    }
);

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        logout: (state) => {
            state.user = null;
            state.token = null;
            state.isAuthenticated = false;
            state.error = null;
            state.showLevelUpModal = false;
            state.newLevel = null;
        },
        clearError: (state) => {
            state.error = null;
        },
        closeLevelUpModal: (state) => {
            state.showLevelUpModal = false;
            state.newLevel = null;
        }
    },
    extraReducers: (builder) => {
        builder
            .addCase(loginUser.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(loginUser.fulfilled, (state, action) => {
                state.loading = false;
                state.token = action.payload.token;
                state.user = action.payload.user;
                state.isAuthenticated = true;
            })
            .addCase(loginUser.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload as string;
            })
            .addCase(refreshProfile.fulfilled, (state, action) => {
                // Check for Level Up
                if (state.user && action.payload.level > state.user.level) {
                    state.showLevelUpModal = true;
                    state.newLevel = action.payload.level;
                }
                state.user = action.payload;
            });
    },
});

export const { logout, clearError, closeLevelUpModal } = authSlice.actions;
export default authSlice.reducer;
