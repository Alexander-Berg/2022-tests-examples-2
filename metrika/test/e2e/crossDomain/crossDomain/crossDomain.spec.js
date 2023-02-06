const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('crossDomain', function () {
    const baseUrl = `${e2eUtils.baseUrl}/test/crossDomain/crossDomain.hbs`;
    const counterId = 12345;

    beforeEach(function () {
        return this.browser
            .timeoutsAsyncScript(10000)
            .url(baseUrl)
            .deleteCookie()
            .localStorage('DELETE')
            .execute(function () {
                document.cookie = 'gdpr=0';
                localStorage.setItem('_ym_synced', '{"SYNCED_ADM":9999999999}');
            });
    });

    it('should find crossDomain page', function () {
        return this.browser.getText('body').then((innerText) => {
            chai.expect(
                'crossDomain page',
                'check if page contains required text',
            ).to.be.equal(innerText);
        });
    });

    it('the first request contains no crossDomain vars', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/${options.counterId}`,
                                    count: 2,
                                    body: {
                                        settings: {
                                            pcs: '0',
                                        },
                                    },
                                },
                            ],
                            function () {
                                serverHelpers.collectRequests(2000);
                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                            },
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const brInfos = requests.reduce((acc, request) => {
                    const { url, brInfo } = e2eUtils.getRequestParams(request);
                    if (url.indexOf('/watch/') !== -1) {
                        acc.push(brInfo);
                    }
                    return acc;
                }, []);
                chai.expect(
                    brInfos.length,
                    'we have caught at least the first request',
                ).to.be.at.least(1);
                chai.expect(
                    brInfos[0].pp,
                    'there is no PP var in the first request',
                ).to.be.undefined;
                chai.expect(
                    brInfos[0].pu,
                    'there is no PU var in the first request',
                ).to.be.undefined;
                chai.expect(
                    brInfos[0].zzlc,
                    'there is no ZZLC var in the first request',
                ).to.be.undefined;
            });
    });

    it('should be no crossDomain activity if isEU is set ', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/${options.counterId}`,
                                    count: 2,
                                    body: {
                                        settings: {
                                            pcs: '0',
                                            eu: '1',
                                        },
                                        userData: {},
                                    },
                                },
                            ],
                            function () {
                                const counter = new Ya.Metrika2({
                                    id: options.counterId,
                                });
                                const requests = [];
                                serverHelpers.onRequest(function (request) {
                                    requests.push(request);
                                });

                                setTimeout(() => {
                                    counter.reachGoal('random', {});
                                }, 500);

                                setTimeout(() => {
                                    done(requests);
                                }, 1500);
                            },
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const brInfos = requests.reduce((acc, request) => {
                    const { url, brInfo } = e2eUtils.getRequestParams(request);
                    if (url.indexOf('/watch/') !== -1) {
                        acc.push(brInfo);
                    }
                    return acc;
                }, []);
                chai.expect(
                    brInfos.length,
                    'we have caught at least two requests',
                ).to.be.at.least(2);
                chai.expect(
                    brInfos[0].pp || brInfos[1].pp,
                    'there is no PP var',
                ).to.be.undefined;
                chai.expect(
                    brInfos[0].pu || brInfos[1].pu,
                    'there is no PU var',
                ).to.be.undefined;
                chai.expect(
                    brInfos[0].zzlc || brInfos[1].zzlc,
                    'there is no ZZLC var',
                ).to.be.undefined;
            });
    });

    it('should add crossDomain vars if not EU and PP check', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/${options.counterId}`,
                                    count: 2,
                                    body: {
                                        settings: {
                                            pcs: '0',
                                            eu: 0,
                                        },
                                        userData: {},
                                    },
                                },
                            ],
                            function () {
                                const requests = [];
                                serverHelpers.onRequest(function (request) {
                                    requests.push(request);
                                });
                                const counter = new Ya.Metrika2({
                                    id: options.counterId,
                                });
                                setTimeout(() => {
                                    counter.reachGoal('random', {});
                                }, 1000);
                                setTimeout(() => {
                                    done(requests);
                                }, 1500);
                            },
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const brInfos = requests.reduce((acc, request) => {
                    const { url, brInfo } = e2eUtils.getRequestParams(request);
                    if (url.indexOf('/watch/') !== -1) {
                        acc.push(brInfo);
                    }
                    return acc;
                }, []);
                chai.expect(
                    brInfos.length,
                    'we have caught at least two requests',
                ).to.be.at.least(2);
                chai.expect(brInfos[1].cc, 'there is CC var').not.to.be
                    .undefined;
                // chai.expect(brInfos[1].pp, 'there is PP var').not.to.be
                //     .undefined;
                chai.expect(brInfos[1].pp, 'PP var is not empty').not.equals(
                    '',
                );
                chai.expect(brInfos[1].pu, 'there is PU var').not.to.be
                    .undefined;
                chai.expect(brInfos[1].zzlc, 'there is ZZLC var').not.to.be
                    .undefined;
            });
    });

    it.skip('PU (opener connection) check', function () {
        const localURL = `${e2eUtils.baseUrl}/test/crossDomain/crossDomainPU.hbs`;
        const counterIdChild = 67890;
        const childURL = localURL;
        return this.browser
            .url(localURL)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/`,
                                    count: 8,
                                    body: {
                                        settings: {
                                            pcs: '0',
                                            eu: 0,
                                        },
                                        userData: {},
                                    },
                                },
                            ],
                            function () {
                                localStorage.clear();
                                let child = null;
                                let counterChild = null;
                                const requests = [];
                                window._socket.on('request', function (r) {
                                    if (
                                        r.url.match(
                                            new RegExp(options.counterId),
                                        )
                                    ) {
                                        requests.push(r);
                                    }
                                });
                                const counter = new Ya.Metrika2({
                                    id: options.counterId,
                                });
                                setTimeout(() => {
                                    counter.reachGoal('random', {});
                                }, 500);
                                setTimeout(() => {
                                    window.addEventListener(
                                        'message',
                                        (e) => {
                                            try {
                                                const data = JSON.parse(e.data);
                                                if (data.url) {
                                                    requests.push(data);
                                                }
                                            } catch (err) {
                                                console.log(err);
                                            }
                                            if (requests.length === 3) {
                                                setTimeout(() => {
                                                    counterChild.reachGoal(
                                                        'random',
                                                        {},
                                                    );
                                                }, 500);
                                            }
                                            if (requests.length === 4) {
                                                try {
                                                    child.close();
                                                } catch (error) {
                                                    // empty
                                                }
                                                done(requests);
                                            }
                                        },
                                        false,
                                    );
                                    child = window.open(options.childURL);
                                    child.onload = function () {
                                        child._socket.on(
                                            'request',
                                            function (r) {
                                                if (
                                                    r.url.match(
                                                        new RegExp(
                                                            options.counterChild,
                                                        ),
                                                    )
                                                ) {
                                                    child.opener.postMessage(
                                                        JSON.stringify(r),
                                                        '*',
                                                    );
                                                }
                                            },
                                        );
                                        child._socket.on(
                                            'connect',
                                            function () {
                                                counterChild =
                                                    new child.Ya.Metrika2({
                                                        id: options.counterIdChild,
                                                    });
                                            },
                                        );
                                    };
                                }, 1000);
                            },
                        );
                    },
                    counterId,
                    counterIdChild,
                    childURL,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const brInfos = requests.reduce(
                    (acc, request) => {
                        const { url, brInfo } =
                            e2eUtils.getRequestParams(request);
                        if (url.indexOf(`/watch/${counterId}/1`) !== -1) {
                            if (brInfo.pu) {
                                acc.parentPU = brInfo.pu;
                            }
                        }
                        if (url.indexOf(`/watch/${counterIdChild}/1`) !== -1) {
                            if (brInfo.pu) {
                                acc.childPU = brInfo.pu;
                            }
                        }
                        return acc;
                    },
                    {
                        parentPU: undefined,
                        childPU: undefined,
                    },
                );
                chai.expect(brInfos.parentPU, 'parentPU').is.not.undefined;
                chai.expect(brInfos.childPU, 'childPU').is.not.undefined;
                chai.expect(brInfos.childPU, 'childPU').is.equal(
                    brInfos.parentPU,
                );
            });
    });

    it('ZZ (iframe) check', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/`,
                                    count: 2,
                                    body: {
                                        settings: {
                                            pcs: '0',
                                            eu: 0,
                                        },
                                        userData: {},
                                    },
                                },
                            ],
                            function () {
                                const requests = [];
                                serverHelpers.onRequest(function (request) {
                                    requests.push(request);
                                });
                                const counter = new Ya.Metrika2({
                                    id: options.counterId,
                                });
                                setTimeout(() => {
                                    done(false);
                                }, 4000);
                                window.addEventListener(
                                    'message',
                                    (e) => {
                                        try {
                                            const info = e.data.substr(0, 8);
                                            if (info === '__ym__zz') {
                                                requests.push({
                                                    url: 'iframe',
                                                    body: e.data.substr(8),
                                                });
                                            }
                                        } catch (err) {
                                            console.log(err);
                                        }
                                        setTimeout(() => {
                                            counter.reachGoal('random', {});
                                        }, 100);

                                        setTimeout(() => {
                                            done(requests);
                                        }, 1000);
                                    },
                                    false,
                                );
                            },
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const brInfos = requests.reduce(
                    (acc, request) => {
                        const { url, brInfo } =
                            e2eUtils.getRequestParams(request);
                        if (url.indexOf(`/watch/${counterId}/1`) !== -1) {
                            if (brInfo.zzlc) {
                                acc.parentZZ = brInfo.zzlc;
                            }
                        }
                        if (url.indexOf(`iframe`) !== -1) {
                            acc.childZZ = request.body;
                        }
                        return acc;
                    },
                    {
                        parentZZ: undefined,
                        childZZ: undefined,
                    },
                );
                chai.expect(brInfos.parentZZ, 'should be requests from counter')
                    .is.not.undefined;
                chai.expect(brInfos.childZZ, 'should be request from iframe').is
                    .not.undefined;
                chai.expect(brInfos.childZZ).is.equal(brInfos.parentZZ);
            });
    });
});
