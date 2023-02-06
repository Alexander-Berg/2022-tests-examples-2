/* globals gemini */
var Suite = require('../../../suite');
var mocks = require('../../../mocks').desktop.ff;
var suitesPresets = require('../../../suites-presets-desktop');


var suites = [
    new Suite('footer', [mocks.default], suitesPresets.comFooterChecks),
    new Suite('search_input', [mocks.ffInformers], suitesPresets.searchInputChecks),
    new Suite('search_tabs', [mocks.default], suitesPresets.searchTabsChecks),
    new Suite('virtual_keyboard', [mocks.default], suitesPresets.vkChecks),
    new Suite('informers', [mocks.ffInformers], suitesPresets.ffInformersChecks),
    new Suite('logo', [mocks.default], suitesPresets.ffLogoChecks),
    new Suite('logo+arrow', [mocks.default], suitesPresets.comMainRowChecks)
];


gemini.suite('desktop firefox.ru', function () {
    suites.forEach(function (suite) {
        suite.run();
    });
});
