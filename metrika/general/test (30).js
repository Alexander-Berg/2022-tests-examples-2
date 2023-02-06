console.log('TEST_START');

var assert = require('assert');

var uatraits;
var Detector;
var detector;

var userAgentDefault = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36 OPR/42.0.2393.85';
//'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebK it/537.36 (KHTML, like Gecko) Chrome/40.0.2214.45 YaBrowser/15.2.2214.2613 (beta) Safari/537.36';
var browserPath = '../data/browser.xml';
var profilesPath = '../data/profiles.xml';
var extraPath = '../data/extra.xml';


describe('uatraits node bindings:', function () {
	assert.doesNotThrow(function () {
		uatraits = require('./');
		Detector = uatraits.Detector;
	});

	function test(userAgentString) {
		var uaInfo;

		assert.doesNotThrow(function() {
			uaInfo = detector.detect(userAgentString);
		});
		assert(typeof uaInfo == 'object');
		assert(typeof uaInfo.isBrowser !== 'undefined');

		return uaInfo;
	}

	it('one argument constructor', function () {
		detector = new Detector(browserPath);
		test(userAgentDefault);
	});

	it('two arguments constructor', function () {
		detector = new Detector(browserPath, profilesPath);
		test(userAgentDefault);
	});

	it('three arguments constructor', function () {
		detector = new Detector(browserPath, profilesPath, extraPath);
		uaInfo = test(userAgentDefault);
		
		assert(typeof uaInfo.CSP1Support !== 'undefined');
	});
});

console.log('TEST_END');


// one day one guy will use good test framework. Until then...
function describe(description, func) {
    func();
}

function it(description, test){
	try {
		test();
	} catch (err) {
		console.error('failed: ' +  description);
		throw err;
	}
}

