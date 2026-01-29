/** @type {import('tailwindcss').Config} */
export default {
	darkMode: ["class"],
	content: [
		"./index.html",
		"./src/**/*.{js,jsx,ts,tsx}",
	],
	theme: {
		extend: {
			borderRadius: {
				lg: 'var(--radius)',
				md: 'calc(var(--radius) - 2px)',
				sm: 'calc(var(--radius) - 4px)'
			},
			colors: {
				background: 'hsl(var(--background))',
				foreground: 'hsl(var(--foreground))',
				primary: 'hsl(var(--primary))',
				'primary-hv': 'hsl(var(--primary-hv))',
				secondary: 'hsl(var(--secondary))',
				'secondary-hv': 'hsl(var(--secondary-hv))',
				tertiary: 'hsl(var(--tertiary))',
				'tertiary-hv': 'hsl(var(--tertiary-hv))',
				muted: 'hsl(var(--muted))',
				// accent: 'hsl(var(--accent))',
				danger: 'hsl(var(--danger))',
				'danger-hv': 'hsl(var(--danger-hv))',
				success: 'hsl(var(--success))',
				'success-hv': 'hsl(var(--success-hv))',

			}
		}
	}
};
