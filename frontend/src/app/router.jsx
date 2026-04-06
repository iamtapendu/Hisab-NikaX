import { createBrowserRouter, Navigate } from "react-router-dom";
import AuthLayout from "./layouts/AuthLayout";
import Login from "@/pages/Login";
import Profile from '@/pages/Profile'
import PublicRoute from "./layouts/PublicRoute";
import ProtectedRoute from "./layouts/ProtectedRoute";
import BaseLayout from "./layouts/BaseLayout";
import Users from "@/pages/Users";
import NotFound from "@/pages/NotFound";

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
        element: (
            <ProtectedRoute>
                <BaseLayout />
            </ProtectedRoute>
        ),
        children: [
            { path: "/home" },
            { path: "/users", element: <Users /> },
            { path: "/users/profile", element: <Profile /> },
            { path: "*", element: <NotFound /> },
        ],
    },
]);
