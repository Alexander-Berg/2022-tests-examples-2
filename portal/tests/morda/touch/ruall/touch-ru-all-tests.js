/* globals gemini */

var Suite = require('../../../suite');
var mocks = require('../../../mocks').touch.all;
var usefull = require('../../../usefull');


var footerChecks = function (suite) {
	suite
		.setCaptureElements('.footer')
		.capture('plain', usefull.stopScroll);
};


var logoChecks = function (suite) {
	suite
		.setCaptureElements('.logo')
		.capture('plain', usefull.stopScroll);
};


var headerChecks = function (suite) {
	suite
		.setCaptureElements('.b-line__header')
		.capture('plain', usefull.stopScroll);
};


var mainServicesChecks = function (suite) {
	suite
		.setCaptureElements('.services-big__row')
		.capture('plain', usefull.stopScroll);
};


var allServicesChecks = function (suite) {
	suite
		.setCaptureElements('.b-line__services-all')
		.capture('plain', usefull.stopScroll);
};


var suites = [
	new Suite('footer', [mocks.default], footerChecks, {path: 'all'}),
	new Suite('header', [mocks.default], headerChecks, {path: 'all'}),
	new Suite('services_main', [mocks.default], mainServicesChecks, {path: 'all'}),
	new Suite('services_all', [mocks.default], allServicesChecks, {path: 'all'}),
	new Suite('main_logo', [mocks.default], logoChecks, {path: 'all'})
];


gemini.suite('touch yandex.ru/all', function () {
	suites.forEach(function (suite) {
		suite.run();
	});
});
