/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html'
  ],
  darkMode: 'class',
  theme: {
    extend: {
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
