const chai = require('chai');
const e2eUtils = require('../../utils/index.js');
const constants = require('../../../../src/providers/clickmap/constants.ts');

describe('ClickMap', () => {
    const pathToTestPage = 'test/clickmap/clickmap.hbs';
    const testUrl = `${e2eUtils.baseUrl}/${pathToTestPage}`;
    const pointerLinkResultBaseRe =
        'rn:\\d+:x:-?\\d+:y:-?\\d+:t:\\d+:p:[\\w|;]+:X:\\d+:Y:\\d+';
    const pointerLinkWithoutTrackHash = new RegExp(
        `^${pointerLinkResultBaseRe}$`,
    );
    const pointerLinkWithTrackHash = new RegExp(
        `^${pointerLinkResultBaseRe}:wh:1$`,
    );
    const counterId = 26302566;

    const checkClmapRequests =
        (expectedRequestsCount, hashTracking = false) =>
        (result) => {
            const clmapUrlRegexp = new RegExp(
                `[http|s?]://[^/]+/clmap/${counterId}`,
            );

            const clmapRequestsCount = result.value.reduce((acc, request) => {
                const { url, params } = e2eUtils.getRequestParams(request);
                if (clmapUrlRegexp.test(url)) {
                    if (params['page-url'] !== testUrl) {
                        return acc;
                    }
                    if (!params['browser-info']) {
                        return acc;
                    }
                    if (
                        hashTracking &&
                        !pointerLinkWithTrackHash.test(params['pointer-click'])
                    ) {
                        return acc;
                    }
                    if (
                        !hashTracking &&
                        !pointerLinkWithoutTrackHash.test(
                            params['pointer-click'],
                        )
                    ) {
                        return acc;
                    }

                    // eslint-disable-next-line no-param-reassign
                    acc += 1;
                }
                return acc;
            }, 0);

            chai.expect(clmapRequestsCount).to.be.equal(expectedRequestsCount);
        };

    beforeEach(function () {
        return this.browser.deleteCookie().timeoutsAsyncScript(10000);
    });

    describe('Checks browser-info', () => {
        it('Without hash tracking', function () {
            return this.browser
                .url(testUrl)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            new Ya.Metrika2({
                                id: options.counterId,
                                clickmap: true,
                            });

                            document.querySelector('#img1').click();
                            serverHelpers.collectRequests(200);
                        },
                        counterId,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(checkClmapRequests(1));
        });
        it('With hash tracking', function () {
            return this.browser
                .url(testUrl)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            new Ya.Metrika2({
                                id: options.counterId,
                                clickmap: {
                                    isTrackHash: true,
                                },
                            });

                            document.querySelector('#img1').click();
                            serverHelpers.collectRequests(200);
                        },
                        counterId,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(checkClmapRequests(1, true));
        });
    });
    describe('Checks no clickmap', () => {
        it('No clickmap option', function () {
            return this.browser
                .url(testUrl)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            new Ya.Metrika2({
                                id: options.counterId,
                            });

                            document.querySelector('#img1').click();
                            serverHelpers.collectRequests(200);
                        },
                        counterId,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(checkClmapRequests(0));
        });
        it('Clickmap option set to false', function () {
            return this.browser
                .url(testUrl)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            new Ya.Metrika2({
                                id: options.counterId,
                                clickmap: false,
                            });

                            document.querySelector('#img1').click();
                            serverHelpers.collectRequests(200);
                        },
                        counterId,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(checkClmapRequests(0));
        });
    });
    describe('Exclude tags options', () => {
        it('Checks ym-disable-clickmap class in element', function () {
            return this.browser
                .url(testUrl)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            new Ya.Metrika2({
                                id: options.counterId,
                                clickmap: true,
                            });

                            document.querySelector('#div4').click();
                            serverHelpers.collectRequests(200);
                        },
                        counterId,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(checkClmapRequests(0));
        });
        it('Checks ym-disable-clickmap class in parents', function () {
            return this.browser
                .url(testUrl)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            new Ya.Metrika2({
                                id: options.counterId,
                                clickmap: true,
                            });

                            document.querySelector('#img2').click();
                            serverHelpers.collectRequests(200);
                        },
                        counterId,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(checkClmapRequests(0));
        });
        it('Checks ignoreTags option', function () {
            return this.browser
                .url(testUrl)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            new Ya.Metrika2({
                                id: options.counterId,
                                clickmap: {
                                    ignoreTags: ['iMg'],
                                },
                            });

                            document.querySelector('#img1').click();
                            serverHelpers.collectRequests(200);
                        },
                        counterId,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(checkClmapRequests(0));
        });
        it('Checks custom filter function option', function () {
            return this.browser
                .url(testUrl)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            serverHelpers.collectRequests(1000);
                            new Ya.Metrika2({
                                id: options.counterId,
                                clickmap: {
                                    filter: (domElement) => {
                                        if (
                                            domElement.className === 'div2' ||
                                            domElement.id === 'div3'
                                        ) {
                                            return false;
                                        }
                                        return true;
                                    },
                                },
                            });

                            setTimeout(() => {
                                document.querySelector('#div2').click();
                                setTimeout(() => {
                                    document.querySelector('#img1').click();
                                }, options.timeout);
                                setTimeout(() => {
                                    document.querySelector('#div3').click();
                                }, options.timeout * 2);
                            }, 300);
                        },
                        counterId,
                        timeout: constants.TIMEOUT_CLICK,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(checkClmapRequests(1));
        });
    });
    describe('Checks timeouts', () => {
        it('Checks two clicks on same element during TIMEOUT_SAME_CLICKS ms', function () {
            return this.browser
                .url(testUrl)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            new Ya.Metrika2({
                                id: options.counterId,
                                clickmap: true,
                            });

                            document.querySelector('#div2').click();
                            setTimeout(() => {
                                document.querySelector('#div2').click();
                            }, options.timeout - 50);
                            serverHelpers.collectRequests(1000);
                        },
                        counterId,
                        timeout: constants.TIMEOUT_CLICK,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(checkClmapRequests(1));
        });
        it('Checks two clicks on same element in TIMEOUT_SAME_CLICKS ms', function () {
            return this.browser
                .url(testUrl)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            serverHelpers.collectRequests(2000);

                            new Ya.Metrika2({
                                id: options.counterId,
                                clickmap: true,
                            });

                            document.querySelector('#div2').click();
                            setTimeout(() => {
                                document.querySelector('#div2').click();
                            }, options.timeout);
                        },
                        counterId,
                        timeout: constants.TIMEOUT_SAME_CLICKS,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(checkClmapRequests(2));
        });
        it('Checks two clicks with different position during TIMEOUT_CLICK ms', function () {
            return this.browser
                .url(testUrl)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            serverHelpers.collectRequests(200);
                            new Ya.Metrika2({
                                id: options.counterId,
                                clickmap: true,
                            });
                            document.querySelector('#div2').click();
                            setTimeout(() => {
                                document.querySelector('#div3').click();
                            }, options.timeout - 20);
                        },
                        counterId,
                        timeout: constants.TIMEOUT_CLICK,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(checkClmapRequests(1));
        });
        it('Checks two clicks with different position in TIMEOUT_CLICK ms', function () {
            return this.browser
                .url(testUrl)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            serverHelpers.collectRequests(300);
                            new Ya.Metrika2({
                                id: options.counterId,
                                clickmap: true,
                            });
                            document.querySelector('#div2').click();
                            setTimeout(() => {
                                document.querySelector('#div3').click();
                            }, options.timeout);
                        },
                        counterId,
                        timeout: constants.TIMEOUT_CLICK,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(checkClmapRequests(2));
        });
    });
    describe('Checks quota', () => {
        it('Checks non-zero quota', function () {
            return this.browser
                .url(testUrl)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            new Ya.Metrika2({
                                id: options.counterId,
                                clickmap: {
                                    quota: 4,
                                },
                            });

                            document.querySelector('#div2').click();
                            setTimeout(() => {
                                document.querySelector('#div3').click();
                            }, options.timeout - 20);
                            setTimeout(() => {
                                document.querySelector('#img1').click();
                            }, options.timeout * 2);
                            setTimeout(() => {
                                document.querySelector('#div3').click();
                            }, options.timeout * 3);
                            setTimeout(() => {
                                document.querySelector('#div2').click();
                            }, options.timeout * 4);
                            serverHelpers.collectRequests(2000);
                        },
                        counterId,
                        timeout: constants.TIMEOUT_CLICK,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(checkClmapRequests(4));
        });
        it('Checks zero quota', function () {
            return (
                this.browser
                    .url(testUrl)
                    .then(
                        e2eUtils.provideServerHelpers(this.browser, {
                            cb(serverHelpers, options) {
                                new Ya.Metrika2({
                                    id: options.counterId,
                                    clickmap: {
                                        quota: 0,
                                    },
                                });

                                document.querySelector('#div2').click();
                                setTimeout(() => {
                                    document.querySelector('#div3').click();
                                }, options.timeout);
                                setTimeout(() => {
                                    document.querySelector('#img1').click();
                                }, options.timeout * 2);
                                serverHelpers.collectRequests(2000);
                            },
                            counterId,
                            timeout: 10 + constants.TIMEOUT_CLICK,
                        }),
                    )
                    .then(e2eUtils.handleRequest(this.browser))
                    // в старом счетчике 'quota: 0' интерпретируется как бесконечная квота
                    // для совместимости оставляем в новом так же
                    .then(checkClmapRequests(3))
            );
        });
    });
    describe('Mouse buttons checking', function () {
        it('Click A tag by LEFT mouse button', function () {
            return this.browser
                .url(testUrl)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            new Ya.Metrika2({
                                id: options.counterId,
                                clickmap: true,
                            });

                            document.querySelector('#link').dispatchEvent(
                                new MouseEvent('click', {
                                    button: 0,
                                }),
                            );

                            serverHelpers.collectRequests(200);
                        },
                        counterId,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(checkClmapRequests(1));
        });
        it('Click A tag by CENTRAL mouse button', function () {
            return this.browser
                .url(testUrl)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            new Ya.Metrika2({
                                id: options.counterId,
                                clickmap: true,
                            });

                            document.querySelector('#link').dispatchEvent(
                                new MouseEvent('click', {
                                    button: 1,
                                }),
                            );

                            serverHelpers.collectRequests(200);
                        },
                        counterId,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(checkClmapRequests(1));
        });
        it('Click A tag by RIGHT mouse button', function () {
            return this.browser
                .url(testUrl)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            new Ya.Metrika2({
                                id: options.counterId,
                                clickmap: true,
                            });

                            document.querySelector('#link').dispatchEvent(
                                new MouseEvent('click', {
                                    button: 2,
                                }),
                            );

                            serverHelpers.collectRequests(200);
                        },
                        counterId,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(checkClmapRequests(1));
        });
        it('Click non-A tag by central and right mouse button', function () {
            return this.browser
                .url(testUrl)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            new Ya.Metrika2({
                                id: options.counterId,
                                clickmap: true,
                            });

                            const event1 = new MouseEvent('click', {
                                button: 1,
                            });
                            const event2 = new MouseEvent('click', {
                                button: 2,
                            });

                            document
                                .querySelector('#div3')
                                .dispatchEvent(event1);
                            setTimeout(() => {
                                document
                                    .querySelector('#img1')
                                    .dispatchEvent(event2);
                            }, options.timeout);

                            serverHelpers.collectRequests(200);
                        },
                        counterId,
                        timeout: constants.TIMEOUT_CLICK,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(checkClmapRequests(0));
        });
    });
    describe('Near clicks checking', function () {
        it('Same mouse position click', function () {
            return this.browser
                .url(testUrl)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            new Ya.Metrika2({
                                id: options.counterId,
                                clickmap: true,
                            });

                            const event1 = new MouseEvent('click', {
                                clientX: 1,
                                clientY: 1,
                            });
                            const event2 = new MouseEvent('click', {
                                clientX: options.delta,
                                clientY: options.delta,
                            });

                            document
                                .querySelector('#div1')
                                .dispatchEvent(event1);
                            setTimeout(() => {
                                document
                                    .querySelector('#div1')
                                    .dispatchEvent(event2);
                            }, options.timeout);

                            serverHelpers.collectRequests(200);
                        },
                        counterId,
                        timeout: constants.TIMEOUT_CLICK,
                        delta: constants.DELTA_SAME_CLICKS,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(checkClmapRequests(1));
        });
        it('Different mouse position click', function () {
            return this.browser
                .url(testUrl)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            new Ya.Metrika2({
                                id: options.counterId,
                                clickmap: true,
                            });

                            const event1 = new MouseEvent('click', {
                                clientX: 1,
                                clientY: 1,
                            });
                            const event2 = new MouseEvent('click', {
                                clientX: options.delta + 1,
                                clientY: options.delta + 1,
                            });

                            document
                                .querySelector('#div1')
                                .dispatchEvent(event1);
                            setTimeout(() => {
                                document
                                    .querySelector('#div1')
                                    .dispatchEvent(event2);
                            }, options.timeout);

                            serverHelpers.collectRequests(200);
                        },
                        counterId,
                        timeout: constants.TIMEOUT_CLICK,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(checkClmapRequests(1));
        });
    });
});
