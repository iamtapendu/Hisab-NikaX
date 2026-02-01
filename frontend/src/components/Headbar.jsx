import { useNavigate } from "react-router-dom"
import UserMenu from '@/components/UserMenu'

export default function Headbar() {
    let navigate = useNavigate();

    return (
        <header className="col-span-2 bg-primary-hv h-12 flex items-center px-4 shadow-md z-50">
            <div className="flex justify-between items-center w-full" >
                <div className="flex items-center gap-2 cursor-pointer"
                    onClick={() => navigate("/home")}>
                    <img
                        src="/logo/logo.png"
                        alt="Hisab NikaX Logo"
                        className="h-12 object-contain"
                    />
                    <span className="text-2xl font-black text-background">
                        Hisab NikaX
                    </span>
                </div>
                <UserMenu
                    user={{
                        name: "User Account",
                        username: "UserName_01",
                        profileImage: "/logo/user.png",
                    }}
                />
            </div>
        </header >
    );

}