export interface User {
    id: string;
    email: string;
    full_name: string;
    role: 'CITIZEN' | 'GOVERNMENT' | 'ADMIN';
    karma_points: number;
    level: number;
}

export interface MediaAttachment {
    id: string;
    file_url: string;
    media_type: 'image' | 'video';
}

export interface Problem {
    id: string;
    title: string;
    description: string;
    category: string;
    status: 'open' | 'under_review' | 'solved' | 'rejected';
    latitude: number;
    longitude: number;
    address?: string;
    image_url?: string;
    media_attachments?: MediaAttachment[];
    escalation_level?: number;
    sla_due_at?: string;
    created_at: string;
    author?: User;
    department_id?: string;
    jurisdiction_id?: string;
}

export interface Jurisdiction {
    id: string;
    name: string;
    type: 'CITY' | 'ZONE' | 'WARD' | 'DISTRICT';
    boundary_polygon?: {
        type: 'Polygon' | 'MultiPolygon';
        coordinates: number[][][] | number[][][][];
    };
}

export interface Solution {
    id: string;
    title: string;
    description: string;
    problem_id: string;
    ai_score_feasibility: number;
    ai_score_impact: number;
    ai_score_cost: number;
    overall_score: number;
    upvotes_count: number;
    downvotes_count: number;
    author_id: string;
    media_attachments?: { id: string; file_url: string; media_type: 'image' | 'video' }[];
    created_at: string;
}
export interface GovernmentResponse {
    id: string;
    problem_id: string;
    official_id: string;
    response_text: string;
    action_plan?: string;
    created_at: string;
    updated_at: string;
}

export interface Comment {
    id: string;
    content: string;
    user_id: string;
    created_at: string;
    author?: User;
}

export interface Notification {
    id: string;
    title: string;
    message: string;
    is_read: boolean;
    created_at: string;
    resource_id?: string;
    resource_type?: string;
}

