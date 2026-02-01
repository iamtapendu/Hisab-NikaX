import useTheme from "@/hooks/useTheme"

export default function ThemeSwitcher() {
    const { theme, setTheme, themes } = useTheme()

    return (
        <div className="px-4 py-3 border-t border-foreground/40">
            <div className="flex gap-2">
                {themes.map(t => (
                    <button
                        key={t}
                        onClick={() => setTheme(t)}
                        className={`flex-1 btn transition-all px-1 py-1 capitalize text-sm
            ${theme === t
                                ? "btn-primary"
                                : "btn-tertiary"}`}
                    >
                        {t}
                    </button>
                ))}
            </div>
        </div>
    )
}
