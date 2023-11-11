const path = require('path');

const projectPaths = [
    path.join(__dirname, './templates/**/*.html')
];

const contentPaths = [...projectPaths];

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: contentPaths,
  theme: {
    extend: {},
  },
  plugins: [],
};