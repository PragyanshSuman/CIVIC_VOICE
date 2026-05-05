
import apiClient from '../utils/api';

export interface Quest {
    id: string;
    title: string;
    description: string;
    xp_reward: number;
    action_type: string;
    target_count: number;
    is_active: boolean;
    user_progress: number;
    is_completed: boolean;
}

const QuestService = {
    getAll: async (): Promise<Quest[]> => {
        const response = await apiClient.get('/quests/');
        return response.data;
    },

    claim: async (questId: string): Promise<any> => {
        const response = await apiClient.post(`/quests/${questId}/claim`);
        return response.data;
    }
};

export default QuestService;
