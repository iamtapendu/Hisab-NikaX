import { useEffect, useState } from "react"

const THEMES = ["light", "dark", "warm"]

export default function useTheme() {
    const [theme, setTheme] = useState(
        () => localStorage.getItem("theme") || "light"
    )

    useEffect(() => {
        const root = document.documentElement

        // remove all theme classes first
        root.classList.remove("dark", "warm")

        // apply selected theme
        if (theme !== "light") {
            root.classList.add(theme)
        }

        localStorage.setItem("theme", theme)
    }, [theme])

    return { theme, setTheme, themes: THEMES }
}
