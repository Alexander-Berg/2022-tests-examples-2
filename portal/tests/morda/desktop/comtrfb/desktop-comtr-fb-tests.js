/* globals gemini */
var Suite = require('../../../suite');
var mocks = require('../../../mocks').desktop.comTr;
var usefull = require('../../../usefull');
var suitesPresets = require('../../../suites-presets-desktop');


var setFbPopupChecks = function (suite) {
    suite
        .before(usefull.cleatLs)
        .before(usefull.stopZoomFbComtr)
        .setCaptureElements('.reset__popup>.popup__content')
        .capture('plain', function (actions) {
            usefull.stopZoomFbComtr(actions);
            usefull.showComtrFbSetPopup(actions);
            actions.wait(300);
        });
};


var suites = [
    new Suite('footer_gs', [mocks.default], suitesPresets.comFooterChecks, {path: 'gs'}),
    new Suite('set_fb_gs', [mocks.default], setFbPopupChecks, {path: 'gs'}),
    new Suite('logo_gs', [mocks.default], suitesPresets.comtrLogoChecks, {path: 'gs'}),
    new Suite('search_tabs_gs', [mocks.default], suitesPresets.comtrSearchTabsChecks, {path: 'gs'}),
    new Suite('virtual_keyboard_gs', [mocks.default], suitesPresets.vkChecks, {path: 'gs'}),
    new Suite('auth', [mocks.auth, mocks.auth_long], suitesPresets.comtrAuthChecks,{path: 'gs'}),
    new Suite('header_gs', [mocks.default], suitesPresets.comtrHeaderChecks, {path: 'gs'}),
    new Suite('search_input', [mocks.default], suitesPresets.searchInputChecks,{path: 'gs'}),
    new Suite('informers_gs', [mocks.traffic, mocks.no_traffic], suitesPresets.comtrInformersChecks, {path: 'gs'})
];


gemini.suite('desktop yandex.com.tr fb', function () {
    suites.forEach(function (suite) {
        suite.run();
    });
});