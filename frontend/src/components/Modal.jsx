import { createPortal } from "react-dom";
import { useEffect } from "react"

export default function Modal({ open, message, onClose }) {
    
    useEffect(() => {
        if (!open) return;
        
        const handler = (e) => {
            if (e.key === "Escape") onClose();
            if (e.key === "Enter") onClose();
        }
        window.addEventListener("keydown", handler);
        
        return () => window.removeEventListener("keydown", handler);
    }, [open, onClose]);
    
    if (!open) return null;

    return createPortal(
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-foreground/60"
                onClick={onClose}
            />

            {/* Modal box */}
            <div className="relative z-10 w-full max-w-sm rounded-lg bg-background p-6 shadow-lg">

                {/* Close button (top-right) */}
                <button
                    onClick={onClose}
                    className="absolute right-3 top-3 btn btn-tertiary py-0 px-2 m-0"
                    aria-label="Close"
                >
                    &times;
                </button>

                {/* Header */}
                <h2 className="text-lg font-semibold text-foreground mb-3">
                    Message
                </h2>

                {/* Message body */}
                <p className="text-foreground m-6">
                    {message}
                </p>

                {/* Footer */}
                <div className="flex justify-end">
                    <button
                        onClick={onClose}
                        className="btn btn-primary py-1 px-2"
                    >
                        OK
                    </button>
                </div>
            </div>

        </div>,
        document.body
    );
}
