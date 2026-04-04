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
    className = ""
}) {
    if (isEditing) {
        return (
            <InputWithPopup
                label={label}
                name={name}
                placeholder={placeholder || label}
                register={register}
                error={error}
            />
        )
    }

    return (
        <span className={`${className}`}>
           {showLabel?label:""} {value || "N/A"}
        </span>
    )
}