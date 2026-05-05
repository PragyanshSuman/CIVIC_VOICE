
import apiClient from '../utils/api';
import { User } from '../types';

export interface ChatMessage {
    id: string;
    community_id: string;
    user_id: string;
    content: string;
    created_at: string;
    user: {
        id: string;
        full_name: string;
        level: number;
    };
}

export interface Community {
    id: string;
    name: string;
    description: string;
    location: string;
    image_url: string | null;
    members_count: number;
    is_member: boolean;
    created_by_id: string;
}

export interface ResourceItem {
    id: string;
    community_id: string;
    user_id: string;
    title: string;
    description: string;
    item_type: 'OFFER' | 'REQUEST';
    status: 'AVAILABLE' | 'TAKEN' | 'COMPLETED';
    created_at: string;
    user: {
        id: string;
        full_name: string;
    };
}

const CommunityService = {
    getAll: async (): Promise<Community[]> => {
        const response = await apiClient.get('/communities/');
        return response.data;
    },

    create: async (data: { name: string; description: string; location: string }): Promise<Community> => {
        const response = await apiClient.post('/communities/', data);
        return response.data;
    },

    join: async (communityId: string): Promise<{ joined: boolean; message: string }> => {
        const response = await apiClient.post(`/communities/${communityId}/join`);
        return response.data;
    },

    getChat: async (communityId: string): Promise<ChatMessage[]> => {
        const response = await apiClient.get(`/communities/${communityId}/chat`);
        return response.data;
    },

    postMessage: async (communityId: string, content: string): Promise<ChatMessage> => {
        const response = await apiClient.post(`/communities/${communityId}/chat`, { content });
        return response.data;
    },

    getResources: async (communityId: string): Promise<ResourceItem[]> => {
        const response = await apiClient.get(`/communities/${communityId}/resources`);
        return response.data;
    },

    createResource: async (communityId: string, data: { title: string; description: string; item_type: string }): Promise<ResourceItem> => {
        const response = await apiClient.post(`/communities/${communityId}/resources`, data);
        return response.data;
    }
};

export default CommunityService;
