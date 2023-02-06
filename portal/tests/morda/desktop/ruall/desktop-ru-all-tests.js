/* globals gemini */
var Suite = require('../../../suite');
var mocks = require('../../../mocks').desktop.all;
var suitesPresets = require('../../../suites-presets-desktop');




var suites = [
    new Suite('footer', [mocks.default], suitesPresets.allFooterChecks, {path: 'all'}),
    new Suite('header', [mocks.default], suitesPresets.allHeaderChecks, {path: 'all'}),
    new Suite('services_main', [mocks.default],suitesPresets.allMainServicesChecks, {path: 'all'}),
    new Suite('services_all', [mocks.default],suitesPresets.allServicesChecks, {path: 'all'}),
    new Suite('services_bottom', [mocks.default], suitesPresets.allBottomServicesChecks, {path: 'all'}),
    new Suite('services_special', [mocks.default], suitesPresets.allSpecialServicesChecks, {path: 'all'})
];


gemini.suite('desktop yandex.ru/all', function () {
    suites.forEach(function (suite) {
        suite.run();
    });
});
