const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('deviceSync / AppMetricaInitializer', function () {
    const baseUrl = 'https://yandex.ru/test/deviceSync/appMetricaInit.hbs';

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000);
    });

    it('should call init / interface load before counter', function () {
        const counterId = 26302566;
        const data = {
            a: 1,
            b: 2,
        };
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/${options.counterId}`,
                                    count: 1,
                                    body: {
                                        settings: {
                                            sbp: options.data,
                                        },
                                    },
                                },
                            ],
                            function () {
                                window.AppMetricaInitializer = {};
                                window.AppMetricaInitializer.init = done;

                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                            },
                        );
                    },
                    counterId,
                    data,
                }),
            )
            .then(({ value }) => {
                chai.expect(value).to.deep.eq(
                    JSON.stringify({ ...data, c: counterId }),
                );
            });
    });

    it('should call init / interface load after counter', function () {
        const counterId = 26302566;
        const data = {
            a: 1,
            b: 2,
        };
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/${options.counterId}`,
                                    count: 1,
                                    body: {
                                        settings: {
                                            sbp: options.data,
                                        },
                                    },
                                },
                            ],
                            function () {
                                new Ya.Metrika2({
                                    id: options.counterId,
                                });

                                setTimeout(() => {
                                    window.AppMetricaInitializer = {};
                                    window.AppMetricaInitializer.init = done;
                                }, 2000);
                            },
                        );
                    },
                    counterId,
                    data,
                }),
            )
            .then(({ value }) => {
                chai.expect(value).to.deep.eq(
                    JSON.stringify({ ...data, c: counterId }),
                );
            });
    });
});
