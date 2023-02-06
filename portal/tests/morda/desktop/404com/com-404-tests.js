/* globals gemini */
var Suite = require('../../../suite');
var mocks = require('../../../mocks').desktop['404'];
var usefull = require('../../../usefull');
var suitesPresets = require('../../../suites-presets-desktop');


var suites = [
    new Suite('footer', [mocks.default], suitesPresets.footer404Checks, {path: 'sl'}),
    new Suite('search_input', [mocks.default], suitesPresets.searchInputChecks, {path: 'sl'}),
    new Suite('virtual_keyboard', [mocks.default], suitesPresets.vkChecks, {path: 'sl'}),
    new Suite('logo+arrow', [mocks.default], suitesPresets.logo404Checks, {path: 'sl'}),
    new Suite('text_under_arrow', [mocks.default], suitesPresets.mainBlock404Checks, {path: 'sl'})
];


gemini.suite('desktop yandex.com 404', function () {
    suites.forEach(function (suite) {
        suite.run();
    });
});