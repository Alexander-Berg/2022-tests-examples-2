/* globals gemini */
var Suite = require('../../../suite');
var mocks = require('../../../mocks').desktop.spok;
var usefull = require('../../../usefull');
var suitesPresets = require('../../../suites-presets-desktop');


var footerChecks = function (suite) {
    suite
        .setCaptureElements('.mfooter')
        .capture('plain',function (actions) {
            usefull.footerCollapse(actions);
            actions.wait(300);
        });
};

var suites = [
    new Suite('footer', [mocks.langUa, mocks.langRu, mocks.langEn], footerChecks),
    new Suite('search_input', [mocks.langUa, mocks.langRu, mocks.langEn], suitesPresets.searchInputChecks),
    new Suite('search_tabs', [mocks.langUa, mocks.langRu, mocks.langEn], suitesPresets.comtrSearchTabsChecks),
    new Suite('virtual_keyboard', [mocks.langUa, mocks.langRu, mocks.langEn], suitesPresets.vkChecks),
    new Suite('header', [mocks.langUa, mocks.langRu, mocks.langEn], suitesPresets.langSwitchChecks),
    new Suite('auth', [mocks.authEn, mocks.authRu, mocks.authUa, mocks.authLongEn, mocks.authLongRu, mocks.authLongUa], suitesPresets.comtrHeaderChecks)
];


gemini.suite('desktop yandex.fr', function () {
    suites.forEach(function (suite) {
        suite.run();
    });
});
