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


var contentChecks = function (suite) {
	suite
		.setCaptureElements('.page-views')
		.capture('plain');
};


var domikChecks = function (suite) {
	suite
		.before(function (actions) {
			actions
				.click('.personal_logged_no')
				.wait(1000);

		})
		.setCaptureElements('.domik__popup ')
		.capture('plain');
};


var content2Checks = function (suite) {
	suite
		.before(function (actions) {
			actions
				.click('.checkbox_checked_yes');
		})
		.setCaptureElements('.page-views')
		.capture('plain');
};


var suites = [
	new Suite('header', [mocks.default], headerChecks, {path: 'tune/search'}),
	new Suite('content', [mocks.default], contentChecks, {path: 'tune/search'}),
	new Suite('changed content', [mocks.default], content2Checks, {path: 'tune/search'}),
	new Suite('footer', [mocks.default], footerChecks, {path: 'tune/search'}),
	new Suite('domik', [mocks.default], domikChecks, {path: 'tune/search'})
];

gemini.suite('desktop tune search', function () {
	suites.forEach(function (suite) {
		suite.run();
	});
});