import { useAuth } from "@/app/providers/auth-context"
import { useState } from "react"
import { usersSchema, updatePasswordSchema } from "@/modules/users/schema"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import Spinner from "@/components/Spinner"
import Modal from "@/components/Modal"
import { updateUser, updatePassword } from "@/modules/users/service"
import EditableField from "@/components/EditableField"

export default function Profile() {
    const { user, setUser } = useAuth();
    const [isEditing, setIsEditing] = useState(false);

    const [modalMsg, setModalMsg] = useState("");
    const [msgModalOpen, setMsgModalOpen] = useState(false);
    const [passModalOpen, setPassModalOpen] = useState(false);

    const {
        register,
        handleSubmit,
        reset,
        formState: { errors, isSubmitting },
    } = useForm({
        resolver: zodResolver(usersSchema),
        defaultValues: user,
    });


    const {
        register: registerPassChange,
        handleSubmit: handlePassChange,
        reset: passReset,
        formState: { errors: passErrors, isSubmitting: isPassChange },
    } = useForm({
        resolver: zodResolver(updatePasswordSchema),
    });

    const onSubmit = async (values) => {
        try {
            const payload = {
                ...user,
                ...values,
            };
            const updatedUser = await updateUser(user.id, payload);
            setUser(updatedUser)
            setModalMsg("Profile updated successfully");
            setMsgModalOpen(true);
            setIsEditing(false);
            console.log("[User Updated]");

        } catch (error) {
            setModalMsg((error?.msg || "Error") + " " + (error?.errors || ""));
            setMsgModalOpen(true);
            console.log("[Update Failed]", error.msg, error.errors);
        }
    }

    const onPasswordChange = async (values) => {
        try {
            await updatePassword(user.id, values);
            console.log("[User Password changed]");
            setPassModalOpen(false);
            passReset();
            setModalMsg("Password Changed Successfuly");
            setMsgModalOpen(true)
        } catch (error) {
            setModalMsg((error?.msg || "Error") + " " + (error?.errors || ""));
            setMsgModalOpen(true);
            console.log("[Update Failed]", error.msg, error.errors);
        }
    }

    return (
        <div>
            <form className="relative grid grid-cols-[30%_70%] m-4" onSubmit={handleSubmit(onSubmit)}>
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

                <EditableField
                    label="Username :"
                    name="username"
                    value={user.username}
                    isEditing={isEditing}
                    register={register}
                    error={errors.username}
                    placeholder={"Username"}
                    className="font-black text-lg text-foreground/50 place-content-end pl-2"
                />

                <EditableField
                    label="Name :"
                    name="name"
                    value={user.name}
                    isEditing={isEditing}
                    register={register}
                    error={errors.name}
                    placeholder={"Name"}
                    className="font-black text-5xl capitalize p-2"
                />

                <EditableField
                    label="Role:"
                    name="role"
                    value={user.role}
                    isEditing={isEditing}
                    register={register}
                    error={errors.role}
                    placeholder={"Role"}
                    className="font-medium text-xl capitalize place-content-center p-2"
                    showLabel={true}
                />

                <EditableField
                    label="Phone:"
                    name="phone"
                    value={user.phone}
                    isEditing={isEditing}
                    register={register}
                    error={errors.phone}
                    placeholder={"Phone"}
                    className="font-medium text-xl capitalize place-content-center p-2"
                    showLabel={true}
                />

                <EditableField
                    label="Email:"
                    name="email"
                    value={user.email}
                    isEditing={isEditing}
                    register={register}
                    error={errors.email}
                    placeholder={"Email"}
                    className="font-medium text-xl place-content-center p-2"
                    showLabel={true}
                />

                <button
                    type="button"
                    className="absolute top-4 right-4 btn btn-tertiary h-8 w-8  rounded-full 
                        shadow-lg hover:scale-105 transition-all duration-200 flex items-center 
                        justify-center text-lg"
                    onClick={() => {
                        if (!isEditing) {
                            reset({
                                username: user.username,
                                name: user.name,
                                role: user.role,
                                phone: user.phone,
                                email: user.email,
                                address: user.address
                            });
                        }
                        setIsEditing(prev => !prev);
                    }}
                >
                    {!isEditing ? "\u270E" : "\u2715"}
                </button>

                {isEditing && (
                    <div className="absolute bottom-0 right-4 flex gap-4">
                        <button
                            type="submit"
                            className="btn btn-primary"
                        >
                            {isSubmitting && <Spinner />}
                            {isSubmitting ? "Saving..." : "Save"}
                        </button>
                    </div>
                )}

                <Modal
                    open={msgModalOpen}
                    message={modalMsg}
                    onClose={() => setMsgModalOpen(false)}
                />
            </form>

            <button className="btn btn-primary m-10" onClick={() => { setPassModalOpen(true) }}>
                Change Password
            </button>

            <Modal
                open={passModalOpen}
                title={"Password Change"}
                onClose={() => setPassModalOpen(false)}
            >
                <form className="relative m-2" onSubmit={handlePassChange(onPasswordChange)}>
                    <EditableField
                        type="password"
                        label="Current Password:"
                        name="current_password"
                        isEditing={true}
                        register={registerPassChange}
                        error={passErrors.current_password}
                        placeholder={"Current Password"}
                        className="font-medium text-xl place-content-center p-2"
                        showLabel={true}
                    />

                    <EditableField
                        type="password"
                        label="New Password:"
                        name="new_password"
                        isEditing={true}
                        register={registerPassChange}
                        error={passErrors.new_password}
                        placeholder={"New Password"}
                        className="font-medium text-xl place-content-center p-2"
                        showLabel={true}
                    />
                    <div className="flex justify-end gap-2 mt-4">
                        <button
                            type="button"
                            className="btn btn-tertiary"
                            onClick={() => setPassModalOpen(false)}
                        >
                            Cancel
                        </button>

                        <button
                            type="submit"
                            className="btn btn-primary flex items-center gap-2"
                        >
                            {isPassChange && <Spinner size="sm" />}
                            {isPassChange ? "Changing..." : "Change Password"}
                        </button>
                    </div>

                </form>
            </Modal>
        </div>
    )
}