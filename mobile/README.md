# Civic Voice - Mobile Application

## Overview
React Native mobile application for the Civic Collaboration Platform, enabling citizens to report problems and propose solutions.

## Features
- 🔐 Secure authentication with JWT
- 📍 Location-based problem reporting
- 📸 Image upload support
- 🗺️ Interactive map view
- 💬 Real-time solution discussions
- 📊 AI-powered solution rankings

## Tech Stack
- **React Native** with Expo
- **TypeScript** for type safety
- **Redux Toolkit** for state management
- **React Navigation** for routing
- **Axios** for API communication
- **Formik & Yup** for form validation

## Setup

### Prerequisites
- Node.js 18+
- Expo CLI
- Android Studio (for Android) or Xcode (for iOS)

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start

# Run on Android
npm run android

# Run on iOS
npm run ios
```

### Configuration

1. Update API URL in `src/constants/Config.ts`:
   ```typescript
   export const API_URL = "http://YOUR_BACKEND_URL/api/v1";
   ```

2. Add Google Maps API key in `src/constants/Config.ts`:
   ```typescript
   export const GOOGLE_MAPS_API_KEY = "YOUR_API_KEY";
   ```

## Project Structure

```
src/
├── api/              # API service layer
├── components/       # Reusable components
├── constants/        # App constants and config
├── hooks/            # Custom React hooks
├── navigation/       # Navigation configuration
├── screens/          # Screen components
├── store/            # Redux store and slices
├── types/            # TypeScript type definitions
└── utils/            # Utility functions
```

## Development

### Code Quality

```bash
# Lint code
npm run lint

# Format code
npm run format

# Type check
npm run type-check
```

## Building for Production

### Android
```bash
eas build --platform android
```

### iOS
```bash
eas build --platform ios
```

## License
MIT
