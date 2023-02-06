const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('isEu', function () {
    const baseUrl = 'test/isEu/isEu.hbs';

    beforeEach(function () {
        return this.browser
            .deleteCookie()
            .timeoutsAsyncScript(10000)
            .url(baseUrl)
            .executeAsync(function (done) {
                localStorage.clear();
                done();
            });
    });

    it('counter should correctly initialize with broken params', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        try {
                            const fakeHitBrokenParams = {};

                            localStorage.setItem(
                                '_ym_wasSynced',
                                JSON.stringify(fakeHitBrokenParams),
                            );
                        } catch (_) {
                            // empty
                        }

                        serverHelpers.collectRequests(
                            400,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );

                        new Ya.Metrika2({
                            id: 123456,
                        });
                    },
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const parsedRequests = requests.map(e2eUtils.getRequestParams);

                const requestsCount = parsedRequests.length;

                chai.expect(
                    requestsCount,
                    'должны быть запросы от счётчика',
                ).to.greaterThan(0);

                parsedRequests.forEach(({ params }) => {
                    // защита от jserrs
                    chai.expect(
                        params,
                        'запрос должен быть хитом',
                    ).to.have.property('wmode');
                });
            });
    });

    it('counter should send eu flag in browserInfo from ls', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        try {
                            const fakeHitParams = {
                                time: 1587728899390,
                                params: {
                                    eu: 1,
                                },
                                bkParams: {},
                            };

                            localStorage.setItem(
                                '_ym_wasSynced',
                                JSON.stringify(fakeHitParams),
                            );
                        } catch (_) {
                            // empty
                        }

                        serverHelpers.collectRequests(
                            400,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );

                        new Ya.Metrika2({
                            id: 123456,
                        });
                    },
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const parsedRequests = requests.map(e2eUtils.getRequestParams);

                const requestsCount = parsedRequests.length;

                chai.expect(
                    requestsCount,
                    'должны быть запросы от счётчика',
                ).to.greaterThan(0);

                parsedRequests.forEach(({ brInfo }) => {
                    chai.expect(
                        brInfo.eu,
                        'в запросах должен быть eu',
                    ).to.be.equal('1');
                });
            });
    });
});
