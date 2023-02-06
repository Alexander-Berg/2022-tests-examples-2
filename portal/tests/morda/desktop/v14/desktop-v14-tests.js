/* globals gemini */
var Suite = require('../../../suite');
var mocks = require('../../../mocks').desktop.v14;
var usefull = require('../../../usefull');
var suitesPresets = require('../../../suites-presets-desktop');


var footerChecks = function (suite) {
    suite
        .before(usefull.setFontV14)
        .setCaptureElements('.media-grid')
        .capture('plain', function (actions) {
            usefull.hideMediaFooter(actions);
            actions.wait(300);
        });
};


var headerChecks = function (suite) {
    suite
        .before(usefull.setFontV14)
        .setCaptureElements('.rows__row_first')
        .capture('plain');
};


var domikChecks = function (suite) {
    suite
        .before(usefull.setFontV14)
        .before(usefull.hideTeaser)
        .setCaptureElements('.desk-notif-card__card')
        .capture('plain');
};


var domikLoginChecks = function (suite) {
    suite
        .before(usefull.setFontV14)
        .setCaptureElements('.desk-notif-card__card')
        .capture('plain');
};


var domikStaleChecks = function (suite) {
    suite
        .before(usefull.setFontV14)
        .setCaptureElements('.desk-notif-card__card')
        .capture('plain')
        .capture('isnt_me', function (actions) {
            actions
                .click('.domik3__stale-not-me')
                .wait(300);
        });
};


var arrowRowChecks = function (suite) {
    suite
        .before(usefull.setFontV14)
        .setCaptureElements('.col_home-arrow')
        .capture('plain');
};


var popupMoreChecks = function (suite) {
    suite
        .before(usefull.setFontV14)
        .before(function (actions) {
            actions
                .click('.home-tabs__more-switcher')
                .wait(300);
        })
        .setCaptureElements('.home-tabs__more')
        .capture('plain');
};


var popupOptionsChecks = function (suite) {
    suite
        .before(usefull.setFontV14)
        .before(usefull.hideTeaser)
        .before(function (actions) {
            actions
                .click('.head-options2__link')
                .wait(300);
        })
        .setCaptureElements('.b-menu-vert__layout .popup__content')
        .capture('plain');
};


var topNewsBlockChecks = function (suite) {
    suite
        .before(usefull.setFontV14)
        .ignoreElements('.datetime__time')
        .setCaptureElements('.col_td_0')
        .capture('plain')
        .capture('changed_tab', function (actions) {
            actions
                .click('.content-tabs__head-item_active_false')
                .mouseMove('.geolink__reg')
                .wait(300);
        });
};


var weatherBlockChecks = function (suite) {
    suite
        .before(usefull.setFontV14)
        .setCaptureElements('[id="wd-wrapper-_weather"]')
        .capture('plain');
};


var trafficBlockChecks = function (suite) {
    suite
        .before(usefull.setFontV14)
        .setCaptureElements('[id="wd-wrapper-_traffic"]')
        .capture('plain');
};


var geoBlockChecks = function (suite) {
    suite
        .before(usefull.setFontV14)
        .setCaptureElements('[id="wd-wrapper-_geo"]')
        .capture('plain');
};


var servicesBlockChecks = function (suite) {
    suite
        .before(usefull.setFontV14)
        .setCaptureElements('[id="wd-wrapper-_services"]')
        .capture('plain');
};


var tvBlockChecks = function (suite) {
    suite
        .before(usefull.setFontV14)
        .setCaptureElements('[id="wd-wrapper-_tv"]')
        .capture('plain');
};


var afishaBlockChecks = function (suite) {
    suite
        .setCaptureElements('[id="wd-wrapper-_afisha"]')
        .capture('plain');
};


var themesCatalogChecks = function (suite) {
    suite
        .before(usefull.setFontV14)
        .setCaptureElements('.b-themes-catalog')
        .capture('plain')
        .capture('tab_new_hovered', function (actions) {
            actions
                .mouseMove('.b-themes-catalog__tab_name_new')
                .wait(300);
        })
        .capture('theme_hovered', function (actions) {
            actions
                .mouseMove('.b-themes-catalog__theme-item:nth-child(5)')
                .wait(300);
        })
        .capture('arrow_hovered', function (actions) {
            actions
                .mouseMove('.b-themes-catalog__arrow_scroll_right')
                .wait(300);
        })
        .capture('arrow_used', function (actions) {
            actions
                .click('.b-themes-catalog__arrow_scroll_right')
                .wait(300);
        })
        .capture('tab_new', function (actions) {
            actions
                .click('.b-themes-catalog__tab_name_new')
                .wait(300);
        })
        .capture('tab_food', function (actions) {
            actions
                .click('.b-themes-catalog__tab_name_food')
                .wait(300);
        });
};


var themesPromoChecks = function (suite) {
    suite
        .before(usefull.setFontV14)
        .setCaptureElements('.themes-promo__wrapper')
        .capture('plain')
        .capture('hovered_text', function (actions) {
            actions
                .mouseMove('.themes-promo__wrapper')
                .wait(300);
        })
        .capture('hovered_close', function (actions) {
            actions
                .mouseMove('.themes-promo__close')
                .wait(300);
        });
};


var editChecks = function (suite) {
    suite
        .before(usefull.setFontV14)
        .setCaptureElements('.catalog__plate')
        .capture('plain')
        .capture('hovered_reset', function (actions) {
            actions
                .mouseMove('.catalog__reset')
                .wait(300);
        })
        .capture('hovered_revert', function (actions) {
            actions
                .mouseMove('.catalog__revert')
                .wait(300);
        });
};


var suites = [
    new Suite('footer', [mocks.default], footerChecks),
    new Suite('header', [mocks.default, mocks.authSocial, mocks.auth], headerChecks),
    new Suite('domik', [mocks.default], domikChecks),
    new Suite('domik', [mocks.authSocial, mocks.auth], domikLoginChecks),
    new Suite('arrow_row', [mocks.example], arrowRowChecks),
    new Suite('popup_more', [mocks.default], popupMoreChecks),
    new Suite('popups_options', [mocks.default], popupOptionsChecks),
    new Suite('domik_stale', [mocks.staleLogin], domikStaleChecks),
    new Suite('news_block', [mocks.topNews], topNewsBlockChecks),
    new Suite('weather_block', [mocks.weather], weatherBlockChecks),
    new Suite('traffic_block', [mocks.traffic], trafficBlockChecks),
    new Suite('geo_block', [mocks.geoBlock], geoBlockChecks),
    new Suite('services_block', [mocks.services], servicesBlockChecks),
    new Suite('tv_block', [mocks.tv], tvBlockChecks),
    new Suite('afisha_block', [mocks.afisha], afishaBlockChecks),
    new Suite('themes_catalog', [mocks.default], themesCatalogChecks, {path: 'themes'}),
    new Suite('theme_promo', [mocks.themePromo], themesPromoChecks),
    new Suite('edit_mod', [mocks.default], editChecks, {getParam: 'edit=1'})
];


gemini.suite('desktop yandex.ru', function () {
    suites.forEach(function (suite) {
        suite.run();
    });
});
