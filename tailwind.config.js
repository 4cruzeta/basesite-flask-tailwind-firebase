/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './edcat_root/pages/templates/**/*.html',
    './edcat_root/web_client/templates/**/*.html', // <-- Adicionado para incluir os templates do novo cliente web
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
