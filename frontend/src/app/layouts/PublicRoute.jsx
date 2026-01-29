import { Navigate } from "react-router-dom";
import { useAuth } from "../providers/auth-context";

export default function PublicRoute({ children }) {
    const { isAuthenticated } = useAuth();

    if (isAuthenticated) {
        return <Navigate to="/home" replace />;
    }

    return children;
}
