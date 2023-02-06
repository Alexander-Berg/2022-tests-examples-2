/* globals gemini*/
var Suite = require('../../../suite');
var mocks = require('../../../mocks').desktop.tune;
var usefull = require('../../../usefull');


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


var paranjaChecks = function (suite) {
	suite
		.setCaptureElements('.places-options__noauth')
		.capture('plain', function (actions) {
			actions.wait(2000);
			usefull.mapPaint(actions);
		});
};


var suites = [
	new Suite('header', [mocks.default], headerChecks, {path: 'tune/places'}),
	new Suite('paranja', [mocks.default], paranjaChecks, {path: 'tune/places'}),
	new Suite('footer', [mocks.default], footerChecks, {path: 'tune/places'})
];

gemini.suite('desktop tune places', function () {
	suites.forEach(function (suite) {
		suite.run();
	});
});