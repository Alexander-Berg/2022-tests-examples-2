/* globals gemini */

var Suite = require('../../../suite');
var mocks = require('../../../mocks').touch.yaru;


var tabsChecks = function (suite) {
	suite
		.setCaptureElements('.mtabs__list')
		.capture('plain');
};


var searchInputChecks = function (suite) {
	suite
		.setCaptureElements('body')
		.capture('plain')
		.capture('with_text', function (actions, find) {
			actions
				.sendKeys(find('.mini-suggest__input'), 'компьютеризация')
				.wait(1000);
		});
};


var loginChecks = function (suite) {
	suite
		.setCaptureElements('.personal')
		.capture('plain');
};


var logoChecks = function (suite) {
	suite
		.setCaptureElements('.mlogo-yaru__container')
		.capture('plain');
};


var suites = [
	new Suite('logo', [mocks.default], logoChecks),
	new Suite('login', [mocks.default], loginChecks),
	new Suite('tabs', [mocks.default], tabsChecks),
	new Suite('search_input', [mocks.default], searchInputChecks)
];


gemini.suite('touch ya.ru', function () {
	suites.forEach(function (suite) {
		suite.run();
	});
});
