/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBase: '#050505',
        brandPink: '#ec4899',
        brandIndigo: '#6366f1'
      },
      backgroundImage: {
        'gradient-brand': 'linear-gradient(to right, #ec4899, #6366f1)',
      }
    },
  },
  plugins: [],
}
