const { defineConfig } = require('cypress')

module.exports = defineConfig({
  retries: 1,
  viewportHeight: 1200,
  viewportWidth: 1600,
  numTestsKeptInMemory: 5,
  projectId: 'ynoqzw',
  e2e: {
    // We've imported your old cypress plugins here.
    // You may want to clean this up later by importing these.
    setupNodeEvents(on, config) {
      return require('./cypress/plugins/index.js')(on, config)
    },
    specPattern: 'cypress/e2e/**/*.{js,jsx,ts,tsx}',
  },
})
