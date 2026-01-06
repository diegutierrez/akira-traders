/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Colores principales (Binance-inspired)
        primary: {
          DEFAULT: '#F0B90B',
          dark: '#C99C0A',
          light: '#F3C94D',
        },
        // Fondos
        bg: {
          primary: '#0B0E11',
          secondary: '#1E2329',
          tertiary: '#2B3139',
        },
        // Texto
        text: {
          primary: '#EAECEF',
          secondary: '#848E9C',
          tertiary: '#5E6673',
        },
        // Estados
        success: '#0ECB81',
        danger: '#F6465D',
        warning: '#F0B90B',
        info: '#3DCFFF',
        // Bordes
        border: {
          DEFAULT: '#2B3139',
          hover: '#474D57',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}