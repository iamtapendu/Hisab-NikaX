import { createBrowserRouter, Navigate } from "react-router-dom";
import AuthLayout from "./layouts/AuthLayout";
import Login from "@/pages/Login";
import Profile from '@/pages/Profile'
import PublicRoute from "./layouts/PublicRoute";
import ProtectedRoute from "./layouts/ProtectedRoute";
import BaseLayout from "./layouts/BaseLayout";
import App from "@/App";

export const router = createBrowserRouter([
    {
        path: "/",
        element: <Navigate to="/auth/login" replace />
    },

    {
        element: (
            <PublicRoute>
                <AuthLayout />
            </PublicRoute>
        ),
        children: [
            { path: "/auth/login", element: <Login /> },
        ],
    },
    {
        path: "/home",
        element: (
            <ProtectedRoute>
                <BaseLayout />
            </ProtectedRoute>
        ),
    },
    {
        element: (
            <ProtectedRoute>
                <BaseLayout/>
            </ProtectedRoute>
        ),
         children: [
            { path: "/users/profile", element: <Profile/> },
        ],
    },
    {
        path: "/app",
        element: (
            // <ProtectedRoute>
            <App />
            // </ProtectedRoute>
        ),
    },
]);
