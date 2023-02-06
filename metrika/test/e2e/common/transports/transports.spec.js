const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Transports e2e test', function () {
    const url = `${e2eUtils.baseUrl}/test/transports/transports.hbs`;
    const counterId = 26302566;

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000).deleteCookie();
    });

    it('Should iterate transports without triggering retransmit', function () {
        return this.browser
            .url(url)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        localStorage.clear();
                        window.localStorage.setItem(
                            '_ym_synced',
                            '{"SYNCED_ADM":9999999999}',
                        );
                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                count: 1,
                                status: '500',
                            },
                            function () {
                                const requests = [];
                                serverHelpers.onRequest(function (request) {
                                    requests.push(request);
                                }, options.regexp.defaultRequestRegEx);
                                setTimeout(function () {
                                    done({
                                        requests,
                                        retransmitFired:
                                            localStorage.getItem(
                                                '_ym_retryReqs',
                                            ),
                                    });
                                }, 1000);

                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                            },
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: { requests, retransmitFired } }) => {
                const transportIndexes = [];
                requests.forEach(function (request) {
                    const { telemetry } = e2eUtils.getRequestParams(request);
                    transportIndexes.push(telemetry.ti);
                });
                chai.expect(
                    transportIndexes.sort((a, b) => a - b),
                ).to.deep.equal(['1', '2']);
                chai.expect(JSON.parse(retransmitFired)).to.be.deep.equal({});
            });
    });
});
