
import axios from 'axios';
import { API_URL } from '../constants/Config';
// import { store } from '../store';
let store: any;

export const injectStore = (_store: any) => {
    store = _store;
};

const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 10000,
});

// Request interceptor to add token
apiClient.interceptors.request.use(
    async (config) => {
        // Redux store is the source of truth for the token
        const state = store.getState();
        const token = state.auth.token;

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default apiClient;
