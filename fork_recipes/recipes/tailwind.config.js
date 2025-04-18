/** @type {import('tailwindcss').Config} */
module.exports = {
content: ['./templates/**/*.html', '../schedule/templates/**/*.html', "../shopping/templates/**/*.html", "../settings/templates/**/*.html"],
  darkMode: 'class',
  theme: {
    extend: {
    textDecoration: {
        'line-through': 'line-through',
      },
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
      fancy: ['"Young Serif"', 'sans-serif'],
        outfit: ['"Outfit"', 'serif'],
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
      'nutmeg': '#854632',
      'eggshell': '#f3e6d8',
      'wenge-brown': '#5f574e',
      'dark-charcoal': '#302d2c',
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
  safelist: [
    {
      pattern: /^peer(-.*)?$/,
    },
    'peer-checked:after:translate-x-full',
    'peer-checked:bg-mint-600',
    'after:absolute',
    'after:top-[2px]',
    'after:start-[2px]',
    'after:h-5',
    'after:w-5',
    'after:rounded-full',
    'after:border',
    'after:border-gray-300',
    'after:bg-white',
    'after:transition-all',
    'after:content-[\'\']',
    'h-6',
    'w-11',
    'rounded-full',
    'border',
    'border-gray-300',
    'bg-gray-200',
    'transition-colors',
    'focus:outline-none',
    'focus:ring-2',
    'focus:ring-mint-600',
    'focus:ring-offset-2',
  ],
  plugins: [
    require('@tailwindcss/container-queries'),
    function({ addComponents }) {
      addComponents({
        '@media print': {
          '.print-img': {
            maxWidth: '100%',
            height: '400px',  // Adjust this value for A4 paper
            objectFit: 'cover',
            display: 'block',
            margin: '0 auto',
          },
        },
        'media-controller': {
          '--media-background-color': 'transparent',
          '--media-control-background': 'transparent',
          '--media-control-hover-background': 'transparent',
          display: 'block',
          opacity: '1 !important',
          '& button': {
            opacity: '1 !important',
          }
        },
        'media-control-bar': {
          width: '100%',
          height: '5rem',
          '@screen md': {
            height: '4rem',
            borderRadius: '0.375rem',
            borderWidth: '1px',
            borderColor: 'rgb(226 232 240)', // slate-200 color
            borderStyle: 'solid',
          },
          padding: '0 1rem',
          backgroundColor: 'white',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.05)',
          position: 'relative',
          overflow: 'hidden', // Add this to contain the progress bar
        },
        'media-time-range': {
          '--media-range-track-background': 'transparent',
          '--media-time-range-buffered-color': 'rgb(0 0 0 / 0.02)',
          '--media-range-bar-color': 'rgb(77 184 141)',
          '--media-range-track-height': '0.5rem',
          '--media-range-thumb-background': 'rgb(77 184 141)',
          '--media-range-thumb-box-shadow': '0 0 0 2px rgb(255 255 255 / 0.9)',
          '--media-range-thumb-width': '0.25rem',
          '--media-range-thumb-height': '1rem',
          '--media-preview-time-text-shadow': 'transparent',
          '--media-range-track-border-radius': '0',
          display: 'block',
          width: '100%',
          height: '0.5rem',
          minHeight: '0',
          padding: '0',
          backgroundColor: 'rgb(248 250 252)',
          '&.block\\@md\\:hidden': {
            position: 'absolute',
            top: '0',
            left: '0',
            right: '0',
            margin: '0',
            borderRadius: '0',
          },
          '&.hidden\\@md\\:block': {
            flexGrow: '1',
            margin: '0 1rem',
            borderRadius: '0.375rem',
          },
        },
        'media-play-button': {
          height: '2.5rem',
          width: '2.5rem',
          margin: '0 0.75rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderRadius: '9999px',
          backgroundColor: 'rgb(77 184 141)',
          color: 'white',
          transition: 'background-color 150ms',
          '&:hover': {
            backgroundColor: 'rgb(68 164 126)',
          },
          '& button': {
            width: '100%',
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
          }
        },
        'media-time-display': {
          color: 'rgb(17 24 39)',
          fontSize: '0.875rem',
          '&.order-last': {
            '@screen md': {
              order: 'initial',
            }
          }
        },
        'media-duration-display': {
          color: 'rgb(17 24 39)',
          fontSize: '0.875rem',
          '&.hidden': {
            '@screen md': {
              display: 'block',
            }
          }
        },
        'media-mute-button': {
          color: 'rgb(77 184 141)',
          transition: 'color 150ms',
          '&.order-first': {
            '@screen md': {
              order: 'initial',
            }
          },
          '&:hover': {
            color: 'rgb(68 164 126)',
          },
          '& button': {
            color: 'currentColor',
          }
        },
      });
    }
  ],
};
