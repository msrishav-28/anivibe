import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class'],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    container: {
      center: true,
      padding: {
        DEFAULT: '1rem',
        sm: '2rem',
        lg: '4rem',
        xl: '5rem',
        '2xl': '6rem',
      },
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))', // #050505
        foreground: 'hsl(var(--foreground))',

        // Neo-Tokyo Palette
        primary: {
          DEFAULT: '#8B5CF6', // Spirit: Electric Violet
          50: '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#4c1d95',
          950: '#2e1065',
          foreground: '#ffffff',
        },
        secondary: {
          DEFAULT: '#00F0FF', // Tech: Neon Cyan
          foreground: '#000000',
        },
        alert: {
          DEFAULT: '#FF0055', // Hype: Crimson
          foreground: '#ffffff',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        // Anime genre colors
        anime: {
          action: '#ef4444',
          romance: '#ec4899',
          fantasy: '#8b5cf6',
          scifi: '#3b82f6',
          thriller: '#6366f1',
          comedy: '#f59e0b',
          drama: '#8b5cf6',
          sliceoflife: '#10b981',
          mystery: '#6366f1',
          horror: '#dc2626',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      fontFamily: {
        sans: ['var(--font-satoshi)', 'var(--font-inter)', 'system-ui', 'sans-serif'], // Body
        heading: ['var(--font-clash)', 'var(--font-outfit)', 'system-ui', 'sans-serif'], // Headers
        accent: ['var(--font-zen)', 'sans-serif'], // Decorative
        mono: ['var(--font-jetbrains-mono)', 'monospace'],
      },
      boxShadow: {
        'glow': '0 0 20px rgba(139, 92, 246, 0.5)', // Increased opacity
        'glow-lg': '0 0 40px rgba(139, 92, 246, 0.6)',
        'neon-green': '0 0 10px #10B981',
        'float': '0 20px 25px -5px rgb(0 0 0 / 0.1)',
      },
      backgroundImage: {
        'gradient-spirit': 'linear-gradient(to right, #8B5CF6, #6366F1)',
        'gradient-holo': 'linear-gradient(115deg, transparent, rgba(255,255,255,0.2), transparent)',
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        'fade-in': 'fade-in 0.3s ease-out',
        'fade-out': 'fade-out 0.3s ease-out',
        'glitch': 'glitch 1s linear infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 3s linear infinite',
        // Radix Animations
        'scale-in': 'scale-in 0.2s ease-out',
        'scale-out': 'scale-out 0.2s ease-in',
        'zoom-in-95': 'zoom-in-95 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
        'zoom-out-95': 'zoom-out-95 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
        'slide-in-from-top-2': 'slide-in-from-top-2 0.2s ease-out',
        'slide-in-from-bottom-2': 'slide-in-from-bottom-2 0.2s ease-out',
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'fade-out': {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        'glitch': {
          '2%, 64%': { transform: 'translate(2px,0) skew(0deg)' },
          '4%, 60%': { transform: 'translate(-2px,0) skew(0deg)' },
          '62%': { transform: 'translate(0,0) skew(5deg)' },
        },
        // Native-like transitions for Radix Primitives
        'scale-in': {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'scale-out': {
          'from': { transform: 'scale(1)', opacity: '1' },
          'to': { transform: 'scale(0.95)', opacity: '0' },
        },
        'zoom-in-95': {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'zoom-out-95': {
          'from': { transform: 'scale(1)', opacity: '1' },
          'to': { transform: 'scale(0.95)', opacity: '0' },
        },
        'slide-in-from-top-2': {
          'from': { transform: 'translateY(-0.5rem)', opacity: '0' },
          'to': { transform: 'translateY(0)', opacity: '1' },
        },
        'slide-in-from-bottom-2': {
          'from': { transform: 'translateY(0.5rem)', opacity: '0' },
          'to': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('tailwindcss-animate'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/aspect-ratio'),
  ],
};

export default config;
