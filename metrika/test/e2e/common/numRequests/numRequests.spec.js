const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('numRequests', () => {
    const url = `${e2eUtils.baseUrl}/test/numRequests/numRequests.hbs`;
    const counterId1 = 123;
    const counterId2 = 555;

    const allCounters = [
        { id: counterId1, type: 0 },
        { id: counterId2, type: 0 },
        { id: counterId1, type: 1 },
        { id: counterId2, type: 1 },
    ];

    /**
     * An array of tuples, one entry per page load.
     * tuple[0] - counters to be initialized on a page.
     * tuple[1] - expected cumulative number of requests sent in brInfo.rqn for each counter.
     */
    const testData = [
        [allCounters, 1],
        [allCounters.slice(2), 2],
        [allCounters.slice(0, 2), 2],
        [allCounters, 3],
    ];

    const pageLoad = (browser, counters, expectedNumRequests) =>
        browser
            .url(url)
            .then(
                e2eUtils.provideServerHelpers(browser, {
                    cb(serverHelpers, options, done) {
                        options.counters.forEach(function (counter) {
                            new Ya.Metrika2({
                                id: counter.id,
                                type: counter.type,
                            });
                        });

                        const requests = [];
                        serverHelpers.onRequest(function (request) {
                            requests.push(request);

                            if (requests.length === options.counters.length) {
                                done(requests);
                            }
                        }, options.regexp.defaultRequestRegEx);
                    },
                    counters,
                }),
            )
            .then(e2eUtils.handleRequest(browser))
            .then(({ value: requests }) => {
                const parsedRequest = requests.map(e2eUtils.getRequestParams);
                chai.expect(parsedRequest).to.be.lengthOf(counters.length);

                parsedRequest.forEach(({ brInfo, counterId, params }) => {
                    const counterType = parseInt(params['cnt-class'], 10) || 0;
                    const counter = counters.find(
                        ({ id, type }) =>
                            id === parseInt(counterId, 10) &&
                            type === counterType,
                    );
                    const numRequests = parseInt(brInfo.rqn, 10);
                    chai.expect(counter).to.be.ok;
                    chai.expect(numRequests).to.be.eq(expectedNumRequests);
                });
            });

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000);
    });

    it('Sends request index number in brInfo.rqn separately for each counterKey (counterId + counterType)', function () {
        return testData.reduce(
            (browser, [counters, expectedNumRequests]) =>
                pageLoad(browser, counters, expectedNumRequests),
            this.browser,
        );
    });
});
