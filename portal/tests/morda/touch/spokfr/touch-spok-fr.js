/* globals gemini */
var Suite = require('../../../suite');
var mocks = require('../../../mocks').touch.spok;
var usefull = require('../../../usefull');


var footerChecks = function (suite) {
	suite
		.setCaptureElements('.content__footer')
		.capture('plain', usefull.stopScroll);
};


var newsChecks = function (suite) {
	suite
		.setCaptureElements('.news')
		.capture('plain', usefull.stopScroll);
};


var headerChecks = function (suite) {
	suite
		.setCaptureElements('.content__head')
		.capture('plain', usefull.stopScroll);
};


var informersChecks = function (suite) {
	suite
		.setCaptureElements('.content__informers')
		.capture('plain', usefull.stopScroll);
};


var mainRowChecks = function (suite) {
	suite
		.setCaptureElements('.mlogo__container', '.search')
		.capture('plain', usefull.stopScroll);
};


var arrowChecks = function (suite) {
	suite
		.setCaptureElements('.search')
		.capture('focused', function (actions) {
			actions
				.click('.mini-suggest__button-cell')
				.wait(1000);
			usefull.stopScroll(actions);
		});
};


var suites = [
	new Suite('footer', [mocks.langUa, mocks.langRu, mocks.langEn], footerChecks),
	new Suite('header', [mocks.authEn, mocks.authRu, mocks.authUa, mocks.authLongEn, mocks.authLongRu, mocks.authLongUa], headerChecks),
	new Suite('informers', [mocks.weather], informersChecks),
	new Suite('main_row', [mocks.langUa, mocks.langRu, mocks.langEn], mainRowChecks),
	new Suite('arrow', [mocks.langUa, mocks.langRu, mocks.langEn], arrowChecks),
	new Suite('news', [mocks.news], newsChecks)
];


gemini.suite('touch yandex.fr', function () {
	suites.forEach(function (suite) {
		suite.run();
	});
});
