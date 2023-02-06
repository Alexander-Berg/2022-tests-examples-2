// ***********************************************************
// This example plugins/index.js can be used to load plugins
//
// You can change the location of this file or turn off loading
// the plugins file with the 'pluginsFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/plugins-guide
// ***********************************************************

// This function is called when a project is opened or re-opened (e.g. due to
// the project's config changing)
const fs = require('fs');
const cucumber = require('cypress-cucumber-preprocessor').default;

module.exports = (on, config) => {
    // `on` is used to hook into various events Cypress emits
    // `config` is the resolved Cypress config
    on('task', {
        readFileMaybe(filename) {
            if (fs.existsSync(filename)) {
                const contents = fs.readFileSync(filename, 'utf8');
                return contents ? JSON.parse(contents) : {};
            }
            return {};
        }
    });
    on('file:preprocessor', cucumber());

    config.env.yavOauthToken = process.env.YAV_TOKEN;
    return config;
};
