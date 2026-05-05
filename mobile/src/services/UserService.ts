import apiClient from '../utils/api';
import { Problem, User } from '../types';

export interface UserStats {
    reports_submitted: number;
    issues_resolved: number;
    verification_score: number;
    impact_level: string;
    volunteered_count: number;
}

export const UserService = {
    getStats: async (userId: string): Promise<UserStats> => {
        const response = await apiClient.get(`/users/${userId}/stats`);
        return response.data;
    },

    getUserProblems: async (userId: string): Promise<Problem[]> => {
        const response = await apiClient.get(`/problems/user/${userId}`);
        return response.data;
    },

    getUser: async (userId: string): Promise<User> => {
        const response = await apiClient.get(`/users/${userId}`);
        return response.data;
    }
};
