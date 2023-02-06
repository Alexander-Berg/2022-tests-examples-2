/* globals gemini*/
var Suite = require('../../../suite');
var mocks = require('../../../mocks').desktop.tune;


var headerChecks = function (suite) {
	suite
		.setCaptureElements('.tune-header')
		.capture('plain');
};


var footerChecks = function (suite) {
	suite
		.setCaptureElements('.tune-footer')
		.capture('plain');
};


var langSwitcherChecks = function (suite) {
	suite
		.before(function (actions, find) {
			this.input = find('.input__input');
			actions
				.click('.button_arrow_down');
		})
		.setCaptureElements('.popup_autoclosable_yes')
		.capture('plain');
};


var activeSaveButtonChecks = function (suite) {
	suite
		.before(function (actions) {
			actions
				.click('.button_arrow_down')
				.click('.select__item:last-child')
				.wait(1000);
		})
		.setCaptureElements('.form__save')
		.capture('plain');
};


var contentChecks = function (suite) {
	suite
		.setCaptureElements('.page-views')
		.capture('plain');
};


var suites = [
	new Suite('header', [mocks.default], headerChecks, {path: 'tune/lang'}),
	new Suite('content', [mocks.default], contentChecks, {path: 'tune/lang'}),
	new Suite('footer', [mocks.default], footerChecks, {path: 'tune/lang'}),
	new Suite('langSwitcher', [mocks.default], langSwitcherChecks, {path: 'tune/lang'}),
	new Suite('activeSaveButton', [mocks.default], activeSaveButtonChecks, {path: 'tune/lang'})
];

gemini.suite('desktop tune lang', function () {
	suites.forEach(function (suite) {
		suite.run();
	});
});