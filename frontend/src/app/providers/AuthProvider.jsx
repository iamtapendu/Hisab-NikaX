import {  useState } from "react";
import { AuthContext } from "./auth-context";

export function AuthProvider({ children }) {
    const [accessToken, setAccessToken] = useState(
        () => localStorage.getItem("access_token")
    );

    const login = ({ access_token, refresh_token }) => {
        localStorage.setItem("access_token", access_token);
        localStorage.setItem("refresh_token", refresh_token);
        setAccessToken(access_token);
    };

    const logout = () => {
        localStorage.clear();
        setAccessToken(null);
    };

    return (
        <AuthContext.Provider
            value={{
                isAuthenticated: !!accessToken,
                accessToken,
                login,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}
