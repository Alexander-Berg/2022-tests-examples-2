/* globals gemini*/
var Suite = require('../../../suite');
var mocks = require('../../../mocks').desktop.tune;


var headerChecks = function (suite) {
	suite
		.setCaptureElements('.tune-header')
		.capture('plain')
		.capture('with_hover', function (actions) {
			actions
				.mouseMove('.tabs-menu__tab');
		});
};


var footerChecks = function (suite) {
	suite
		.setCaptureElements('.tune-footer')
		.capture('plain');
};


var contentChecks = function (suite) {
	suite
		.setCaptureElements('.page-views')
		.capture('plain');
};


var content2Checks = function (suite) {
	suite
		.before(function (actions) {
			actions
				.click('.checkbox_checked_yes')
				.click('.checkbox_checked_yes')
				.click('.checkbox_checked_yes')
				.click('.adv-options__hint');
		})
		.setCaptureElements('.page-views')
		.capture('plain', function (actions) {
			actions
				.wait(2000);
		});
};


var suites = [
	new Suite('header', [mocks.default], headerChecks, {path: 'tune/adv'}),
	new Suite('content', [mocks.default], contentChecks, {path: 'tune/adv'}),
	new Suite('changed content', [mocks.default], content2Checks, {path: 'tune/adv'}),
	new Suite('footer', [mocks.default], footerChecks, {path: 'tune/adv'})
];

gemini.suite('desktop tune adv', function () {
	suites.forEach(function (suite) {
		suite.run();
	});
});