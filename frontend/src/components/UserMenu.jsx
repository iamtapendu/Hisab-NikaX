import { memo, useState } from "react"
import ThemeSwitcher from '@/components/ThemeSwitcher'
import { useAuth } from "../app/providers/auth-context";
import { useNavigate } from "react-router-dom";
import { logoutUser } from "@/modules/auth/service";

const UserMenu = memo(function UserMenu() {
    const [open, setOpen] = useState(false);
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const onLogout = async () => {
        setOpen(false);
        await logoutUser();
        logout();
        navigate("/auth/login");
    }

    const onProfile = () => {
        setOpen(false);
        navigate("/users/profile");
    }

    return (
        <div
            className="relative h-12 content-center"
            onMouseLeave={() => setOpen(false)}
        >
            {/* Trigger */}
            <div
                className="flex items-center gap-2 cursor-pointer"
                onClick={() => setOpen(true)}
            >
                <span className="font-bold text-background min-w-32 text-right capitalize">
                    {user?.name ?? "User"}
                </span>
                <img
                    src={user?.profileImage || "/logo/user.png"}
                    alt="User profile"
                    className="h-8 w-8 rounded-full object-cover"
                />
            </div>

            {/* Popover */}
            {open && (
                <div
                    className="absolute right-0 top-12 w-56 bg-background rounded-md shadow-md 
                        shadow-foreground border z-50 "
                >
                    <div
                        className="p-4 border-b grid grid-cols-[30%_70%] items-center hover:bg-tertiary-hv"
                        onClick={onProfile}
                    >
                        <img
                            src={user?.profileImage || "/logo/user.png"}
                            alt="User profile"
                            className="h-10 w-10 row-span-2 rounded-full object-cover"
                        />
                        <p className="font-semibold capitalize">{user?.name ?? "User"}</p>
                        <p className="text-sm text-foreground/40">{user?.username ?? "Username"}</p>
                    </div>
                    <ThemeSwitcher />

                    <div className="flex flex-col border-t border-foreground/40">
                        <button className="px-4 py-2 text-left hover:bg-tertiary-hv">
                            Settings
                        </button>
                        <button
                            className="px-4 py-2 text-left hover:bg-tertiary-hv text-danger"
                            onClick={onLogout}
                        >
                            Logout
                        </button>
                    </div>
                </div>
            )}
        </div>
    )
});

export default UserMenu;
