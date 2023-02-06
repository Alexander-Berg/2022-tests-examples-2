const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('DebugConsole e2e test', function () {
    const baseUrl = 'test/debugConsole/debugConsole.hbs';
    const baseUrlWithDebugConsoleFlag = `${baseUrl}?_ym_debug=1`;
    const counterId = 26302566;
    const ignoredCounterId = 26812653;
    const schema = 'json_ld';
    const testUrl = `contacts`;
    const testReferer = 'http://example.com/main';
    const testTitle = 'Контактная информация';
    const testGoal = 'TEST_GOAL';
    const goalParams = {
        order_price: 1000.35,
        currency: 'RUB',
    };
    const PARAMS_WORD = 'Params';

    const logs = {
        startPublisher: `Publishers analytics schema`,
        sendPublisher: `Publisher content info found`,
        publishersArticleTooSmall: `Warning: content has only`,
        hitWords: ['PageView', 'Counter', 'URL', 'Referrer', counterId],
        goalWords: [
            'Reach goal',
            'Counter',
            'Goal id',
            'Params',
            counterId,
            testGoal,
        ],
        paramsWords: ['Params.', `Counter ${counterId}`, 'Params:'],
        duplicate: `Duplicate counter ${counterId}:0 initialization`,
    };

    const splitDebugLogs = (consoleMessages) => {
        const log = {
            publishersSchema: [],
            publishersContent: [],
            publishersArticleTooSmall: [],
            duplicate: [],
            goal: [],
            hit: [],
            params: [],
        };

        consoleMessages.forEach((message) => {
            if (message.includes('Publishers analytics')) {
                log.publishersSchema.push(message);
            } else if (message.includes('Publisher content')) {
                log.publishersContent.push(message);
            } else if (message.includes('Warning: content has only')) {
                log.publishersArticleTooSmall.push(message);
            } else if (message.includes('Duplicate counter')) {
                log.duplicate.push(message);
            } else if (message.includes('Reach goal')) {
                log.goal.push(message);
            } else if (message.includes('PageView')) {
                log.hit.push(message);
            } else if (message.includes('Params')) {
                log.params.push(message);
            }
        });

        return log;
    };

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000).deleteCookie();
    });

    it('no console with disable debug console', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        // eslint-disable-next-line no-undef
                        const script = initCounterFromLocalJs();
                        script.onload = function () {
                            new Ya.Metrika2(options.counterId);
                            serverHelpers.onRequest(function () {
                                done();
                            });
                        };
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleDebugConsole(this.browser))
            .then((consoleMessages) => {
                chai.expect(consoleMessages).to.be.empty;
            });
    });

    it('enable debug console with url param', function () {
        return this.browser
            .url(baseUrlWithDebugConsoleFlag)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        // eslint-disable-next-line no-undef
                        const script = initCounterFromLocalJs();
                        script.onload = function () {
                            new Ya.Metrika2(options.counterId);
                            serverHelpers.onRequest(function () {
                                done();
                            });
                        };
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleDebugConsole(this.browser))
            .then((consoleMessages) => {
                chai.expect(consoleMessages).to.be.not.empty;
            });
    });

    it('enable debug console with cookie', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        document.cookie = '_ym_debug=1';
                        // eslint-disable-next-line no-undef
                        const script = initCounterFromLocalJs();
                        script.onload = function () {
                            new Ya.Metrika2(options.counterId);
                            serverHelpers.onRequest(function () {
                                done();
                            });
                        };
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleDebugConsole(this.browser))
            .then((consoleMessages) => {
                chai.expect(consoleMessages).to.be.not.empty;
            });
    });

    it('enable debug console with window flag', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        window._ym_debug = '1';

                        // eslint-disable-next-line no-undef
                        const script = initCounterFromLocalJs();
                        script.onload = function () {
                            new Ya.Metrika2(options.counterId);
                            serverHelpers.onRequest(function () {
                                done();
                            });
                        };
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleDebugConsole(this.browser))
            .then((consoleMessages) => {
                chai.expect(consoleMessages).to.be.not.empty;
            });
    });

    it('debug console first hit and start, send publishers', function () {
        return this.browser
            .url(baseUrlWithDebugConsoleFlag)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        // eslint-disable-next-line no-undef
                        const script = initCounterFromLocalJs();
                        script.onload = function () {
                            new Ya.Metrika2(options.counterId);
                            serverHelpers.collectRequests(500);
                        };
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleDebugConsole(this.browser))
            .then((consoleMessages) => {
                const {
                    hit,
                    publishersContent,
                    publishersSchema,
                    publishersArticleTooSmall,
                } = splitDebugLogs(consoleMessages);

                logs.hitWords.forEach((word) => {
                    chai.expect(hit[0]).to.be.include(word);
                });

                chai.expect(hit[0]).not.include(PARAMS_WORD);

                chai.expect(hit[0]).to.be.include(
                    `${e2eUtils.baseUrl}/${baseUrlWithDebugConsoleFlag}`,
                );
                chai.expect(publishersContent[0]).to.be.include(
                    logs.sendPublisher,
                );
                chai.expect(publishersSchema[0]).to.be.include(schema);
                chai.expect(publishersSchema[0]).to.be.include(
                    logs.startPublisher,
                );
                chai.expect(publishersArticleTooSmall[0]).to.be.include(
                    logs.publishersArticleTooSmall,
                );
            });
    });

    it('debug console artificial hit', function () {
        return this.browser
            .url(baseUrlWithDebugConsoleFlag)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        // eslint-disable-next-line no-undef
                        const script = initCounterFromLocalJs();
                        script.onload = function () {
                            const counter = new Ya.Metrika2(options.counterId);
                            counter.hit(options.testUrl, {
                                title: options.testTitle,
                                referer: options.testReferer,
                                params: options.goalParams,
                            });

                            serverHelpers.onRequest(function (request) {
                                if (
                                    request.url.indexOf(options.testUrl) !== -1
                                ) {
                                    done(request);
                                }
                            });
                        };
                    },
                    counterId,
                    testUrl,
                    testTitle,
                    testReferer,
                    goalParams,
                }),
            )
            .then(e2eUtils.handleDebugConsole(this.browser))
            .then((consoleMessages) => {
                const { hit: hits } = splitDebugLogs(consoleMessages);
                let hasArtificialHit = false;

                chai.expect(hits.length).to.be.equal(2);
                hits.forEach((hit) => {
                    logs.hitWords.forEach((word) => {
                        chai.expect(hit).to.be.include(word);
                    });

                    if (hit.includes(testUrl)) {
                        hasArtificialHit = true;
                        chai.expect(hit).to.be.include(testUrl);
                        chai.expect(hit).to.be.include(testReferer);
                        chai.expect(hit).to.be.include(PARAMS_WORD);
                    } else {
                        chai.expect(hit).to.be.include(
                            `${e2eUtils.baseUrl}/${baseUrlWithDebugConsoleFlag}`,
                        );
                    }
                });

                chai.expect(hasArtificialHit).to.be.true;
            });
    });

    it('debug console reach goal', function () {
        return this.browser
            .url(baseUrlWithDebugConsoleFlag)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        // eslint-disable-next-line no-undef
                        const script = initCounterFromLocalJs();
                        script.onload = function () {
                            const counter = new Ya.Metrika2(options.counterId);

                            counter.reachGoal(
                                options.testGoal,
                                options.goalParams,
                            );

                            serverHelpers.onRequest(function (request) {
                                if (
                                    request.url.indexOf('page-url=goal') !== -1
                                ) {
                                    done(request);
                                }
                            });
                        };
                    },
                    counterId,
                    testGoal,
                    goalParams,
                }),
            )
            .then(e2eUtils.handleDebugConsole(this.browser))
            .then((consoleMessages) => {
                const { goal } = splitDebugLogs(consoleMessages);

                logs.goalWords.forEach((word) => {
                    chai.expect(goal[0]).to.be.include(word);
                });
            });
    });

    it('debug .params', function () {
        return this.browser
            .url(baseUrlWithDebugConsoleFlag)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        // eslint-disable-next-line no-undef
                        const script = initCounterFromLocalJs();
                        script.onload = function () {
                            const counter = new Ya.Metrika2(options.counterId);
                            counter.params(options.goalParams);
                            serverHelpers.onRequest(function (request) {
                                if (
                                    request.url.indexOf(
                                        encodeURIComponent('pa:1'),
                                    ) !== -1
                                ) {
                                    done(request);
                                }
                            });
                        };
                    },
                    counterId,
                    goalParams,
                }),
            )
            .then(e2eUtils.handleDebugConsole(this.browser))
            .then((consoleMessages) => {
                const { params } = splitDebugLogs(consoleMessages);

                logs.paramsWords.forEach((word) => {
                    chai.expect(params[0]).to.be.include(word);
                });
            });
    });

    it('debug duplicate counter', function () {
        return this.browser
            .url(baseUrlWithDebugConsoleFlag)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        // eslint-disable-next-line no-undef
                        const script = initCounterFromLocalJs();
                        script.onload = function () {
                            new Ya.Metrika2(options.counterId);
                            new Ya.Metrika2(options.counterId);

                            serverHelpers.onRequest(function (request) {
                                done(request);
                            });
                        };
                    },
                    counterId,
                    testGoal,
                    goalParams,
                }),
            )
            .then(e2eUtils.handleDebugConsole(this.browser))
            .then((consoleMessages) => {
                const { duplicate } = splitDebugLogs(consoleMessages);

                chai.expect(duplicate[0]).to.be.include(logs.duplicate);
            });
    });

    it('should not log for ignored counters ( like Yandex Share )', function () {
        return this.browser
            .url(baseUrlWithDebugConsoleFlag)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        // eslint-disable-next-line no-undef
                        const script = initCounterFromLocalJs();
                        script.onload = function () {
                            new Ya.Metrika2(options.counterId);
                            serverHelpers.onRequest(function () {
                                done();
                            });
                        };
                    },
                    counterId: ignoredCounterId,
                }),
            )
            .then(e2eUtils.handleDebugConsole(this.browser))
            .then((consoleMessages) => {
                const pageViewMessage = consoleMessages.find((message) =>
                    message.startsWith('"PageView. Counter 26812653.'),
                );
                chai.expect(pageViewMessage).to.not.exist;
            });
    });
});
