import { Outlet } from "react-router-dom"

export default function HomeLayout() {
    return (
        <div className="min-h-screen min-w-screen grid grid-rows-[48px_1fr] m-0 p-0 bg-background">
            <header className="col-span-2 bg-primary-hv h-12 flex items-center px-4 shadow-md z-50">
                <div className="flex justify-between items-center w-full">
                    <span className="text-2xl font-black text-background">
                        Hisab NikaX
                    </span>
                    <span className="font-bold text-background">
                        User Account
                    </span>
                </div>
            </header>

            <div className="grid grid-cols-[14rem_1fr]">

                <aside className="bg-primary h-full">
                    <nav className="flex flex-col items-center h-full">
                        {["Dashboard", "Customers", "Suppliers", "Sales", "Purchase", "Expenses",
                            "Inventory", "Staff", "Reports","Users"].map(item => (
                                <span
                                    key={item}
                                    className="flex-1 flex w-full justify-center items-center font-bold
                                 text-background cursor-pointer hover:bg-primary-hv transition 
                                 border border-primary-hv"
                                >
                                    {item}
                                </span>
                            ))}
                    </nav>
                </aside>

                <main className="">
                    {/* <Outlet /> later */}
                </main>

            </div>
        </div>
    );
}
