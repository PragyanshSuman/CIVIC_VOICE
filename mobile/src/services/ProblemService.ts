import apiClient from '../utils/api';
import { Problem, Solution, GovernmentResponse, User } from '../types';

export interface SquadJoinResponse {
    joined: boolean;
    message: string;
}

export const ProblemService = {
    getProblem: async (id: string): Promise<Problem> => {
        const response = await apiClient.get(`/problems/${id}`);
        return response.data;
    },

    getSolutions: async (problemId: string): Promise<Solution[]> => {
        const response = await apiClient.get(`/solutions/problem/${problemId}`);
        return response.data;
    },

    getGovernmentResponses: async (problemId: string): Promise<GovernmentResponse[]> => {
        const response = await apiClient.get(`/problems/${problemId}/responses`);
        return response.data;
    },

    // Action Squads
    joinSquad: async (problemId: string): Promise<SquadJoinResponse> => {
        const response = await apiClient.post(`/problems/${problemId}/join`);
        return response.data;
    },

    getSquad: async (problemId: string): Promise<User[]> => {
        const response = await apiClient.get(`/problems/${problemId}/squad`);
        return response.data;
    },

    verifyResolution: async (problem_id: string, is_resolved: boolean, comment?: string): Promise<{ message: string; points_awarded: number }> => {
        const response = await apiClient.post(`/problems/${problem_id}/verify-resolution`, null, {
            params: { is_resolved, comment }
        });
        return response.data;
    },

    updateProblemStatus: async (problemId: string, status: string): Promise<Problem> => {
        const response = await apiClient.put(`/problems/${problemId}`, { status });
        return response.data;
    },
    // Official/Contractor
    getAssignedProblems: async (): Promise<Problem[]> => {
        // Backend: GET /problems?assigned_official_id=me (Need to implement filter in backend or use a specific endpoint)
        // For now, let's assume /problems return all, and we filter client side OR add a specific endpoint.
        // Actually, `GET /problems` has a `status` filter, but not `official_id`.
        // Better: GET /officials/queue (I planned this in Implementation Plan).
        // Let's use that.
        const response = await apiClient.get('/officials/queue');
        return response.data;
    }
};
