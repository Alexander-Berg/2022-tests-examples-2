const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('turbo page test', () => {
    const url = `${e2eUtils.baseUrl}/test/turboPage/turboPage.hbs`;
    const testCounterId = 26302566;

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000).url(url);
    });

    it('Correctly identifies turbo page if turbo_page_id and turbo_page is set in options', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.onRequest(function (request) {
                            done(request);
                        }, options.regexp.defaultRequestRegEx);

                        new Ya.Metrika2({
                            id: options.testCounterId,
                            params: {
                                __ym: {
                                    turbo_page: true,
                                    turbo_page_id: 100,
                                },
                            },
                        });
                    },
                    testCounterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then((result) => {
                const request = result.value;
                const { counterId, brInfo, siteInfo } =
                    e2eUtils.getRequestParams(request);

                const { turbo_page, turbo_page_id } = siteInfo.__ym;
                chai.expect(counterId).to.equal(testCounterId.toString());
                chai.expect(turbo_page).to.be.true;
                chai.expect(turbo_page_id).to.be.equal(100);
                chai.expect(brInfo.tp).to.equal('1');
                chai.expect(brInfo.tpid).to.equal('100');
            });
    });

    it('Correctly identifies turbo page if tpid and tp is set in params', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            500,
                            0,
                            options.regexp.defaultRequestRegEx,
                        );

                        const counter = new Ya.Metrika2({
                            id: options.testCounterId,
                        });
                        counter.params({
                            __ym: {
                                turbo_page: true,
                                turbo_page_id: 100,
                            },
                        });
                        counter.hit('http://example.com');
                    },
                    testCounterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then((result) => {
                const requests = result.value;
                let markedTpRequests = 0;

                requests.forEach((request) => {
                    const { brInfo } = e2eUtils.getRequestParams(request);
                    if (brInfo.tp === '1' && brInfo.tpid === '100') {
                        markedTpRequests += 1;
                    }
                });
                chai.expect(markedTpRequests).above(1);
            });
    });
});
