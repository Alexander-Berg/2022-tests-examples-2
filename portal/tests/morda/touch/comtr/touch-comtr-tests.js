/* globals gemini */

var Suite = require('../../../suite');
var mocks = require('../../../mocks').touch.comTr;
var usefull = require('../../../usefull');
var data = require('../../../tests-data');


var footerChecks = function (suite) {
	suite
		.setCaptureElements('.mfooter')
		.capture('plain');
};


var logoChecks = function (suite) {
	suite
		.setCaptureElements('.mlogo')
		.capture('plain');
};


var searchInputChecks = function (suite) {
	suite
		.setCaptureElements('.mini-suggest')
		.capture('plain')
		.capture('with_text', function (actions, find) {
			actions.sendKeys(find('.mini-suggest__input'), 'fb')
				.wait(1000);
		});
};


var searchTabsChecks = function (suite) {
	suite
		.setCaptureElements('.informers')
		.capture('plain');
};


var headerChecks = function (suite) {
	suite
		.setCaptureElements('.content__head')
		.capture('plain');
};


var domikUnauthChecks = function (suite) {
	suite
		.setCaptureElements('.dialog')
		.before(function (actions, find) {
			actions.click(find('.mheader__user-login'))
				.wait(1000);
			usefull.strongParanja(actions);
		})
		.capture('plain')
		.capture('with_login_and_passwd', function (actions, find) {
			actions.sendKeys(find('input[name=\'login\']'), 'login')
				.wait(1000);
			actions.sendKeys(find('input[name=\'passwd\']'), 'passwd')
				.wait(1000);
		})
		.capture('try_login_and_fail', function (actions, find) {
			actions.click(find('.mdomik__submit'))
				.wait(1000);
		});
};


var domikAuthChecks = function (suite) {
	suite
		.setCaptureElements('.dialog')
		.before(function (actions, find) {
			actions.click(find('.username'))
				.wait(1000);
		})
		.capture('plain');
};


var typeSuggestChecks = function (suite) {
	suite
		.setCaptureElements('body')
		.capture('weather', function (actions) {
			usefull.stopScroll(actions);
			usefull.enchantRequests(actions);
			actions
				.click('.mini-suggest__input')
				.fakeRequest('wea', data.fakeResTr.weather)
				.sendKeys('wea');
		})
		.capture('fact', function (actions) {
			usefull.enchantRequests(actions);
			actions
				.click('.mini-suggest__input-clear')
				.fakeRequest('длина', data.fakeResTr.fact)
				.sendKeys('длина');
		})
		.capture('traffic', function (actions) {
			usefull.enchantRequests(actions);
			actions
				.click('.mini-suggest__input-clear')
				.fakeRequest('traf', data.fakeResTr.traffic)
				.sendKeys('traf');
		})
		.capture('navigation', function (actions) {
			usefull.enchantRequests(actions);
			actions
				.click('.mini-suggest__input-clear')
				.fakeRequest('fac', data.fakeResTr.navigation)
				.sendKeys('fac');
		})
		.capture('ramadan', function (actions) {
			usefull.enchantRequests(actions);
			actions
				.click('.mini-suggest__input-clear')
				.fakeRequest('rama', data.fakeResTr.ramadan)
				.sendKeys('rama');
		});
};


var suites = [
	new Suite('footer', [mocks.tr], footerChecks),
	new Suite('search_input', [mocks.tr], searchInputChecks),
	new Suite('search_tabs', [mocks.traffic, mocks.no_traffic, mocks.auth], searchTabsChecks),
	new Suite('header', [mocks.tr, mocks.auth, mocks.auth_long], headerChecks),
	new Suite('domik_unauth', [mocks.tr], domikUnauthChecks),
	new Suite('domik_auth', [mocks.auth, mocks.auth_long], domikAuthChecks),
	new Suite('main_logo', [mocks.default], logoChecks),
	new Suite('type_suggest', [mocks.default], typeSuggestChecks)
];


gemini.suite('touch yandex.com.tr', function () {
	suites.forEach(function (suite) {
		suite.run();
	});
});