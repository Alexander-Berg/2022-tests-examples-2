const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Page Load Time', function () {
    const baseUrl = 'test/pageLoadTime/pageLoadTime.hbs';
    const firstCounterId = 26302566;
    const secondCounterId = 24226447;
    const PERF_DIFS = [
        // 0 DNSTiming
        ['domainLookupEnd', 'domainLookupStart'],
        // 1 ConnectTiming
        ['connectEnd', 'connectStart'],
        // 2 ResponseStartTiming
        ['responseStart', 'requestStart'],
        // 3 ResponseEndTiming
        ['responseEnd', 'responseStart'],
        // 4 FetchTiming
        ['fetchStart', 'navigationStart'],
        // 5 RedirectTiming
        ['redirectEnd', 'redirectStart'],
        // 6 RedirectCount
        [
            (performance) =>
                performance.timing.redirectCount ||
                (performance.navigation &&
                    performance.navigation.redirectCount),
        ],
        // 7 DOMInteractiveTiming
        ['domInteractive', 'domLoading'],
        // 8 DOMContentLoadedTiming
        ['domContentLoadedEventEnd', 'domContentLoadedEventStart'],
        // 9 DOMCompleteTiming
        ['domComplete', 'navigationStart'],
        // 10 LoadEventStartTiming
        ['loadEventStart', 'navigationStart'],
        // 11 LoadEventEndTiming
        ['loadEventEnd', 'loadEventStart'],
        // 12 NSToDOMContentLoadedTiming
        ['domContentLoadedEventStart', 'navigationStart'],
    ];
    const itemsUnknownEarlyOn = {
        responseEnd: 1,
        domInteractive: 1,
        domContentLoadedEventStart: 1,
        domContentLoadedEventEnd: 1,
        domComplete: 1,
        loadEventStart: 1,
        loadEventEnd: 1,
        unloadEventStart: 1,
        unloadEventEnd: 1,
        secureConnectionStart: 1,
    };
    const isUnknownTiming = (item) => {
        const [left, right] = item;
        return itemsUnknownEarlyOn[left] || itemsUnknownEarlyOn[right];
    };
    const getPerformanceStats = (performance) => {
        return PERF_DIFS.map((item) => {
            const { timing } = performance;
            const [left, right] = item;

            if (typeof left === 'function') {
                return left(performance, timing) || '';
            }

            if (typeof right === 'function') {
                return '';
            }

            let shouldSubtract = Boolean(timing[left] && timing[right]);

            if (!shouldSubtract && item.length === 2) {
                shouldSubtract =
                    timing[left] === 0 &&
                    timing[right] === 0 &&
                    !isUnknownTiming(item);
            }

            if (shouldSubtract) {
                const diff =
                    Math.round(timing[left]) - Math.round(timing[right]);
                if (diff < 0 || diff > 36e5) {
                    return '';
                }
                return diff;
            }

            if (item.length === 1 && timing[left]) {
                return Math.round(timing[left]);
            }

            return '';
        });
    };

    beforeEach(function () {
        return this.browser
            .deleteCookie()
            .timeoutsAsyncScript(10000)
            .url(baseUrl);
    });

    it('Sends the Performance Info Correctly', function () {
        return this.browser
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const memoizedPerformance =
                            window.globalRequestsData.memoizePerformance(
                                window.performance,
                                options.perfDifs,
                            );

                        new Ya.Metrika2({
                            id: options.firstCounterId,
                        });

                        serverHelpers.onRequest(function (request) {
                            done({
                                performanceAPI: memoizedPerformance,
                                request,
                            });
                        });
                    },
                    firstCounterId,
                    perfDifs: [...PERF_DIFS.slice(0, 6), ...PERF_DIFS.slice(7)],
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: data }) => {
                const { performanceAPI, request } = data;
                const {
                    brInfo: { ds: actualPerformanceStats },
                } = e2eUtils.getRequestParams(request);

                if (!performanceAPI) {
                    chai.expect(actualPerformanceStats).to.equal(undefined);

                    return;
                }

                const expectedPerformanceStats =
                    getPerformanceStats(performanceAPI).join(',');

                chai.expect(actualPerformanceStats).to.equal(
                    expectedPerformanceStats,
                );
            });
    });

    it('Two counters should send the Performance Stats Independently', function () {
        return this.browser
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const requests = [];
                        const memoizedPerformace =
                            window.globalRequestsData.memoizePerformance(
                                window.performance,
                                options.perfDifs,
                            );

                        new Ya.Metrika2({
                            id: options.firstCounterId,
                        });

                        new Ya.Metrika2({
                            id: options.secondCounterId,
                        });

                        serverHelpers.onRequest(function (request) {
                            requests.push(request);

                            if (requests.length === 2) {
                                done({
                                    performanceAPI: memoizedPerformace,
                                    requests,
                                });
                            }
                        });
                    },
                    firstCounterId,
                    secondCounterId,
                    perfDifs: [...PERF_DIFS.slice(0, 6), ...PERF_DIFS.slice(7)],
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: data }) => {
                const { performanceAPI, requests } = data;
                const dsInfo = requests.map((request) => {
                    const {
                        brInfo: { ds },
                    } = e2eUtils.getRequestParams(request);

                    return ds;
                });

                if (!performanceAPI) {
                    chai.expect(dsInfo[0]).to.equal(undefined);
                    chai.expect(dsInfo[1]).to.equal(undefined);

                    return;
                }

                const expectedPerformanceStats =
                    getPerformanceStats(performanceAPI).join(',');

                chai.expect(dsInfo[0]).to.equal(expectedPerformanceStats);
                chai.expect(dsInfo[1]).to.equal(expectedPerformanceStats);
            });
    });

    it('Hits Should Not Duplicate the DS Values Sent in the Preceding Hits', function () {
        return this.browser
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const memoizedPerformace =
                            window.globalRequestsData.memoizePerformance(
                                window.performance,
                                options.perfDifs,
                            );

                        window.globalRequestsData.counter.hit(
                            'https://google.com',
                        );
                        window.globalRequestsData.counter.hit(
                            'https://yahoo.com',
                        );
                        serverHelpers.onRequest(function () {
                            const { initialRequests } =
                                window.globalRequestsData;

                            if (initialRequests.length === 4) {
                                done({
                                    requests: initialRequests,
                                    performanceAPI: memoizedPerformace,
                                });
                            }
                        });
                    },
                    perfDifs: PERF_DIFS,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: data }) => {
                const { requests, performanceAPI } = data;
                const requestsDSInfo = requests.map((request) => {
                    const {
                        brInfo: { ds },
                    } = e2eUtils.getRequestParams(request);

                    if (!ds) {
                        return null;
                    }

                    return ds.split(',');
                });

                if (!performanceAPI) {
                    requestsDSInfo.forEach((ds) => {
                        chai.expect(ds).to.equal(null);
                    });

                    return;
                }

                const statsCount = PERF_DIFS.length;
                const requestCount = requestsDSInfo.length;

                for (let i = 0; i < statsCount; i += 1) {
                    const statValuesSentMap = {};

                    for (let j = 0; j < requestCount; j += 1) {
                        const allRequestStats = requestsDSInfo[j];

                        if (allRequestStats) {
                            const statValue = allRequestStats[i];

                            if (statValue !== '') {
                                chai.expect(
                                    statValuesSentMap[statValue],
                                ).to.equal(undefined);
                                statValuesSentMap[statValue] = true;
                            }
                        }
                    }
                }
            });
    });
});
