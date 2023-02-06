/* globals  gemini */
var Mock = require('./mock');

function Suite(name, mocks, checks, urlParam) {
	this.name = name;
	this.mocks = mocks || [];
	this.checks = checks;
	if (urlParam) {
		this.path = urlParam.path || '';
		this.getParam = urlParam.getParam || '';
	}
}

Suite.prototype.run = function () {
	var mocks = this.mocks;
	var checks = this.checks;
	var path = this.path;
	var getParam = this.getParam;
	var name = this.name;
	var fullUrl, fullName;

	mocks.forEach(function (mock) {
		fullName = [name, mock.description].join(', ');
		fullUrl = path ? ('/' + path + '?') : ('/?');
		if (getParam) {
			fullUrl = fullUrl + getParam;
		}
		if (mock.mockString) {
			fullUrl += getParam ? ('&usemock=' + mock.mockString) : ('usemock=' + mock.mockString);
		}

		Mock.prototype.start = function (suite, handler) {
			suite.setUrl(fullUrl);
			handler(suite);
		};

		gemini.suite(fullName, function (suite) {
			Mock.prototype.start(suite, checks);
		});
	});
};


module.exports = Suite;