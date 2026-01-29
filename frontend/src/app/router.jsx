import { createBrowserRouter, Navigate } from "react-router-dom";
import AuthLayout from "./layouts/AuthLayout";
import Login from "../pages/Login";
import PublicRoute from "./layouts/PublicRoute";

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
            <PublicRoute>
                <h1>Hello</h1>
            </PublicRoute>
        ),
    },
]);
