import { useAuth } from "@/app/providers/auth-context"
import { useState } from "react"
import InputWithPopup from "@/components/InputWithPopup"
import { usersSchema } from "@/modules/users/schema"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"

export default function Profile() {
    const { user } = useAuth()
    const [formData, setFormData] = useState(user)
    const [isEditing, setIsEditing] = useState(false)

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm({
        resolver: zodResolver(usersSchema),
    });

    return (
        <div className="relative grid grid-cols-[30%_70%] m-4">
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

            {isEditing ? (
                <InputWithPopup label= "Username :" name="username" placeholder="Username" defaultValue={user.username} register={register} error={errors.username} />
            ) : (
                <span className="font-black text-lg text-foreground/50 place-content-end pl-2">{user.username}</span>
            )}
            {isEditing ? (
                <InputWithPopup label= "Name :" name="name" placeholder="Name" defaultValue={user.name} register={register} error={errors.name} />
            ) : (
                <span className="font-black text-5xl capitalize p-2">{user.name}</span>
            )}
            {isEditing ? (
                <InputWithPopup label= "Role :" name="role" placeholder="Role" defaultValue={user.role} register={register} error={errors.role} />
            ) : (
                <span className="font-medium text-xl capitalize place-content-center p-2">Role: {user.role}</span>
            )}
            {isEditing ? (
                <InputWithPopup label= "Phone Number :" name="phone" placeholder="Phone Number" defaultValue={user.phone} register={register} error={errors.phone} />
            ) : (
                <span className="font-medium text-xl capitalize place-content-center p-2">Phone: {user.phone}</span>
            )}
            {isEditing ? (
                <InputWithPopup label= "Email :" name="email" placeholder="Email" defaultValue={user.email} register={register} error={errors.email} />
            ) : (
                <span className="font-medium text-xl capitalize place-content-center p-2">Email: {user.email}</span>
            )}
            {isEditing ? (
                <InputWithPopup label= "Address :" name="address" placeholder="Address" defaultValue={user.address} register={register} error={errors.address} />
            ) : (
                <span className="font-medium text-xl capitalize place-content-center p-2">Address: {user.address || "N/A"}</span>
            )}

            <button
                className="absolute top-4 right-4 btn btn-tertiary h-8 w-8  rounded-full 
                        shadow-lg hover:scale-105 transition-all duration-200 flex items-center 
                        justify-center text-lg"
                onClick={() => setIsEditing(true)}
            >
                &#9998;
            </button>

            {isEditing && (
                <div className="col-span-2 flex gap-4 mt-4">
                    <button
                        // onClick={handleSave}
                        // disabled={loading}
                        className="btn btn-primary"
                    >
                        Save {/* {loading ? "Saving..." : "Save"} */}
                    </button>

                    <button
                        onClick={() => {
                            setFormData(user);
                            setIsEditing(false);
                        }}
                        className="btn btn-secondary"
                    >
                        Cancel
                    </button>
                </div>
            )}
        </div>
    )
}