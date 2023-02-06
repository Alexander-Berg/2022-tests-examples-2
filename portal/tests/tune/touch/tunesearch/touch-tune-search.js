/* globals gemini*/
var Suite = require('../../../suite');
var mocks = require('../../../mocks').touch.tune;


var BodyChecks = function (suite) {
	suite
		.setCaptureElements('body')
		.capture('plain')
		.capture('changed_content', function (actions) {
			actions
				.click('.checkbox_checked_yes')
				.wait(1000)
		})
		.capture('not_auth', function (actions) {
			actions
				.click('.checkbox')
				.wait(1000);
		});
};


var suites = [
	new Suite('body', [mocks.default], BodyChecks, {path: 'tune/search'})
];

gemini.suite('touch tune search', function () {
	suites.forEach(function (suite) {
		suite.run();
	});
});