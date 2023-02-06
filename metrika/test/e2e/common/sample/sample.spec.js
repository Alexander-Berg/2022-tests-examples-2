const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Sample e2e test', function () {
    const baseUrl = 'test/sample/sample.hbs';
    const counterId = 26302566;
    const testOptions = {
        counterId,
        baseUrl,
    };
    beforeEach(function () {
        return this.browser
            .timeoutsAsyncScript(10000)
            .url(baseUrl)
            .execute(() => {
                localStorage.clear();
            });
    });
    it('should not send http request with ls key', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        localStorage[
                            `_ym_ymoo${options.counterId}:0`
                        ] = 9999999999999;
                        new Ya.Metrika2(options.counterId);
                        serverHelpers.collectRequests(1000, null);
                    },
                    ...testOptions,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                chai.expect(requests).is.empty;
            });
    });
    it('should not send http request with counter settings', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            {
                                regex: `/watch/(${options.counterId})`,
                                count: 1,
                                body: {
                                    settings: {
                                        c_recp: 0,
                                    },
                                },
                            },
                            function () {
                                let once = false;
                                const counter = new Ya.Metrika2(
                                    options.counterId,
                                );
                                serverHelpers.collectRequests(1000, null);
                                serverHelpers.onRequest(() => {
                                    if (!once) {
                                        setTimeout(() => {
                                            counter.hit('/');
                                        }, 500);
                                        once = true;
                                    }
                                });
                            },
                        );
                    },
                    ...testOptions,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const pageViews = requests
                    .map(e2eUtils.getRequestParams)
                    .filter(({ brInfo }) => brInfo.pv === '1');
                chai.expect(pageViews).to.be.lengthOf(1);
            });
    });
});
