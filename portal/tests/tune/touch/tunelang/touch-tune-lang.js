/* globals gemini*/
var Suite = require('../../../suite');
var mocks = require('../../../mocks').touch.tune;


var BodyChecks = function (suite) {
	suite
		.setCaptureElements('body')
		.capture('plain')
		.capture('changed_content', function (actions) {
			actions
				.click('.list__item:last-child');
		});
};


var suites = [
	new Suite('body', [mocks.default], BodyChecks, {path: 'tune/lang'})
];

gemini.suite('touch tune lang', function () {
	suites.forEach(function (suite) {
		suite.run();
	});
});