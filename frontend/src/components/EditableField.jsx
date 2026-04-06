import InputWithPopup from "@/components/InputWithPopup"

export default function EditableField({
    label,
    showLabel,
    name,
    value,
    isEditing,
    register,
    error,
    placeholder,
    className = "",
    type="text"
}) {
    if (isEditing) {
        return (
            <InputWithPopup
                label={label}
                name={name}
                placeholder={placeholder || label}
                register={register}
                error={error}
                type={type}
            />
        )
    }

    return (
        <span className={`${className}`}>
           {showLabel?label:""} {value || ""}
        </span>
    )
}