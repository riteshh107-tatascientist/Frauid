/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'dark-bg': '#0f172a',
        'dark-secondary': '#1e293b',
        'dark-tertiary': '#334155',
        'accent-red': '#ef4444',
        'accent-green': '#10b981',
        'accent-yellow': '#f59e0b',
        'accent-blue': '#3b82f6',
      },
      backgroundImage: {
        'gradient-dark': 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
      },
    },
  },
  plugins: [],
}
