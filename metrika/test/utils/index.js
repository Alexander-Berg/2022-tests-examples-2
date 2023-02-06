const { e2eTestRun } = require('./e2e');
const { seleniumTestRun } = require('./selenium.js');

const { versionList, last } = require('./vault');
const { runProxy } = require('./proxy');

module.exports = {
    runProxy,
    seleniumTestRun,
    e2eTestRun,
    last,
    versionList,
};
