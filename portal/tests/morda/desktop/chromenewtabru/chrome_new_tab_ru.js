/* globals gemini */
var Suite = require('../../../suite');
var mocks = require('../../../mocks').desktop.chromenewtab;
var suitesPresets = require('../../../suites-presets-desktop');


var suites = [
    new Suite('search_input', [mocks.default], suitesPresets.searchInputChecks, {getParam: 'content=chromenewtab'}),
    new Suite('informers', [mocks.default], suitesPresets.newTabInformersChecks, {getParam: 'content=chromenewtab'}),
    new Suite('logo+arrow', [mocks.default], suitesPresets.comMainRowChecks, {getParam: 'content=chromenewtab'})
];


gemini.suite('chromenewtab.ru', function () {
    suites.forEach(function (suite) {
        suite.run();
    });
});