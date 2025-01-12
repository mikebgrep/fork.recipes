/** @type {import('tailwindcss').Config} */
module.exports = {
content: ['./templates/**/*.html'],
  darkMode: 'class',
  theme: {
    extend: {
        animation: {
        spin: 'spin 1s linear infinite',
        pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        spin: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        pulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '.5' },
        },
      },
      fontFamily: {
        body: [
          'Inter',
          'ui-sans-serif',
          'system-ui',
          '-apple-system',
          'system-ui',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'Noto Sans',
          'sans-serif',
          'Apple Color Emoji',
          'Segoe UI Emoji',
          'Segoe UI Symbol',
          'Noto Color Emoji'
        ],
        sans: [
          'Inter',
          'ui-sans-serif',
          'system-ui',
          '-apple-system',
          'system-ui',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'Noto Sans',
          'sans-serif',
          'Apple Color Emoji',
          'Segoe UI Emoji',
          'Segoe UI Symbol',
          'Noto Color Emoji'
        ],
      },

      colors: {
        mint: {
          50: '#edfbf6',
          100: '#d3f5e8',
          200: '#56cc9d',
          300: '#56cc9d',
          400: '#56cc9d',
          500: '#56cc9d',
          600: '#4db88d',
          700: '#44a47e',
          800: '#3b906e',
          900: '#327c5f',
        },
        primary: {
          50: '#edfbf6',
          100: '#d3f5e8',
          200: '#56cc9d',
          300: '#56cc9d',
          400: '#56cc9d',
          500: '#56cc9d',
          600: '#4db88d',
          700: '#44a47e',
          800: '#3b906e',
          900: '#327c5f',
        },

      }
    },
  },
  plugins: [],
};
