const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Track hash test', function () {
    const baseUrl = 'test/trackHash/trackHash.hbs';
    const counterId = 1;
    const WH_BR_KEY = 'wh';

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000).deleteCookie();
    });

    it('should send request when counter is initialized and then change urls hash', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        new Ya.Metrika2({
                            id: options.counterId,
                            trackHash: true,
                        });

                        window.location.hash = 'test';

                        serverHelpers.collectRequests(
                            200,
                            done,
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const request = requests[1];
                const { brInfo } = e2eUtils.getRequestParams(request);

                chai.expect(brInfo[WH_BR_KEY]).to.be.equal('1');
            });
    });
    it('should send request after called method trackHash and then change urls hash', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        counter.trackHash(true);

                        window.location.hash = 'test';

                        serverHelpers.collectRequests(
                            200,
                            done,
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const request = requests[1];
                const { brInfo } = e2eUtils.getRequestParams(request);

                chai.expect(brInfo[WH_BR_KEY]).to.be.equal('1');
            });
    });
    it(`shouldn't send request after unsubscribe from trackHash and then change urls hash`, function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                            trackHash: true,
                        });

                        counter.trackHash(false);
                        window.location.hash = 'test2';

                        serverHelpers.collectRequests(
                            200,
                            done,
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                chai.expect(requests.length).to.be.equal(1);
            });
    });
});
