import SideNavbar from "@/components/SideNavbar";
import { Outlet } from "react-router-dom"
import { useState } from "react"
import Headbar from "@/components/Headbar";

export default function BaseLayout() {
    const [sidebarOpen, setSidebarOpen] = useState(true)

    return (
        <div className="min-h-screen min-w-screen grid grid-rows-[48px_1fr] m-0 p-0 bg-background">

            <Headbar/>

            <div
                className={`grid transition-all duration-300 ease-in-out
                ${sidebarOpen ? "grid-cols-[14rem_1fr]" : "grid-cols-[0_1fr]"}`}
            >
                <SideNavbar isOpen={sidebarOpen} onToggle={setSidebarOpen} />

                <main className="">
                    <Outlet />
                </main>

            </div>
        </div >
    );
}
