import { useNavigate } from "react-router-dom"
import { memo } from "react";
import UserMenu from '@/components/UserMenu'

const Headbar = memo(function Headbar() {
    const navigate = useNavigate();
    const handleHomeClick = () => navigate("/home");
    return (
        <header className="col-span-2 bg-primary-hv h-12 flex items-center px-4 shadow-md z-25">
            <div className="flex justify-between items-center w-full" >
                <div className="flex items-center gap-2 cursor-pointer"
                    onClick={handleHomeClick}>
                    <img
                        src="/logo/logo.png"
                        alt="Hisab NikaX Logo"
                        className="h-12 object-contain"
                    />
                    <span className="text-2xl font-black text-background">
                        Hisab NikaX
                    </span>
                </div>
                <UserMenu />
            </div>
        </header >
    );

});

export default Headbar;