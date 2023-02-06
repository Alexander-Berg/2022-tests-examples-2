const path = require('path');
const baseConfig = require('../base-hermione.conf');

module.exports = {
    ...baseConfig,

    screenshotsDir: path.join(__dirname, '/screens'),

    sets: {
        common: {
            files: path.join(__dirname, '/screenshooter'),
        },
    },
};
