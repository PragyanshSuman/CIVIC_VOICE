
import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAppSelector } from '../store/hooks';
import LoginScreen from '../screens/auth/LoginScreen';
import SignupScreen from '../screens/auth/SignupScreen';
import MainTabNavigator from './MainTabNavigator';
import SubmitProblemScreen from '../screens/problem/SubmitProblemScreen';
import ProblemDetailScreen from '../screens/problem/ProblemDetailScreen';
import SubmitSolutionScreen from '../screens/problem/SubmitSolutionScreen';
import NotificationScreen from '../screens/notifications/NotificationScreen';
// Gov imports
import OfficialDashboardScreen from '../screens/official/OfficialDashboardScreen';
import CreateWorkOrderScreen from '../screens/official/CreateWorkOrderScreen';

import { Colors } from '../constants/Colors';

const Stack = createNativeStackNavigator();

const RootNavigator = () => {
  const { isAuthenticated, user } = useAppSelector((state) => state.auth);

  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: Colors.background },
        headerTintColor: Colors.text,
        headerTitleStyle: { fontWeight: 'bold' },
        contentStyle: { backgroundColor: Colors.background }
      }}
    >

      {isAuthenticated ? (
        user?.role === 'GOVERNMENT' ? (
          <>
            <Stack.Screen 
              name="OfficialDashboard" 
              component={OfficialDashboardScreen} 
              options={{ title: 'Gov Workspace' }}
            />
            <Stack.Screen 
              name="ProblemDetail" 
              component={ProblemDetailScreen} 
              options={{ title: 'Problem Details' }} 
            />
            <Stack.Screen 
              name="SubmitSolution" 
              component={SubmitSolutionScreen} 
              options={{ title: 'Propose Innovation' }} 
            />
            <Stack.Screen 
              name="CreateWorkOrder" 
              component={CreateWorkOrderScreen} 
              options={{ title: 'Dispatch Work Order' }} 
            />
          </>
        ) : (
          <>
            <Stack.Screen 
              name="Main" 
              component={MainTabNavigator} 
              options={{ headerShown: false }} 
            />
            <Stack.Screen 
              name="SubmitProblem" 
              component={SubmitProblemScreen} 
              options={{ title: 'Report a Problem' }} 
            />
            <Stack.Screen 
              name="ProblemDetail" 
              component={ProblemDetailScreen} 
              options={{ title: 'Problem Details' }} 
            />
            <Stack.Screen 
              name="SubmitSolution" 
              component={SubmitSolutionScreen} 
              options={{ title: 'Propose Innovation' }} 
            />
            <Stack.Screen 
              name="Notifications" 
              component={NotificationScreen} 
              options={{ headerShown: false }} 
            />
          </>
        )
      ) : (
        <>
          <Stack.Screen name="Login" component={LoginScreen} options={{ headerShown: false }} />
          <Stack.Screen name="Signup" component={SignupScreen} options={{ headerShown: false }} />
        </>
      )}
    </Stack.Navigator>
  );
};


export default RootNavigator;
