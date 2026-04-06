import { useAuth } from "@/app/providers/auth-context";
import { useNavigate } from "react-router-dom";


export default function Users() {
    const navigate = useNavigate();
    const { user, setUser } = useAuth();
    const isAdmin = user?.role?.toLowerCase() === "admin";
    
    return isAdmin ? (
        <p>Hello {user.name} - {user.role}, This is User page</p>
    ) : (<>
        <div className="h-full flex flex-col items-center justify-center">
            <h1 className="text-4xl font-bold">401</h1>
            <p className="mt-2 text-lg">Unauthorized - Admin Only Page</p>

            <button
                onClick={() => navigate("/home")}
                className="btn btn-primary rounded m-4"
            >
                Go Home
            </button>
        </div>
    </>)
}