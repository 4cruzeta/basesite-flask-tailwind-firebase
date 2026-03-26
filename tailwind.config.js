/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './edcat_root/pages/templates/**/*.html',
    './edcat_root/web_client/templates/**/*.html', // <-- Adicionado para incluir os templates do novo cliente web
  ],
  darkMode: 'media',
  theme: {
    extend: {
      colors: {
        primary: '#6D28D9', // Cor roxa principal do novo design
        secondary: '#4C1D95', // Tom de roxo mais escuro
      }
    },
  },
  plugins: [],
}
