/* globals gemini */
var Suite = require('../../../suite');
var mocks = require('../../../mocks').desktop.yaru;
var suitesPresets = require('../../../suites-presets-desktop');


var logoChecks = function (suite) {
    suite
        .setCaptureElements('.layout__footer-logo')
        .capture('plain');
};


var headerChecks = function (suite) {
    suite
        .setCaptureElements('.layout__header')
        .capture('plain');
};


var suites = [
    new Suite('footer', [mocks.default], suitesPresets.yaruFooterChecks),
    new Suite('search_input', [mocks.default], suitesPresets.searchInputChecks),
    new Suite('header', [mocks.default], headerChecks),
    new Suite('main_logo', [mocks.default], logoChecks)
];


gemini.suite('desktop ya.ru', function () {
    suites.forEach(function (suite) {
        suite.run();
    });
});
