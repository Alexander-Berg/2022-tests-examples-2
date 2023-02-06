/* globals gemini */
var Suite = require('../../../suite');
var mocks = require('../../../mocks').touch.tune;
var usefull = require('../../../usefull');


var BodyChecks = function (suite) {
	suite
		.setCaptureElements('body')
		.capture('plain', function (actions) {
			actions.wait(2000);
			usefull.mapPaint(actions);
		})
		.capture('changed_content', function (actions) {
			actions
				.click('.checkbox')
				.wait(2000);
		})
		.capture('geo_detect', function (actions) {
			actions
				.click('.geo-map__promo-content')
				.wait(2000);
		})
		.capture('input', function (actions) {
			actions
				.sendKeys('.input__control', 'Му')
				.wait(2000);
		})
		.capture('city_selected', function (actions) {
			actions
				.click('.b-autocomplete-item_type_geo')
				.wait(2000);
			usefull.mapPaint(actions);
		});
};


var suites = [
	new Suite('body', [mocks.default], BodyChecks, {path: 'tune/geo'})
];

gemini.suite('touch tune geo', function () {
	suites.forEach(function (suite) {
		suite.run();
	});
});