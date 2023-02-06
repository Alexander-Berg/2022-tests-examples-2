var usefull = require('./usefull');


var searchInputChecks = function (suite) {
    suite
        .before(usefull.stopZoomFbComtr)
        .ignoreElements({every: '.suggest2-item'})
        .setCaptureElements('.search2', '.suggest2')
        .capture('plain')
        .capture('with_suggest', function (actions) {
            actions
                .sendKeys('.input__input', 'gemini')
                .waitForElementToShow('.suggest2', 1000)
                .wait(500);
        });
};


var vkChecks = function (suite) {
    suite
        .before(usefull.stopScroll)
        .setCaptureElements('.b-keyboard')
        .capture('opened', function (actions) {
            actions
                .click('.keyboard-loader')
                .waitForElementToShow('.b-keyboard', 500)
                .mouseMove('.b-keyboard__row');

        })
        .capture('languages_popup', function (actions) {
            actions
                .click('.b-keyboard__switcher')
                .waitForElementToShow('.b-keyboard__langs', 500)
                .mouseMove('.b-keyboard__row');

        })
        .after(function (actions) {
            actions
                .click('.b-keyboard-popup__close')
                .waitForElementToHide('.b-keyboard__langs', 500)
                .mouseMove('.b-keyboard__row');
        });
};


var searchTabsChecks = function (suite) {
    suite
        .setCaptureElements('.tabs2')
        .capture('plain')
        .capture('hovered', function (actions, find) {
            actions
                .mouseMove(find('.link__tab2'))
                .wait(300);
        });
};

var comFooterChecks = function (suite) {
    suite
        .setCaptureElements('.b-line__mfooter')
        .capture('plain', usefull.stopZoomFbComtr);
};

var ffInformersChecks = function (suite) {
    suite
        .setCaptureElements('.informers')
        .capture('plain');
};

var newTabInformersChecks = function (suite) {
    suite
        .ignoreElements('.informers__left-inner')
        .setCaptureElements('.informers')
        .capture('plain');
};

var ffLogoChecks = function (suite) {
    suite
        .setCaptureElements('.firefox-logo')
        .capture('plain');
};

var comMainRowChecks = function (suite) {
    suite
        .setCaptureElements('.main')
        .capture('plain');
};

var comtrInformersChecks = function (suite) {
    suite
        .before(usefull.stopZoomFbComtr)
        .setCaptureElements('.b-line__informers')
        .capture('plain', usefull.hideResetPopup);
};

var comtrHeaderChecks = function (suite) {
    suite
        .before(usefull.stopZoomFbComtr)
        .setCaptureElements('.b-line__bar-right')
        .capture('plain', usefull.hideDistPopup);
};

var comtrLogoChecks = function (suite) {
    suite
        .setCaptureElements('.logo', '.search2')
        .capture('plain', usefull.stopZoomFbComtr);
};

var comtrSearchTabsChecks = function (suite) {
    suite
        .before(usefull.stopZoomFbComtr)
        .setCaptureElements('.tabs')
        .capture('plain')
        .capture('hovered', function (actions, find) {
            actions
                .mouseMove(find('.b-tabs__item'))
                .wait(1000);
        });
};

var comtrAuthChecks = function (suite) {
    suite
        .setCaptureElements('.popup_head-options_yes', '.b-line__bar-right')
        .capture('plain', usefull.stopZoomFbComtr)
        .capture('user_popup', function (actions, find) {
            actions
                .click(find('.dropdown-menu__switcher'))
                .wait(300)
                .waitForElementToShow('.popup_head-options_yes', 300);
        });
};

var footer404Checks = function (suite) {
    suite
        .setCaptureElements('.foot')
        .capture('plain');
};

var logo404Checks = function (suite) {
    suite
        .setCaptureElements('.layout__line_top')
        .capture('plain');
};

var mainBlock404Checks = function (suite) {
    suite
        .setCaptureElements('.layout__cell')
        .capture('plain');
};

var allFooterChecks = function (suite) {
    suite
        .setCaptureElements('.footer')
        .capture('plain');
};

var allHeaderChecks = function (suite) {
    suite
        .setCaptureElements('.header')
        .capture('plain', function (actions) {
            actions.focus('.link__grey');
        });
};

var allMainServicesChecks = function (suite) {
    suite
        .setCaptureElements('.b-line__services-main')
        .capture('plain', function (actions) {
            actions.focus('.link__grey');
        });
};


var allServicesChecks = function (suite) {
    suite
        .setCaptureElements('.b-line__services-all')
        .capture('plain', function (actions) {
            actions.focus('.link__grey');
        });
};


var allBottomServicesChecks = function (suite) {
    suite
        .setCaptureElements('.b-line__services-bottom')
        .capture('plain', function (actions) {
            actions.focus('.link__grey');
        });
};


var allSpecialServicesChecks = function (suite) {
    suite
        .setCaptureElements('.b-line__services-special')
        .capture('plain', function (actions) {
            actions.focus('.link__grey');
        });
};

var yaruFooterChecks = function (suite) {
    suite
        .setCaptureElements('.layout__footer')
        .capture('plain')
        .capture('hover_logo', function (actions) {
            actions
                .mouseMove('.layout__footer-logo')
                .wait(300);
        });
};


var langSwitchChecks = function (suite) {
    suite
        .setCaptureElements('.b-line__bar', '.langswitch__popup')
        .capture('plain')
        .capture('language_popup', function (actions) {
            actions
                .click('.langswitch')
                .wait(300);
        });
};


module.exports.searchInputChecks = searchInputChecks;
module.exports.vkChecks = vkChecks;
module.exports.searchTabsChecks = searchTabsChecks;
module.exports.comFooterChecks = comFooterChecks;
module.exports.ffInformersChecks = ffInformersChecks;
module.exports.newTabInformersChecks = newTabInformersChecks;
module.exports.ffLogoChecks = ffLogoChecks;
module.exports.comMainRowChecks = comMainRowChecks;
module.exports.comtrInformersChecks = comtrInformersChecks;
module.exports.comtrHeaderChecks = comtrHeaderChecks;
module.exports.comtrLogoChecks = comtrLogoChecks;
module.exports.comtrSearchTabsChecks = comtrSearchTabsChecks;
module.exports.comtrAuthChecks = comtrAuthChecks;
module.exports.footer404Checks = footer404Checks;
module.exports.logo404Checks = logo404Checks;
module.exports.mainBlock404Checks = mainBlock404Checks;
module.exports.allFooterChecks = allFooterChecks;
module.exports.allHeaderChecks = allHeaderChecks;
module.exports.allSpecialServicesChecks = allSpecialServicesChecks;
module.exports.allBottomServicesChecks = allBottomServicesChecks;
module.exports.allServicesChecks = allServicesChecks;
module.exports.allMainServicesChecks = allMainServicesChecks;
module.exports.yaruFooterChecks = yaruFooterChecks;
module.exports.langSwitchChecks = langSwitchChecks;