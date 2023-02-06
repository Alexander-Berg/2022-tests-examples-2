/* globals gemini */
var Suite = require('../../../suite');
var mocks = require('../../../mocks').desktop.com;
var suitesPresets = require('../../../suites-presets-desktop');


var countriesChecks = function (suite) {
    suite
        .setCaptureElements('.b-line__worldwide')
        .capture('plain');
};


var suites = [
    new Suite('footer', [mocks.en, mocks.id], suitesPresets.comFooterChecks, {getParam: 'redirect=0'}),
    new Suite('search_input', [mocks.en, mocks.id], suitesPresets.searchInputChecks, {getParam: 'redirect=0'}),
    new Suite('search_tabs', [mocks.en, mocks.id], suitesPresets.comtrSearchTabsChecks, {getParam: 'redirect=0'}),
    new Suite('virtual_keyboard', [mocks.en, mocks.id], suitesPresets.vkChecks, {getParam: 'redirect=0'}),
    new Suite('countries', [mocks.en, mocks.id], countriesChecks, {getParam: 'redirect=0'}),
    new Suite('header', [mocks.en, mocks.id, mocks.auth_en, mocks.auth_id, mocks.auth_long], suitesPresets.langSwitchChecks, {getParam: 'redirect=0'}),
    new Suite('logo+arrow', [mocks.default], suitesPresets.comMainRowChecks, {getParam: 'redirect=0'})
];


gemini.suite('desktop yandex.com', function () {
    suites.forEach(function (suite) {
        suite.run();
    });
});
