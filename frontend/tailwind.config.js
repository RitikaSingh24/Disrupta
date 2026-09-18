/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Brand / UI theme — dark evergreen + warm ivory
        navy: {
          DEFAULT: '#1D312A',   // Deep Forest — was #0F172A
        },
        slate: {
          DEFAULT: '#3D5247',   // Muted evergreen text — was #334155
          light: '#F4F1EA',     // Warm ivory light surface — was #F8FAFC
        },
        orange: {
          DEFAULT: '#F97316',   // CTA accent — unchanged
        },
        // Semantic status colors — DO NOT CHANGE
        success: '#16A34A',
        danger:  '#DC2626',
        warning: '#D97706',
      },
    },
  },
  plugins: [],
}