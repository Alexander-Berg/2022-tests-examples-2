const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('EcommerceParser e2e test', function () {
    const baseDir = 'test/ecommerceParser';
    const emptyPage = `${baseDir}/ecommerceParser.hbs`;
    const checkoutPage = `${baseDir}/checkout-page.hbs`;
    const checkoutMobilePage = `${baseDir}/checkout-mobile-page.hbs`;
    const basketPage = `${baseDir}/basket-page.hbs`;
    const anyPage = `${baseDir}/any-page.hbs`;
    const counterId = 26302566;

    const ym = '__ym';
    const ecommerceParserDataFlag = 'dr';
    const ecommerceParserExtendedDataFlag = 'dre';

    const randomStub = 0.23;
    const generateRandomTwoDigitNumber = '30';
    // Currency — RUB, total — 1235,23
    const encodeData = '25swzyuf47';

    // Currency — RUB, total — 999
    const newEncodeData = '25soz1p20p9';

    // Currency — RUB, total — 0
    const onlyCurrencyEncodeData = '25roz2dyl';

    // Currency — '', total — 1235,23
    const onlyTotalEncodeData = '25swzyuf47';

    // price — '12', quantity — 1, title - Сапог
    const goodsInitialEncodedData =
        'AgAAGXTrXrucq6165V1MtZ6LlnbZb/6Zb/5lv/qMcuc=';

    // price — '12', quantity — 2, title - Сапог
    const goodsAlteredEncodedData =
        'AgAAGXTrXrucq6dzlXUy1nouWdtlv/plv/mW/+oxy58=';

    // ["/basket-page", "#currencyWithTotal", "#currencyWithTotal", "/basket-mobile-page", "#currencyWithTotal", "#currencyWithTotal", "/checkout-page", "#кнопка-купить", "/checkout-mobile-page", "#checkout-mobile-btn"]
    const currencyWithTotalSelectors =
        'AgDgdTPQabw7Gw6gRfpk8wiBvrGz0v61xnw1i/TJ5hEDfWNnpf1rjPhrF+meg03h2Lj0fUMbDqBF+mTzCIG+sbPS/rXGfDWL9MnmEQN9Y2el/WuM+GsX6Z+tD282djYdQIv0yZb8flnYyy3/zLf/TLfj8s7bGW/Hu1Z6jLf/TLOxO1ry7TsEX6Z+tD282di49H1DGw6gRfpk9aHt5s7Fx6PqGNObHIA=';
    // ["/basket-page", "#total", "#currency", "/basket-mobile-page", "#total", "#currency", "/checkout-page", "#кнопка-купить", "/checkout-mobile-page", "#checkout-mobile-btn"]
    const currencyAndTotalSelectors =
        'AgC2dTPQabw7Gw6gRfpk4+GsX6ZPMIgb6xi/TPQabw7Fx6PqGNh1Ai/TJx8NYv0yeYRA31jF+mfrQ9vNnY2HUCL9MmW/H5Z2Mst/8y3/0y34/LO2xlvx7tWeoy3/0yzsTta8u07BF+mfrQ9vNnYuPR9QxsOoEX6ZPWh7ebOxcej6hjTmxyA=';
    // ["/basket-page", "#onlyTotal", "", "/basket-mobile-page", "#onlyTotal", "", "/checkout-page", "#кнопка-купить", "/checkout-mobile-page", "#checkout-mobile-btn"]
    const onlyCurrencySelectors =
        'AgCsdTPQabw7Gw6gRfpkNtbFxnw1i/SL9M9BpvDsXHo+oY2HUCL9MhtrYuM+GsX6Rfpn60PbzZ2Nh1Ai/TJlvx+WdjLLf/Mt/9Mt+PyztsZb8e7VnqMt/9Ms7E7WvLtOwRfpn60PbzZ2Lj0fUMbDqBF+mT1oe3mzsXHo+oY05scg';
    // ["/basket-page", "", "#onlyCurrency", "/basket-mobile-page", "", "#onlyCurrency", "/checkout-page", "#кнопка-купить", "/checkout-mobile-page", "#checkout-mobile-btn"]
    const onlyTotalSelectors =
        'AgCydTPQabw7Gw6gRfpF+mQ21sXeMIgb6xi/TPQabw7Fx6PqGNh1Ai/SL9MhtrYu8YRA31jF+mfrQ9vNnY2HUCL9MmW/H5Z2Mst/8y3/0y34/LO2xlvx7tWeoy3/0yzsTta8u07BF+mfrQ9vNnYuPR9QxsOoEX6ZPWh7ebOxcej6hjTmxyA=';
    // ["/basket-page", "#total", "#currency", "/basket-mobile-page", "#total", "#currency", "/checkout-page", "#кнопка-купить", "/checkout-mobile-page", "#checkout-mobile-btn", ".price", ".qty", ".title", ".price", ".qty", ".title"]
    const extendedCartSelectors =
        'AgDudTPQabw7Gw6gRfpk4+GsX6ZPMIgb6xi/TPQabw7Fx6PqGNh1Ai/TJx8NYv0yeYRA31jF+mfrQ9vNnY2HUCL9MmW/H5Z2Mst/8y3/0y34/LO2xlvx7tWeoy3/0yzsTta8u07BF+mfrQ9vNnYuPR9QxsOoEX6ZPWh7ebOxcej6hjTmxfonYn+CL9E2c6xi/RPP6oRfonYn+CL9E2c6xi/RPP6oRyA=';

    const geParserRequests = ({ value: requests }) => {
        return requests
            .map(e2eUtils.getRequestParams)
            .filter(
                ({ siteInfo }) =>
                    siteInfo &&
                    !!(siteInfo[ym] && siteInfo[ym][ecommerceParserDataFlag]),
            );
    };

    it('no send params without match template', function () {
        return this.browser
            .timeoutsAsyncScript(3000)
            .url(emptyPage)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        auto_goals: 1,
                                        dr: options.currencyWithTotalSelectors,
                                    },
                                },
                            },
                            () => {
                                serverHelpers.collectRequests(2000);
                                new Ya.Metrika2(options.counterId);
                            },
                        );
                    },
                    counterId,
                    currencyWithTotalSelectors,
                    randomStub,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(geParserRequests)
            .then((parserRequests) => {
                chai.expect(parserRequests.length).to.equal(0);
            });
    });

    it('should send params dr on checkout page', function () {
        return this.browser
            .timeoutsAsyncScript(3000)
            .url(checkoutPage)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        Math.random = () => options.randomStub;

                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        auto_goals: 1,
                                        dr: options.currencyWithTotalSelectors,
                                    },
                                },
                            },
                            () => {
                                serverHelpers.collectRequests(2000);
                                new Ya.Metrika2(options.counterId);
                            },
                        );
                    },
                    counterId,
                    currencyWithTotalSelectors,
                    randomStub,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(geParserRequests)
            .then((parserRequests) => {
                parserRequests.forEach(({ siteInfo }) => {
                    chai.expect(siteInfo[ym][ecommerceParserDataFlag]).to.equal(
                        generateRandomTwoDigitNumber,
                    );
                });
                chai.expect(parserRequests.length).to.equal(1);
            });
    });

    it('should send params dr on click checkout button on any page', function () {
        return this.browser
            .timeoutsAsyncScript(3000)
            .url(anyPage)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        Math.random = () => options.randomStub;

                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        auto_goals: 1,
                                        dr: options.currencyWithTotalSelectors,
                                    },
                                },
                            },
                            () => {
                                serverHelpers.collectRequests(2000);
                                new Ya.Metrika2(options.counterId);
                                setTimeout(() => {
                                    document
                                        .querySelector('#кнопка-купить')
                                        .click();
                                }, 300);
                            },
                        );
                    },
                    counterId,
                    currencyWithTotalSelectors,
                    randomStub,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(geParserRequests)
            .then((parserRequests) => {
                parserRequests.forEach(({ siteInfo }) => {
                    chai.expect(siteInfo[ym][ecommerceParserDataFlag]).to.equal(
                        generateRandomTwoDigitNumber,
                    );
                });
                chai.expect(parserRequests.length).to.equal(1);
            });
    });

    it('should send params dr on click mobile checkout button', function () {
        return this.browser
            .timeoutsAsyncScript(3000)
            .url(checkoutMobilePage)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        Math.random = () => options.randomStub;

                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        auto_goals: 1,
                                        dr: options.currencyWithTotalSelectors,
                                    },
                                },
                            },
                            () => {
                                serverHelpers.collectRequests(2000);
                                new Ya.Metrika2(options.counterId);
                                setTimeout(() => {
                                    document
                                        .querySelector('#checkout-mobile-btn')
                                        .click();
                                }, 300);
                            },
                        );
                    },
                    counterId,
                    currencyWithTotalSelectors,
                    randomStub,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(geParserRequests)
            .then((parserRequests) => {
                parserRequests.forEach(({ siteInfo }) => {
                    chai.expect(siteInfo[ym][ecommerceParserDataFlag]).to.equal(
                        generateRandomTwoDigitNumber,
                    );
                });
                chai.expect(parserRequests.length).to.equal(2);
            });
    });

    it('should send params dr and dre on cart page (same selectors)', function () {
        return this.browser
            .timeoutsAsyncScript(3000)
            .url(basketPage)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        Math.random = () => options.randomStub;

                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        auto_goals: 1,
                                        dr: options.currencyWithTotalSelectors,
                                    },
                                },
                            },
                            () => {
                                serverHelpers.collectRequests(2000);
                                new Ya.Metrika2(options.counterId);
                            },
                        );
                    },
                    counterId,
                    currencyWithTotalSelectors,
                    randomStub,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(geParserRequests)
            .then((parserRequests) => {
                parserRequests.forEach(({ siteInfo }) => {
                    chai.expect(siteInfo[ym][ecommerceParserDataFlag]).to.equal(
                        encodeData,
                    );
                    chai.expect(
                        siteInfo[ym][ecommerceParserExtendedDataFlag],
                    ).to.equal(generateRandomTwoDigitNumber);
                });
                chai.expect(parserRequests.length).to.equal(1);
            });
    });

    it('should send params dr and dre on cart page (different selectors)', function () {
        return this.browser
            .timeoutsAsyncScript(3000)
            .url(basketPage)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        Math.random = () => options.randomStub;

                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        auto_goals: 1,
                                        dr: options.currencyAndTotalSelectors,
                                    },
                                },
                            },
                            () => {
                                serverHelpers.collectRequests(2000);
                                new Ya.Metrika2(options.counterId);
                            },
                        );
                    },
                    counterId,
                    currencyAndTotalSelectors,
                    randomStub,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(geParserRequests)
            .then((parserRequests) => {
                parserRequests.forEach(({ siteInfo }) => {
                    chai.expect(siteInfo[ym][ecommerceParserDataFlag]).to.equal(
                        encodeData,
                    );
                    chai.expect(
                        siteInfo[ym][ecommerceParserExtendedDataFlag],
                    ).to.equal(generateRandomTwoDigitNumber);
                });
                chai.expect(parserRequests.length).to.equal(1);
            });
    });

    it('should send params dr and dre on cart page (only currency selector)', function () {
        return this.browser
            .timeoutsAsyncScript(3000)
            .url(basketPage)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        Math.random = () => options.randomStub;

                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        auto_goals: 1,
                                        dr: options.onlyCurrencySelectors,
                                    },
                                },
                            },
                            () => {
                                serverHelpers.collectRequests(2000);
                                new Ya.Metrika2(options.counterId);
                            },
                        );
                    },
                    counterId,
                    onlyCurrencySelectors,
                    randomStub,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(geParserRequests)
            .then((parserRequests) => {
                parserRequests.forEach(({ siteInfo }) => {
                    chai.expect(siteInfo[ym][ecommerceParserDataFlag]).to.equal(
                        onlyCurrencyEncodeData,
                    );
                    chai.expect(
                        siteInfo[ym][ecommerceParserExtendedDataFlag],
                    ).to.equal(generateRandomTwoDigitNumber);
                });
                chai.expect(parserRequests.length).to.equal(1);
            });
    });

    it('should send params dr and dre on cart page (only total selector)', function () {
        return this.browser
            .timeoutsAsyncScript(3000)
            .url(basketPage)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        Math.random = () => options.randomStub;

                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        auto_goals: 1,
                                        dr: options.onlyTotalSelectors,
                                    },
                                },
                            },
                            () => {
                                serverHelpers.collectRequests(2000);
                                new Ya.Metrika2(options.counterId);
                            },
                        );
                    },
                    counterId,
                    onlyTotalSelectors,
                    randomStub,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(geParserRequests)
            .then((parserRequests) => {
                parserRequests.forEach(({ siteInfo }) => {
                    chai.expect(siteInfo[ym][ecommerceParserDataFlag]).to.equal(
                        onlyTotalEncodeData,
                    );
                    chai.expect(
                        siteInfo[ym][ecommerceParserExtendedDataFlag],
                    ).to.equal(generateRandomTwoDigitNumber);
                });
                chai.expect(parserRequests.length).to.equal(1);
            });
    });

    it('should send params dr and dre after change total', function () {
        return this.browser
            .timeoutsAsyncScript(5000)
            .url(basketPage)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        Math.random = () => options.randomStub;

                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        auto_goals: 1,
                                        dr: options.currencyAndTotalSelectors,
                                    },
                                },
                            },
                            () => {
                                serverHelpers.collectRequests(2000);
                                new Ya.Metrika2(options.counterId);

                                setTimeout(() => {
                                    const total =
                                        document.querySelector('#currency');
                                    total.innerHTML = '999';
                                }, 1000);
                            },
                        );
                    },
                    counterId,
                    currencyAndTotalSelectors,
                    randomStub,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(geParserRequests)
            .then((parserRequests) => {
                chai.expect(parserRequests.length).to.equal(2);
                chai.expect(
                    parserRequests[0].siteInfo[ym][ecommerceParserDataFlag],
                ).to.equal(encodeData);
                chai.expect(
                    parserRequests[1].siteInfo[ym][ecommerceParserDataFlag],
                ).to.equal(newEncodeData);
                parserRequests.forEach((request) => {
                    chai.expect(
                        request.siteInfo[ym][ecommerceParserExtendedDataFlag],
                    ).to.equal(generateRandomTwoDigitNumber);
                });
            });
    });

    it('should send params dr and dre on cart page (extended cart selector)', function () {
        return this.browser
            .timeoutsAsyncScript(3000)
            .url(basketPage)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        Math.random = () => options.randomStub;

                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        auto_goals: 1,
                                        dr: options.extendedCartSelectors,
                                    },
                                },
                            },
                            () => {
                                serverHelpers.collectRequests(2000);
                                new Ya.Metrika2(options.counterId);
                            },
                        );
                    },
                    counterId,
                    extendedCartSelectors,
                    randomStub,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(geParserRequests)
            .then((parserRequests) => {
                parserRequests.forEach(({ siteInfo }) => {
                    chai.expect(siteInfo[ym][ecommerceParserDataFlag]).to.equal(
                        encodeData,
                    );
                    chai.expect(
                        siteInfo[ym][ecommerceParserExtendedDataFlag],
                    ).to.equal(goodsInitialEncodedData);
                });
                chai.expect(parserRequests.length).to.equal(1);
            });
    });

    it('should send params dr and dre after change in goods data', function () {
        return this.browser
            .timeoutsAsyncScript(5000)
            .url(basketPage)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        Math.random = () => options.randomStub;

                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        auto_goals: 1,
                                        dr: options.extendedCartSelectors,
                                    },
                                },
                            },
                            () => {
                                serverHelpers.collectRequests(2000);
                                new Ya.Metrika2(options.counterId);

                                setTimeout(() => {
                                    const total =
                                        document.querySelector('.qty');
                                    total.innerHTML = '2';
                                }, 1000);
                            },
                        );
                    },
                    counterId,
                    extendedCartSelectors,
                    randomStub,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(geParserRequests)
            .then((parserRequests) => {
                chai.expect(parserRequests.length).to.equal(2);
                parserRequests.forEach((request) => {
                    chai.expect(
                        request.siteInfo[ym][ecommerceParserDataFlag],
                    ).to.equal(encodeData);
                });

                chai.expect(
                    parserRequests[0].siteInfo[ym][
                        ecommerceParserExtendedDataFlag
                    ],
                ).to.equal(goodsInitialEncodedData);
                chai.expect(
                    parserRequests[1].siteInfo[ym][
                        ecommerceParserExtendedDataFlag
                    ],
                ).to.equal(goodsAlteredEncodedData);
            });
    });
});
