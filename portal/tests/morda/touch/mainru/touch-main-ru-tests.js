/* globals gemini BEM $ */

var Suite = require('../../../suite');
var mocks = require('../../../mocks').touch.ru;
var usefull = require('../../../usefull');
var data = require('../../../tests-data');

var headerChecks = function (suite) {
    suite
        .before(usefull.setFont)
        .setCaptureElements('.mheader3')
        .capture('plain', usefull.stopScroll);
};


var wrongDatePopupChecks = function (suite) {
    suite
        .before(usefull.setFont)
        .setCaptureElements('.wrong_date_alert')
        .ignoreElements('.date1', '.date2')
        .capture('plain', usefull.stopScroll);
};


var geoPopupChecks = function (suite) {
    suite
        .before(usefull.setFont)
        .before(function (actions) {
            actions
                .executeJS(function () {
                    BEM.blocks['bottom-popup'].show('geolocation-setup');
                })
        })
        .setCaptureElements('.geolocation-setup__text', '.geolocation-setup__button')
        .capture('failed', function (actions) {
            actions
                .wait(500);
        })
        .capture('blocked', function (actions) {
            actions
                .executeJS(function () {
                    BEM.blocks['geolocation-setup'].showGuideLinkInPopup();
                });
        });
};


var stalePagePopupChecks = function (suite) {
    suite
        .before(usefull.setFont)
        .before(function (actions) {
            actions
                .executeJS(function () {
                    $('.timeload').bem('timeload').setMod('show', 'yes');
                });
        })
        .ignoreElements('.timeload__alert')
        .setCaptureElements('.timeload_js_inited ')
        .capture('plain', usefull.stopScroll);
};


var domikChecks = function (suite) {
    suite
        .before(usefull.setFont)
        .before(function (actions) {
            actions
                .click('.mheader3__user')
                .wait(300)
                .executeJS(function () {
                    document.querySelector('.dialog__overlay').style.backgroundColor = 'aqua';
                });


        })
        .setCaptureElements('body')
        .capture('plain');
};


var domikInputChecks = function (suite) {
    suite
        .before(usefull.setFont)
        .before(function (actions) {
            actions
                .click('.informers7__item_type_mail')
                .wait(300)
                .executeJS(function () {
                    document.querySelector('.dialog__overlay').style.backgroundColor = 'aqua';
                });
        })
        .setCaptureElements('body')
        .capture('empty_inputs', function (actions) {
            actions
                .click('.mdomik__auth-button')
                .wait(300);
        })
        .capture('empty_password', function (actions) {
            actions
                .sendKeys('input[name=\'login\']', 'RichIvan')
                .click('.mdomik__auth-button')
                .wait(300);
        });
};


var menuChecks = function (suite) {
    suite
        .before(usefull.setFont)
        .setCaptureElements('body')
        .capture('plain', function (actions) {
            actions
                .click('.mheader3__menu')
                .wait(300)
                .executeJS(function () {
                    document.querySelector('.menu2__overlay').style.backgroundColor = 'aqua';
                });
        });
};


var footerChecks = function (suite) {
    suite
        .before(usefull.setFont)
        .before(usefull.hideSkinGreetingPopup)
        .setCaptureElements('.mfooter')
        .capture('plain', usefull.stopScroll);
};


var skinPopupChecks = function (suite) {
    suite
        .before(usefull.setFont)
        .before(usefull.showSkinGreetingPopup)
        .setCaptureElements('.skin-greeting__title', '.skin-greeting__notice', '.skin-greeting__close')
        .capture('plain', function (actions) {
            actions
                .wait(1000);
        });
};


var applicationsChecks = function (suite) {
    suite
        .before(usefull.setFont)
        .before(function (actions) {
            actions
                .mouseMove('.apps__content')
                .wait(1500)
        })
        .setCaptureElements('.apps__content')
        .capture('plain', usefull.stopScroll);
};


var servicesChecks = function (suite) {
    suite
        .before(usefull.setFont)
        .before(function (actions) {
            actions
                .mouseMove('.services__title')
                .wait(1500)
        })
        .setCaptureElements('.services__title', '.services__content')
        .capture('plain', usefull.stopScroll);
};


var newsChecks = function (suite) {
    suite
        .before(usefull.setFont)
        .before(usefull.hideSkinGreetingPopup)
        .setCaptureElements('.news .block__title', '.news .swiper__pages', '.news .swiper__categories')
        .capture('plain', function (actions) {
            actions
                .mouseMove('.news .block__title')
                .wait(300);
            usefull.stopScroll(actions);
        });
};


var bridgesCollapsedChecks = function (suite) {
    suite
        .before(usefull.setFont)
        .setCaptureElements('.bridges__collapsed-icon', '.bridges__collapsed-text', '.bridges__arrow')
        .capture('plain', function (actions) {
            actions
                .mouseMove('.bridges__arrow')
                .wait(300);
            usefull.hideSkinGreetingPopup(actions);
            usefull.stopScroll(actions);
        });
};


