const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Callbacks e2e test', function () {
    const baseUrl = 'test/callbacks/callbacks.hbs';
    const testCallback = 'TEST_CALLBACK';

    beforeEach(function () {
        return this.browser.deleteCookie().timeoutsAsyncScript(10000);
    });

    it('should call callback2 with Metrika2', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(onRequest, options, done) {
                        window.yandex_metrika_callback2 = function () {
                            done(options.testCallback);
                        };

                        // eslint-disable-next-line no-undef
                        initCounterLocalJs();
                    },
                    testCallback,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value }) => {
                chai.expect(value).to.be.equal(testCallback);
            });
    });

    it('should call callbacks2 with Metrika2', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(onRequest, options, done) {
                        let count = 0;
                        function cb() {
                            count += 1;
                            if (count === 2) {
                                done(options.testCallback);
                            }
                        }

                        window.yandex_metrika_callbacks2 = [
                            function () {},
                            function () {
                                cb();
                            },
                            function () {
                                cb();
                            },
                        ];

                        // eslint-disable-next-line no-undef
                        initCounterLocalJs();
                    },
                    testCallback,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value }) => {
                chai.expect(value).to.be.equal(testCallback);
            });
    });
});
