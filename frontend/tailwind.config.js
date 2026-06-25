/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Aesthetic premium dark color palette
        dark: {
          950: '#030712',
          900: '#111827',
          800: '#1f2937',
          700: '#374151',
          600: '#4b5563',
        },
        brand: {
          500: '#6366f1', // Indigo
          600: '#4f46e5',
          700: '#4338ca',
        }
      }
    },
  },
  plugins: [],
}
