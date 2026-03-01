export default function InputWithPopup({
    error,
    register,
    name,
    type = "text",
    placeholder,
    defaultValue = "",
}) {
    return (
        <div className="relative w-full group">
            {/* Input */}
            <input
                {...register(name)}
                type={type}
                placeholder={placeholder}
                defaultValue={defaultValue}
                className={`input p-2 m-1 ${error ? "border-danger focus:ring-danger" : ""}`}
            />

            {/* Warning icon */}
            {error && (
                <div className="absolute right-3 top-1/2 -translate-y-1/2 ">
                    <span
                        aria-label="error"
                        className="text-danger text-lg"
                    >
                        !
                    </span>

                    {/* Popup */}
                    <div
                        className="absolute right-0 bottom-10 m-1 w-56 rounded-md
                         bg-foreground text-background text-sm p-1 shadow-lg border-0
                         opacity-0 scale-50 group-hover:opacity-95 group-hover:scale-100
                         transition-all z-20 text-center"
                    >
                        {error.message}
                    </div>
                </div>
            )}
        </div>
    );
}
