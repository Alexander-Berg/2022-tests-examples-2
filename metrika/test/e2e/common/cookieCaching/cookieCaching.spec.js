const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Cookie caching', function () {
    const baseUrl = 'test/cookieCaching/cookieCaching.hbs';
    const firstCounterId = 26302566;
    const secondCounterId = 24226447;
    const extractUid = (request) => {
        const {
            brInfo: { u },
        } = e2eUtils.getRequestParams(request);

        return u;
    };

    beforeEach(function () {
        return this.browser.deleteCookie().timeoutsAsyncScript(10000);
    });

    it('Should set one uid for two instances of a counter', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const requests = {};
                        serverHelpers.onRequest(function (request) {
                            // eslint-disable-next-line no-unused-vars
                            const [_, id] = new RegExp(
                                '\\/watch\\/(\\d+)',
                            ).exec(request.url);
                            requests[id] = request;
                            if (
                                requests[options.firstCounterId] &&
                                requests[options.secondCounterId]
                            ) {
                                done(requests);
                            }
                        });
                        new Ya.Metrika2({
                            id: options.firstCounterId,
                        });
                        new Ya.MetrikaDebug({
                            id: options.secondCounterId,
                        });
                    },
                    firstCounterId,
                    secondCounterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const firstRequest = requests[firstCounterId];
                const secondRequest = requests[secondCounterId];

                chai.expect(extractUid(firstRequest)).to.equal(
                    extractUid(secondRequest),
                );
            });
    });
});
