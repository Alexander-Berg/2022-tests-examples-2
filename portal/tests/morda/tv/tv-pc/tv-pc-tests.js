/* globals gemini */

var Suite = require('../../../suite');
var mocks = require('../../../mocks').tv;
var usefull = require('../../../usefull');

var footerChecks = function (suite) {
    suite
        .before(usefull.setTvBackgroundColor)
        .setCaptureElements('.foot__item', '.foot__item:nth-child(2)')
        .capture('plain');
};


var headerChecks = function (suite) {
    suite
        .before(usefull.setTvBackgroundColor)
        .setCaptureElements('.header')
        .capture('plain');
};


var ServicesChecks = function (suite) {
    suite
        .before(usefull.setTvBackgroundColor)
        .setCaptureElements('.services2')
        .capture('plain');
};


var videoRubricsChecks = function (suite) {
    suite
        .before(usefull.setTvBackgroundColor)
        .setCaptureElements('.video2__nav')
        .capture('plain', function (actions) {
            actions.mouseMove('.search-arrow__button');
        })
        .capture('hovered', function (actions) {
            actions.mouseMove('.button_theme_tvnav');
        });
};


var videoTopChecks = function (suite) {
    suite
        .before(usefull.setTvBackgroundColor)
        .setCaptureElements('.video2__board ')
        .capture('plain', function (actions) {
            actions.mouseMove('.search-arrow__button');
        })
        .capture('hovered', function (actions) {
            actions.mouseMove('.video2__td');
        });
};


var tvBlockChecks = function (suite) {
    suite
        .before(usefull.setTvBackgroundColor)
        .setCaptureElements('.tv__header', '.tv__items')
        .capture('plain')
        .capture('hovered', function (actions) {
            actions.mouseMove('.tv__item');
        });
};


var newsBlockTopChecks = function (suite) {
    suite
        .before(usefull.setTvBackgroundColor)
        .setCaptureElements('.news__headers', '.news__pane')
        .capture('plain')
        .capture('hovered', function (actions) {
            actions.mouseMove('.news__item');
        });
};


var arrowChecks = function (suite) {
    suite
        .ignoreElements({every: '.suggest2-item'})
        .before(usefull.setTvBackgroundColor)
        .setCaptureElements('.main__row_arrow', '.tv-logo')
        .capture('plain')
        .capture('with_suggest', function (actions) {
            actions
                .sendKeys('.input__input', 'fb')
                .wait(500);
        })
};


var suites = [
    new Suite('footer', [mocks.default], footerChecks, {getParam: 'content=tv'}),
    new Suite('header', [mocks.informers], headerChecks, {getParam: 'content=tv'}),
    new Suite('video_rubrics', [mocks.video], videoRubricsChecks, {getParam: 'content=tv'}),
    new Suite('video_top', [mocks.video], videoTopChecks, {getParam: 'content=tv'}),
    new Suite('services', [mocks.default], ServicesChecks, {getParam: 'content=tv'}),
    new Suite('topnews', [mocks.topNews], newsBlockTopChecks, {getParam: 'content=tv'}),
    new Suite('tv', [mocks.tv], tvBlockChecks, {getParam: 'content=tv'}),
    new Suite('logo+arrow', [mocks.default], arrowChecks, {getParam: 'content=tv'})
];


gemini.suite('tv yandex.ru_pc', function () {
    suites.forEach(function (suite) {
        suite.run();
    });
});
