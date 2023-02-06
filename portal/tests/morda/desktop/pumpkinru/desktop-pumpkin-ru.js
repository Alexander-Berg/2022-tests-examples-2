/* globals gemini */
var Suite = require('../../../suite');
var mocks = require('../../../mocks').desktop.pumpkin;
var suitesPresets = require('../../../suites-presets-desktop');


var suites = [
    new Suite('footer_logo', [mocks.default], suitesPresets.yaruFooterChecks, {path: 'pumpkin/ru/'}),
    new Suite('search_input', [mocks.default], suitesPresets.searchInputChecks, {path: 'pumpkin/ru/'})
];


gemini.suite('desktop pumpkin ru', function () {
    suites.forEach(function (suite) {
        suite.run();
    });
});
