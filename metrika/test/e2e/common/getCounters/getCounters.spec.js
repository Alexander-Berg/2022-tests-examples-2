const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('getCounters e2e', function () {
    const baseUrl = 'test/getCounters/getCounters.hbs';
    const twoCountersUrl = 'test/getCounters/getCountersTwoCounterPage.hbs';
    const DEFAULT_PROPERTIES = {
        type: 0,
        oldCode: false,
        trackHash: false,
        webvisor: false,
        clickmap: false,
    };
    const firstCounterId = 111;
    const secondCounterId = 222;
    const thirdCounterId = 3;
    const verifyLog = (rawValue, expectedValue) => {
        const parsed =
            typeof rawValue === 'string' ? JSON.parse(rawValue) : rawValue;
        const { staticMethod, instanceMethod } = parsed;
        chai.expect(instanceMethod).to.deep.eq(expectedValue);
        chai.expect(staticMethod).to.deep.eq(instanceMethod);
    };
    const goToUrl = (browser, url) =>
        browser
            .url(url)
            .deleteCookie()
            .execute(() => {
                window.createLog = function (constructorName) {
                    return {
                        staticMethod:
                            window.Ya[constructorName || 'Metrika2'].counters(),
                        instanceMethod: window.Ya._metrika.getCounters(),
                    };
                };
            })
            .timeoutsAsyncScript(10000);

    beforeEach(function () {
        return goToUrl(this.browser, baseUrl);
    });

    it('should work even if there are no counters on the page', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        window.ya_cid = true;
                        done(JSON.stringify(window.createLog()));
                    },
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: rawValue }) => {
                verifyLog(rawValue, []);
            });
    });

    it('should detect counter state from counterOptions', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        new Ya.Metrika2(options.firstCounterId);
                        new Ya.Metrika2({
                            id: options.secondCounterId,
                            type: 1,
                            accurateTrackBounce: true,
                        });
                        new Ya.Metrika2({
                            id: options.thirdCounterId,
                            webvisor: true,
                            trackHash: true,
                            trackLinks: true,
                        });

                        window.ya_cid = true;

                        done(JSON.stringify(window.createLog()));
                    },
                    firstCounterId,
                    secondCounterId,
                    thirdCounterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: rawValue }) => {
                const expectedValue = [
                    { id: firstCounterId },
                    { id: secondCounterId, accurateTrackBounce: true, type: 1 },
                    {
                        id: thirdCounterId,
                        webvisor: true,
                        trackHash: true,
                        trackLinks: true,
                    },
                ].map((val) => ({
                    ...DEFAULT_PROPERTIES,
                    oldCode: true,
                    ...val,
                }));
                verifyLog(rawValue, expectedValue);
            });
    });

    it('Should detect counter state when coutner methods are called', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter1 = new Ya.Metrika2(
                            options.firstCounterId,
                        );
                        window.ya_cid = true;
                        const counter2 = new Ya.Metrika2(
                            options.secondCounterId,
                        );
                        window.ya_cid = false;
                        const counter3 = new Ya.Metrika2({
                            id: options.thirdCounterId,
                            trackHash: true,
                        });

                        counter1.notBounce();
                        counter2.trackHash(true);
                        counter3.trackLinks({});
                        counter3.trackHash(false);
                        counter3.clickmap(true);

                        done(JSON.stringify(window.createLog()));
                    },
                    firstCounterId,
                    secondCounterId,
                    thirdCounterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: rawValue }) => {
                const expectedValue = [
                    { id: firstCounterId, accurateTrackBounce: true },
                    { id: secondCounterId, trackHash: true },
                    { id: thirdCounterId, trackLinks: true, clickmap: true },
                ].map((val) => ({ ...DEFAULT_PROPERTIES, ...val }));
                verifyLog(rawValue, expectedValue);
            });
    });

    it('Should consider destruct()', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const states = [];
                        const createEntry = () => {
                            states.push(window.createLog());
                        };
                        const counter1 = new Ya.Metrika2(
                            options.firstCounterId,
                        );
                        const counter2 = new Ya.Metrika2({
                            id: options.secondCounterId,
                            clickmap: {},
                        });
                        const counter3 = new Ya.Metrika2({
                            id: options.thirdCounterId,
                            trackLinks: true,
                        });

                        createEntry();
                        counter1.destruct();
                        createEntry();

                        counter2.destruct();
                        createEntry();

                        counter3.destruct();
                        createEntry();
                        done(JSON.stringify(states));
                    },
                    firstCounterId,
                    secondCounterId,
                    thirdCounterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: data }) => {
                const calls = JSON.parse(data);
                const expectedGlobalState = [
                    {
                        id: firstCounterId,
                    },
                    {
                        id: secondCounterId,
                        clickmap: true,
                    },
                    {
                        id: thirdCounterId,
                        trackLinks: true,
                    },
                ].map((val) => ({
                    ...DEFAULT_PROPERTIES,
                    ...val,
                }));
                calls.forEach((rawValue) => {
                    verifyLog(rawValue, expectedGlobalState);
                    expectedGlobalState.shift();
                });
            });
    });

    it('Should work OK for pages with multiple scripts', function () {
        return goToUrl(this.browser, twoCountersUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const states = [];
                        const createEntry = () => {
                            states.push(window.createLog());
                        };

                        window.ya_cid = true;
                        const counter1 = new Ya.Metrika2(
                            options.firstCounterId,
                        );

                        window.ya_cid = false;
                        const counter2 = new Ya.Metrika(
                            options.secondCounterId,
                        );

                        createEntry();
                        counter1.notBounce();
                        counter2.trackHash(true);
                        createEntry();
                        done(JSON.stringify(states));
                    },
                    firstCounterId,
                    secondCounterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: data }) => {
                const states = JSON.parse(data);
                const expectedValues = [
                    [
                        {
                            id: firstCounterId,
                        },
                        {
                            id: secondCounterId,
                        },
                    ],
                    [
                        {
                            id: firstCounterId,
                            accurateTrackBounce: true,
                        },
                        {
                            id: secondCounterId,
                            trackHash: true,
                        },
                    ],
                ].map((vals) =>
                    vals.map((override) => ({
                        ...DEFAULT_PROPERTIES,
                        ...override,
                    })),
                );

                states.forEach((rawValue, i) => {
                    verifyLog(rawValue, expectedValues[i]);
                });
            });
    });
});
