/* globals gemini */
var Suite = require('../../../suite');
var mocks = require('../../../mocks').desktop.gramps;
var usefull = require('../../../usefull');



var footerChecks = function (suite) {
    suite
        .setCaptureElements('.rows__row_last')
        .capture('plain');
};


var midLineChecks = function (suite) {
    suite
        .setCaptureElements('.container__search')
        .capture('plain');
};


var headerOptionsChecks = function (suite) {
    suite
        .before(function (actions) {
            actions
                .click('.head-options2')
                .wait(1000);
        })
        .setCaptureElements('.popup_domik_trigger')
        .capture('plain');
};


var headerChecks = function (suite) {
    suite
        .setCaptureElements('.rows__row_first')
        .capture('plain');
};


var domikChecks = function (suite) {
    suite
        .setCaptureElements('.domik2__mail-promo', '.domik2__dropdown', '.domik2__link')
        .capture('plain')
        .capture('hover_dropdown', function (actions) {
            actions
                .mouseMove('.domik2__dropdown-toggler')
                .wait(1000);
        })
        .capture('social_opened', function (actions) {
            actions
                .click('.domik2__social-more')
                .wait(1000);
        })
        .capture('not_my_pc', function (actions) {
            actions
                .click('.checkbox_size_xxs')
                .wait(1000);
        })
        .capture('hidden', function (actions) {
            actions
                .click('.domik2__dropdown-toggler')
                .wait(1000);
        });
};


var loginDomikChecks = function (suite) {
    suite
        .setCaptureElements('.domik2__dropdown', '.usermenu ', '.user_exp_yes')
        .capture('plain')

        .capture('hidden', function (actions) {
            actions
                .click('.domik2__dropdown-toggler')
                .wait(1000);
        })
        .capture('user_menu', function (actions) {
            actions
                .click('.domik2__dropdown-user-icon')
                .wait(1000);
        });
};


var vkChecks = function (suite) {
    suite
        .before(usefull.stopScroll)
        .setCaptureElements('.b-keyboard')
        .capture('opened', function (actions) {
            actions
                .click('.keyboard-loader')
                .wait(300)
                .mouseMove('.b-keyboard__row');

        })
        .capture('languages_popup', function (actions) {
            actions
                .click('.b-keyboard__switcher')
                .wait(300)
                .mouseMove('.b-keyboard__row');

        })
        .after(function (actions) {
            actions
                .click('.b-keyboard-popup__close')
                .wait(300)
                .mouseMove('.b-keyboard__row');
        });
};


var suites = [
    new Suite('footer', [mocks.default], footerChecks, {getParam: 'gramps=1'}),
    new Suite('middle_line', [mocks.exampleGramps], midLineChecks, {getParam: 'gramps=1'}),
    new Suite('options', [mocks.teaserNoneGramps], headerOptionsChecks, {getParam: 'gramps=1'}),
    new Suite('header', [mocks.default], headerChecks, {getParam: 'gramps=1'}),
    new Suite('domik', [mocks.default], domikChecks, {getParam: 'gramps=1'}),
    new Suite('logged_domik', [mocks.logInGramps], loginDomikChecks, {getParam: 'gramps=1'}),
    new Suite('logged_domik', [mocks.default], vkChecks, {getParam: 'gramps=1'})
];


gemini.suite('desktop yandex.ru gramps', function () {
    suites.forEach(function (suite) {
        suite.run();
    });
});
