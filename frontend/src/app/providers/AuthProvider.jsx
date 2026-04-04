import { useState, useEffect, useCallback } from "react";
import { AuthContext } from "./auth-context";
import api from "@/lib/api";

export function AuthProvider({ children }) {

    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const logout = useCallback(() => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        setUser(null);
    }, []);

    const fetchUser = useCallback(async () => {
        try {
            const { data } = await api.get("/users/profile");
            setUser(data);
        } catch (err) {
            console.log("[Login Failed]", err.message)
            logout();
        } finally {
            setLoading(false);
        }
    }, [logout]);

    const login = async ({ access_token, refresh_token }) => {
        localStorage.setItem("access_token", access_token);
        localStorage.setItem("refresh_token", refresh_token);
        await fetchUser();
    };

    useEffect(() => {
        async function restoreUserOnRefresh() {
            const token = localStorage.getItem("access_token");
            if (!user && token) {
                await fetchUser();
            } else setLoading(false);
        }
        restoreUserOnRefresh();
    }, [user, fetchUser]);

    useEffect(() => {
        const handler = () => logout();
        window.addEventListener("auth:logout", handler);
        return () => window.removeEventListener("auth:logout", handler);
    }, [logout]);


    return (
        <AuthContext.Provider
            value={{
                isAuthenticated: !!user,
                user,
                setUser,
                loading,
                login,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}
