import { Outlet } from "react-router-dom"

export default function AuthLayout() {
    return (
        <div className="min-h-screen min-w-screen flex items-center justify-center bg-background">
            <Outlet />
        </div>
    );
}
