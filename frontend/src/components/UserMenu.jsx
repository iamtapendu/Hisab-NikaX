import { useState } from "react"
import ThemeSwitcher from '@/components/ThemeSwitcher'

export default function UserMenu({ user }) {
    const [open, setOpen] = useState(false)

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
                <span className="font-bold text-background">
                    {user.name}
                </span>
                <img
                    src={user.profileImage}
                    alt="User profile"
                    className="h-8 w-8 rounded-full object-cover"
                />
            </div>

            {/* Popover */}
            {open && (
                <div
                    className="absolute right-0 top-12 w-56 bg-background rounded-md shadow-md 
                        shadow-foreground border z-50"
                >
                    <div className="p-4 border-b">
                        <p className="font-semibold">{user.name}</p>
                        <p className="text-sm text-foreground/40">{user.username}</p>
                    </div>
                    <ThemeSwitcher />

                    <div className="flex flex-col border-t border-foreground/40">
                        <button className="px-4 py-2 text-left hover:bg-tertiary-hv">
                            Profile
                        </button>
                        <button className="px-4 py-2 text-left hover:bg-tertiary-hv">
                            Settings
                        </button>
                        <button className="px-4 py-2 text-left hover:bg-tertiary-hv text-red-600">
                            Logout
                        </button>
                    </div>
                </div>
            )}
        </div>
    )
}
