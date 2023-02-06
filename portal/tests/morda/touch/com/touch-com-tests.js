/* globals gemini */

var Suite = require('../../../suite');
var mocks = require('../../../mocks').touch.com;


var footerChecks = function (suite) {
	suite
		.setCaptureElements('.mfooter')
		.capture('plain');
};


var logoChecks = function (suite) {
	suite
		.setCaptureElements('.mlogo')
		.capture('plain');
};


var searchInputChecks = function (suite) {
	suite
		.setCaptureElements('.mini-suggest')
		.capture('plain')
		.capture('with_text', function (actions) {
			actions
				.click('.mini-suggest__input')
				.wait(1000)
				.sendKeys('.mini-suggest__input', 'fb')
				.wait(1000);
		});
};


var searchTabsChecks = function (suite) {
	suite
		.setCaptureElements('.informers')
		.capture('plain');
};


var headerChecks = function (suite) {
	suite
		.setCaptureElements('.content__head', '.langswitch__popup')
		.capture('plain')
		.capture('language_popup', function (actions, find) {
			actions
				.click(find('.langswitch'))
				.wait(1000);
		});
};


var suites = [
	new Suite('footer', [mocks.en, mocks.id], footerChecks, {getParam: 'redirect=0'}),
	new Suite('search_input', [mocks.en, mocks.id], searchInputChecks, {getParam: 'redirect=0'}),
	new Suite('search_tabs', [mocks.en, mocks.id, mocks.auth_en], searchTabsChecks, {getParam: 'redirect=0'}),
	new Suite('header', [mocks.en, mocks.id, mocks.auth_en, mocks.auth_id, mocks.auth_long], headerChecks, {getParam: 'redirect=0'}),
	new Suite('main_logo', [mocks.default], logoChecks, {getParam: 'redirect=0'})
];


gemini.suite('touch yandex.com', function () {
	suites.forEach(function (suite) {
		suite.run();
	});
});
