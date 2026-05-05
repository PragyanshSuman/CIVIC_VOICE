
import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import { injectStore } from '../utils/api';

export const store = configureStore({
    reducer: {
        auth: authReducer,
        // problems: problemsReducer, // To be added later
    },
});

injectStore(store);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
