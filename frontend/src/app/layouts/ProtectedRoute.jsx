import { Navigate } from "react-router-dom";
import { useAuth } from "../providers/auth-context";

export default function ProtectedRoute({ children }) {
    const { isAuthenticated } = useAuth();

    if (!isAuthenticated) {
        return <Navigate to="/auth/login" replace />;
    }

    return children;
}
