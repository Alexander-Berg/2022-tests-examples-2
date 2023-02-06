const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('InternetServiceProvider itp e2e test', function () {
    const baseUrl =
        'https://yandex.ru/test/internetServiceProvider/internetServiceProvider.hbs';
    const counterId = 26302566;
    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000).deleteCookie();
    });
    it('change request host and browser info for rostelecom', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            {
                                regex: `wmode=7`,
                                count: 1,
                                body: {
                                    settings: {
                                        rt: 1,
                                    },
                                },
                            },
                            () => {
                                serverHelpers.collectRequests(3000, null);
                                new Ya.Metrika2({ id: options.counterId });
                            },
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const [rtRequest] = requests
                    .map(e2eUtils.getRequestParams)
                    .filter(({ brInfo }) => brInfo.rt);
                chai.expect(rtRequest.headers['x-host']).to.be.eq(
                    '2724587256.mc.yandex.ru',
                );
            });
    });
    it('change browser info for megafon', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            {
                                regex: `wmode=7`,
                                count: 1,
                                body: {
                                    settings: {
                                        mf: 1,
                                    },
                                },
                            },
                            () => {
                                serverHelpers.collectRequests(2000, null);
                                new Ya.Metrika2({ id: options.counterId });
                            },
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const hasMfRequests = requests.some(({ headers }) =>
                    headers['x-host'].includes('adstat.yandex.ru'),
                );
                chai.expect(hasMfRequests).to.be.true;
            });
    });
    it('no call external stat api with providers', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            {
                                regex: `wmode=7`,
                                count: 1,
                                body: {
                                    settings: {},
                                },
                            },
                            () => {
                                serverHelpers.collectRequests(1000, null);
                                new Ya.Metrika2({ id: options.counterId });
                            },
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const paramsRequests = requests.map(e2eUtils.getRequestParams);
                const rtRequests = paramsRequests.filter(
                    ({ brInfo }) => brInfo.rt,
                );
                const mfRequests = paramsRequests.filter(
                    ({ brInfo }) => brInfo.mf,
                );
                chai.expect(rtRequests).to.be.lengthOf(0);
                chai.expect(mfRequests).to.be.lengthOf(0);
            });
    });
});
