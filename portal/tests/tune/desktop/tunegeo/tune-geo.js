/* globals gemini*/
var Suite = require('../../../suite');
var mocks = require('../../../mocks').desktop.tune;


var headerChecks = function (suite) {
	suite
		.setCaptureElements('.tune-header')
		.capture('plain');
};

var geoMapChecks = function (suite) {
	suite
		.before(function (actions, find) {
			this.input = find('.input__input');
			actions
				.executeJS(function () {
					//document.getElementsByClassName('geo-map__left')[0].style.backgroundColor = 'aqua';
					document.getElementsByClassName('geo-map__center')[0].style.backgroundColor = 'aqua';
				})
				.click('.input__input')
				.sendKeys(this.input, 'Дно')
				.sendKeys(gemini.ENTER)
				.sendKeys(gemini.ENTER);
		})
		.setCaptureElements('.geo-map__borders')
		.capture('plain', function (actions) {
			actions
				.wait(2000);
		});
};


var cityBlockChecks = function (suite) {
	suite
		.setCaptureElements('.city')
		.capture('plain');
};


var cityInputChecks = function (suite) {
	suite
		.before(function (actions, find) {
			this.input = find('.input__input');
			actions
				.click('.checkbox__control')
				.click('.input__input')
				.sendKeys(gemini.CLEAR)
				.sendKeys(this.input, 'Вла');
		})
		.setCaptureElements('.input__input', '.input__popup_type_geo')
		.capture('with_suggest', function (actions) {
			actions
				.wait(2000);
		})
		.capture('with_suggest_hover', function (actions, find) {
			actions
				.mouseMove(find('.b-autocomplete-item'))
				.wait(2000);
		});
};


var cityInputEmptyChecks = function (suite) {
	suite
		.setCaptureElements('.input__input')
		.capture('plain');
};

var checkBoxGeoChecks = function (suite) {
	suite
		.setCaptureElements('.checkbox_geo_auto')
		.capture('plain');
};


var buttonSaveChecks = function (suite) {
	suite
		.setCaptureElements('.form__save')
		.capture('plain');
};


var footerChecks = function (suite) {
	suite
		.setCaptureElements('.tune-footer')
		.capture('plain');
};


var suites = [
	new Suite('header', [mocks.default], headerChecks, {path: 'tune/geo'}),
	new Suite('geo_map', [mocks.default], geoMapChecks, {path: 'tune/geo'}),
	new Suite('city_block', [mocks.default], cityBlockChecks, {path: 'tune/geo'}),
	new Suite('city_input', [mocks.default], cityInputChecks, {path: 'tune/geo'}),
	new Suite('city_input_empty', [mocks.default], cityInputEmptyChecks, {path: 'tune/geo'}),
	new Suite('footer', [mocks.default], footerChecks, {path: 'tune/geo'}),
	new Suite('button_save', [mocks.default], buttonSaveChecks, {path: 'tune/geo'}),
	new Suite('checkbox_geo', [mocks.default], checkBoxGeoChecks, {path: 'tune/geo'})
];

gemini.suite('desktop tune geo', function () {
	suites.forEach(function (suite) {
		suite.run();
	});
});