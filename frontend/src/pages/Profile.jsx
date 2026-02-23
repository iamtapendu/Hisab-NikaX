import { useAuth } from "@/app/providers/auth-context"

export default function Profile() {
    const { user } = useAuth()
    return (
        <div className="grid grid-cols-[30%_70%] m-4">
            <div
                className="row-span-6 place-self-center p-2 rounded-full 
                bg-gradient-to-br from-secondary to-primary-hv shadow-2xl shadow-primary"
            >
                <div className="p-2 rounded-full bg-background">
                    <img
                        src={user?.profileImage || "/logo/user_256.png"}
                        alt="User profile"
                        className="h-64 w-64 rounded-full object-cover"
                    />
                </div>
            </div>

            <span className="font-black text-lg text-foreground/50 place-content-end pl-2">{user.username}</span>
            <span className="font-black text-5xl capitalize p-2">{user.name}</span>
            <span className="font-medium text-xl capitalize place-content-center p-2">Role: {user.role}</span>
            <span className="font-medium text-xl capitalize place-content-center p-2">Phone: {user.phone}</span>
            <span className="font-medium text-xl capitalize place-content-center p-2">Email: {user.email}</span>
            <span className="font-medium text-xl capitalize place-content-center p-2">Address: {user.address || "N/A"}</span>

        </div>
    )
}