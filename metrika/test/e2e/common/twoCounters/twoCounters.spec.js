const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Two Counters', function () {
    const baseUrl = 'test/twoCounters/twoCounters.hbs';
    const firstCounterId = 26302566;
    const secondCounterId = 24226447;

    beforeEach(function () {
        return this.browser.deleteCookie().timeoutsAsyncScript(10000);
    });

    it('Should track the number of counters correctly', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const requests = [];

                        new Ya.Metrika2({
                            id: options.firstCounterId,
                        });
                        new Ya.Metrika2({
                            id: options.secondCounterId,
                        });

                        serverHelpers.onRequest(function (request) {
                            requests.push(request);

                            if (requests.length === 2) {
                                done(requests);
                            }
                        });
                    },
                    firstCounterId,
                    secondCounterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const requestsDataRegistry = {};

                requests.forEach((request) => {
                    const { brInfo, counterId } =
                        e2eUtils.getRequestParams(request);

                    requestsDataRegistry[counterId] = Number(brInfo.cn);
                });

                chai.expect(requestsDataRegistry[firstCounterId]).to.equal(1);
                chai.expect(requestsDataRegistry[secondCounterId]).to.equal(2);
            });
    });
});
