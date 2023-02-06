/* globals gemini*/
var Suite = require('../../../suite');
var mocks = require('../../../mocks').touch.tune;


var BodyChecks = function (suite) {
	suite
		.setCaptureElements('body')
		.capture('plain');
};


var suites = [
	new Suite('body', [mocks.default], BodyChecks, {path: 'tune'})
];

gemini.suite('touch tune main', function () {
	suites.forEach(function (suite) {
		suite.run();
	});
});