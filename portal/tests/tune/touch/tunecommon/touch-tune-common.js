/* globals gemini */
var Suite = require('../../../suite');
var mocks = require('../../../mocks').touch.tune;


var BodyChecks = function (suite) {
	suite
		.setCaptureElements('body')
		.capture('plain')
		.capture('changed_content', function (actions) {
			actions
				.click('.checkbox_checked_yes')
				.click('.checkbox_checked_yes')
				.click('.checkbox_checked_yes');
		});
};


var suites = [
	new Suite('body', [mocks.default], BodyChecks, {path: 'tune/common'})
];

gemini.suite('touch tune common', function () {
	suites.forEach(function (suite) {
		suite.run();
	});
});