var bridgesExpandedChecks = function (suite) {
    suite
        .before(function (actions) {
            actions
                .click('.bridges__arrow');
            usefull.setFont(actions);
        })
        .setCaptureElements('.bridges__title ', '.bridges__item:nth-child(7)')
        .capture('expanded', function (actions) {
            usefull.hideSkinGreetingPopup(actions);
            usefull.stopScroll(actions);
            actions
                .mouseMove('.bridges__title-text')
                .wait(300);
        });
};


var timeshiftChecks = function (suite) {
    suite
        .before(usefull.setFont)
        .before(usefull.hideSkinGreetingPopup)
        .setCaptureElements('.notifications__item_type_timeshift')
        .ignoreElements('.datetime')
        .capture('plain', function (actions) {
            actions
                .mouseMove('.datetime')
                .wait(300);
            usefull.stopScroll(actions)
        });
};

var getSuggest = function (actions, reqType, reqText) {
    usefull.inputClear(actions);
    usefull.enchantRequests(actions);
    actions
        .fakeRequest(reqText, data.fakeResRu[reqType])
        .focus('.mini-suggest__input')
        .sendKeys(reqText)
        .wait(300);
};

var typeSuggestChecks = function (suite) {
    suite
        .before(function (actions) {
            usefull.setFont(actions);
            usefull.cleanTouchHeader(actions);
            usefull.stopScroll(actions);
            actions.focus('.mini-suggest__input');
            usefull.strongSuggestOverlay(actions);
        })
        .setCaptureElements('body')
        .capture('traffic', function (actions) {
            getSuggest(actions, 'traffic', 'пробк');
        })
        .capture('weather', function (actions) {
            getSuggest(actions, 'weather_in_spb', 'погода в са');
        })
        .capture('time_to_fall', function (actions) {
            getSuggest(actions, 'time_of_fall', 'время зака');
        })
        .capture('time', function (actions) {
            getSuggest(actions, 'time', 'время');
        })
        .capture('time_difference', function (actions) {
            getSuggest(actions, 'time_difference', 'разница во времени москва париж');
        })
        .capture('distance', function (actions) {
            getSuggest(actions, 'distance', 'расстояние от мос');
        })
        .capture('holiday', function (actions) {
            getSuggest(actions, 'holiday', 'како');
        })
        .capture('date', function (actions) {
            getSuggest(actions, 'date', 'какое');
        })
        .capture('moon', function (actions) {
            getSuggest(actions, 'moon', 'фаза');
        })
        .capture('stock', function (actions) {
            getSuggest(actions, 'stock', 'ку');
        })
        .capture('calc', function (actions) {
            getSuggest(actions, 'calc', '666 плюс 666');
        })
        .capture('trans', function (actions) {
            getSuggest(actions, 'trans', 'april пер');
        })
        .capture('planet', function (actions) {
            getSuggest(actions, 'planet', 'погода на сат');
        })
        .capture('day_to', function (actions) {
            getSuggest(actions, 'day_to', 'сколько дней до');
        });
};


var suites = [
    new Suite('header', [mocks.default, mocks.logIn, mocks.logInLongCity, mocks.kylorenDefault, mocks.kylorenLogIn, mocks.kylorenLogInLongCity], headerChecks),
    new Suite('domik_unauth', [mocks.logIn], domikChecks),
    new Suite('domik_auth', [mocks.complexity], domikInputChecks),
    new Suite('slide_menu', [mocks.complexity], menuChecks),
    new Suite('stale_popup', [mocks.complexity], stalePagePopupChecks),
    new Suite('wong_date_popup', [mocks.wrongDate], wrongDatePopupChecks),
    new Suite('geo_popup_failed', [mocks.default], geoPopupChecks),
    new Suite('footer', [mocks.default, mocks.kylorenDefault], footerChecks),
    new Suite('skin_greeting_popup', [mocks.kylorenDefault], skinPopupChecks),
    new Suite('applications', [mocks.default, mocks.kylorenDefault], applicationsChecks),
    new Suite('services', [mocks.services, mocks.kylorenServices], servicesChecks),
    new Suite('news', [mocks.news, mocks.kylorenNews, mocks.specialNew, mocks.kylorenSpecialNew], newsChecks),
    new Suite('bridges_collapsed', [mocks.bridges, mocks.kylorenBridges], bridgesCollapsedChecks),
    new Suite('bridges_expanded', [mocks.bridges, mocks.kylorenBridges], bridgesExpandedChecks),
    new Suite('timeshift', [mocks.timeshift, mocks.kylorenTimeshift], timeshiftChecks),
    new Suite('type_suggest', [mocks.default], typeSuggestChecks)
];


gemini.suite('touch yandex.ru', function () {
    suites.forEach(function (suite) {
        suite.run();
    });
});