/* globals gemini */
var Suite = require('../../../suite');
var mocks = require('../../../mocks').desktop.comTr;
var suitesPresets = require('../../../suites-presets-desktop');


var distPopupChecks = function (suite) {
    suite
        .before(function (actions) {
            actions
                .waitForElementToShow('.dist-popup_install_inline', 1000);
        })
        .setCaptureElements('.dist-popup_install_inline')
        .capture('plain');
};


var suites = [
    new Suite('footer', [mocks.default], suitesPresets.comFooterChecks),
    new Suite('dist_popup', [mocks.dist_popup], distPopupChecks),
    new Suite('search_input', [mocks.tr], suitesPresets.searchInputChecks),
    new Suite('search_tabs', [mocks.tr], suitesPresets.comtrSearchTabsChecks),
    new Suite('virtual_keyboard', [mocks.tr], suitesPresets.vkChecks),
    new Suite('header', [mocks.tr], suitesPresets.comtrHeaderChecks),
    new Suite('auth', [mocks.auth, mocks.auth_long], suitesPresets.comtrAuthChecks),
    new Suite('informers', [mocks.traffic, mocks.no_traffic], suitesPresets.comtrInformersChecks),
    new Suite('logo+arrow', [mocks.default], suitesPresets.comtrLogoChecks)
];


gemini.suite('desktop yandex.com.tr', function () {
    suites.forEach(function (suite) {
        suite.run();
    });
});
