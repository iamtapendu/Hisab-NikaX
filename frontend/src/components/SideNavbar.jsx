import { memo } from "react";
import { useNavigate } from "react-router-dom";


const MENU_ITEMS = [
    "Dashboard",
    "Customers",
    "Suppliers",
    "Sales",
    "Purchases",
    "Expenses",
    "Inventory",
    "Staffs",
    "Reports",
    "Users",
]

const SideNavbar = memo(function SideNavbar({ isOpen, onToggle }) {
    const navigate = useNavigate();

    const handleNavigate = (item) => {
        navigate(`/${item.toLowerCase()}`);
    };

    return (
        <aside
            className={`relative bg-primary h-full transition-all duration-300 
                    ${isOpen ? "w-56" : "w-0"} group`}
        >
            <nav className={`flex flex-col items-center h-full overflow-hidden
                        ${isOpen ? "opacity-100" : "opacity-0 pointer-events-none"}
                        transition-opacity duration-200`}
            >

                {MENU_ITEMS.map(item => (
                    <button
                        key={item}
                        className="flex-1 flex w-full justify-center items-center font-bold
                                 text-background cursor-pointer hover:bg-primary-hv transition 
                                 border border-primary-hv"
                        onClick={() => handleNavigate(item)}
                    >
                        {item}
                    </button>
                ))}
            </nav>

            <div
                onClick={() => onToggle(prev => !prev)}
                className={`absolute top-1/2 -right-3 -translate-y-1/2
                            w-6 h-8 bg-primary-hv rounded-md
                            flex items-center justify-center
                            cursor-pointer shadow-md
                            ${isOpen ? "opacity-0" : "opacity-100"} group-hover:opacity-100
                            transition-all duration-200`}
            >
                <span
                    className={`text-background text-sm transition-transform duration-300
                            ${isOpen ? "rotate-0" : "rotate-180"}`}
                >
                    ❮
                </span>
            </div>
        </aside>
    );
});

export default SideNavbar;
