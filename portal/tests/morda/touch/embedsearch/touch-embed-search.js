/* globals gemini*/
var Suite = require('../../../suite');
var mocks = require('../../../mocks').touch.embed;


var emptyInputChecks = function (suite) {
	suite
		.setCaptureElements('.search-arrow')
		.capture('plain')
		.capture('with_text', function (actions) {
			actions
				.click('.input__input')
				.wait(1000)
				.sendKeys('.input__input', 'ststeal')
				.wait(1000);
		});
};


var fullInputChecks = function (suite) {
	suite
		.setCaptureElements('.search-arrow')
		.capture('plain')
		.capture('with_text', function (actions) {
			actions
				.click('.input__input')
				.wait(1000)
				.sendKeys('.input__input', 'ststeal')
				.wait(1000);
		})
		.capture('input_clear', function (actions) {
			actions
				.click('.input__clear');
		});
};


var aLotInputChecks = function (suite) {
	suite
		.setCaptureElements('.search-arrow')
		.capture('plain')
		.capture('input_clear', function (actions) {
			actions
				.click('.input__clear');
		})
		.capture('with_text', function (actions) {
			actions
				.sendKeys('.input__input', 'ststeal')
				.wait(1000);
		});
};


var InputOnPageChecks = function (suite) {
	suite
		.setCaptureElements('.yandex__embedded-search')
		.capture('plain')
		.capture('input_full', function (actions) {
			actions
				.click('.yandex__embedded-search')
				.sendKeys('fdsfdsfsdfsadasdad');
		});
};


var suites = [
	new Suite('full_input', [mocks.default], fullInputChecks, {path: 'portal/embed_search', getParam: 'text=Ststeal'}),
	new Suite('empty_input', [mocks.default], emptyInputChecks, {path: 'portal/embed_search'}),
	new Suite('overflowing_input', [mocks.default], aLotInputChecks, {
		path: 'portal/embed_search',
		getParam: 'text=StstealStstealStstealStstealStstealStsteal'
	}),
	new Suite('input_on_page', [mocks.default], InputOnPageChecks, {path: 'embeded-search-test.html'})
];


gemini.suite('touch embed_search', function () {
	suites.forEach(function (suite) {
		suite.run();
	});
});