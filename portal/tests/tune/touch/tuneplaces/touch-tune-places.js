/* globals gemini*/
var Suite = require('../../../suite');
var mocks = require('../../../mocks').touch.tune;
var usefull = require('../../../usefull');


var BodyChecks = function (suite) {
	suite
		.setCaptureElements('body')
		.capture('plain', function (actions) {
			actions.wait(1000);
			usefull.mapPaint(actions);
		})
		.capture('not_auth', function (actions) {
			actions
				.click('.form_type_places ')
				.wait(1000);
		});
};


var suites = [
	new Suite('body', [mocks.default], BodyChecks, {path: 'tune/places'})
];

gemini.suite('touch tune places', function () {
	suites.forEach(function (suite) {
		suite.run();
	});
});