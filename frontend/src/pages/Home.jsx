import { useAuth } from "@/app/providers/auth-context";
import { useNavigate } from "react-router-dom";

export default function Home() {
    const navigate = useNavigate();
    const { user } = useAuth();
    return (
        <div className="h-full flex flex-col items-center">
            <h1 className="text-4xl font-bold capitalize m-10">
                {user.name.split(' ')[0]}, welcome to Hisab NikaX
            </h1>

            <button
                onClick={() => navigate("/dashboard")}
                className="btn btn-primary rounded m-4"
            >
                Go Dashboard
            </button>
        </div>
    );
}
