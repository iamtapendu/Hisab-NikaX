import { useNavigate } from "react-router-dom";

export default function NotFound() {
    const navigate = useNavigate();
    return (
        <div className="h-full flex flex-col items-center justify-center">
            <h1 className="text-4xl font-bold">404</h1>
            <p className="mt-2 text-lg">Page Not Found</p>

            <button
                onClick={() => navigate("/home")}
                className="btn btn-primary rounded m-4"
            >
                Go Home
            </button>
        </div>
    );
}
