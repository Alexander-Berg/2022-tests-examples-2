const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Yandex gdpr test', function () {
    const location = 'https://yandex.ru/test/gdpr/';
    const baseUrl = `${location}gdpr.hbs`;
    const counterId = 20302;
    beforeEach(function () {
        return this.browser
            .timeoutsAsyncScript(10000)
            .url(baseUrl)
            .execute(function () {
                localStorage.clear();
                localStorage.setItem('_ym_synced', '{"SYNCED_ADM":9999999999}');
                document.cookie = '_ym_isad=2';
            });
    });
    it('should disable checks if option was provided', function () {
        return this.browser
            .url(baseUrl)
            .deleteCookie('gdpr')
            .getText('body')
            .then((innerText) => {
                chai.expect('yandex page').to.be.equal(innerText);
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        document.cookie = 'gdpr=1';
                        serverHelpers.collectRequests(1000);
                        new Ya.Metrika2({
                            yaDisableGDPR: true,
                            id: options.counterId,
                        });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const req = requests.map(e2eUtils.getRequestParams);
                const counters = req.map((e) => e.counterId);
                chai.expect(counters).to.include(`${counterId}`);
                chai.expect(counters).to.not.include(`3`);
            });
    });
    it('should find yandex page in iframe', function () {
        return this.browser
            .url(`${location}gdprIframe.hbs`)
            .deleteCookie('gdpr')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb: function onExec(serverHelpers, options, done) {
                        const awaitLoad = (cb) => {
                            if (
                                window.loadFrame &&
                                window.myiframe.contentWindow.Ya
                            ) {
                                return cb();
                            }
                            setTimeout(() => awaitLoad(cb), 100);
                            return undefined;
                        };
                        const onServerMess = () => {
                            const child = window.myiframe.contentWindow;
                            window.allReq = [];
                            serverHelpers.onRequest((req) => {
                                window.allReq.push(req);
                            });
                            window.Ya.Metrika2(options.counterId + 1);
                            setTimeout(() => {
                                child._socket.on('request', (req) => {
                                    setTimeout(() => {
                                        done(child.Ya._metrika.dataLayer);
                                    }, 500);
                                    window.allReq.push(req);
                                });
                                child.localStorage.clear();
                                child.Ya.Metrika2(options.counterId);
                            }, 100);
                        };
                        setTimeout(done, 2500);
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/3`,
                                    body: {
                                        settings: {
                                            eu: 1,
                                        },
                                    },
                                    count: 2,
                                },
                            ],
                            function () {
                                awaitLoad(onServerMess);
                            },
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                chai.expect(
                    requests.map((e) => e.ymetrikaEvent.type)[0],
                ).to.be.equal('5');
                return this.browser.getCookie('gdpr_popup');
            })
            .then((gdprPopup) => {
                chai.expect(gdprPopup.value).to.be.equal('1');
            })
            .click('[data-id="button-all"]')
            .execute(function () {
                return [
                    window.Ya._metrika.dataLayer,
                    window.myiframe.contentWindow.Ya._metrika.dataLayer,
                ];
            })
            .then(({ value: requests }) => {
                const [parent, child] = requests;
                const getType = (e) => e.ymetrikaEvent.type;
                const parentTypes = parent.map(getType).join(',');
                const childTypes = child.map(getType).join(',');
                chai.expect(parentTypes).to.be.equal(
                    '7,10,GDPR-ok,GDPR-ok-view-default',
                );
                chai.expect(childTypes).to.be.equal('5');
            })
            .pause(1000)
            .execute(function () {
                return window.allReq;
            })
            .then(({ value: requests }) => {
                const reqList = requests.map(e2eUtils.getRequestParams);
                const uniqHid = reqList.reduce((acc, req) => {
                    const {
                        brInfo: { rn },
                    } = req;
                    if (!acc[rn]) {
                        acc[rn] = req;
                    }
                    return acc;
                }, {});
                const requestList = Object.values(uniqHid);
                const counters = requestList.map((e) => e.counterId);
                const pageViews = requestList
                    .map((e) => e.brInfo && e.brInfo.pv)
                    .filter(Boolean);
                chai.expect(counters).to.include('3');
                chai.expect(counters).to.include(`${counterId}`);
                chai.expect(counters).to.include(`${counterId + 1}`);
                chai.expect(pageViews).lengthOf(4);
                return this.browser.getCookie('gdpr_popup');
            })
            .then((gdprPopup) => {
                chai.expect(gdprPopup).to.be.equal(null);
            });
    });
    it('should find yandex page', function () {
        return this.browser
            .url(baseUrl)
            .deleteCookie('gdpr')
            .getText('body')
            .then((innerText) => {
                chai.expect('yandex page').to.be.equal(innerText);
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb: function onExec(serverHelpers, options) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/3`,
                                    body: {
                                        settings: {
                                            eu: 1,
                                        },
                                    },
                                    count: 1,
                                },
                            ],
                            function () {
                                window.allReq = [];
                                serverHelpers.collectRequests(1000);
                                serverHelpers.onRequest(function (req) {
                                    window.allReq.push(req);
                                });
                                new Ya.Metrika2(options.counterId);
                            },
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const req = requests.map(e2eUtils.getRequestParams);
                chai.expect(req).lengthOf(1);
                const [first] = req;
                chai.expect(first.counterId).to.be.equal('3');
                return this.browser.getCookie('gdpr_popup');
            })
            .then((gdprPopup) => {
                chai.expect(gdprPopup.value).to.be.equal('1');
            })
            .click('[data-id="button-all"]')
            .execute(function () {
                return window.Ya._metrika.dataLayer;
            })
            .then(({ value: requests }) => {
                const types = requests.map((e) => e.ymetrikaEvent.type);
                chai.expect(types.join(',')).to.be.equal(
                    '7,10,GDPR-ok,GDPR-ok-view-default',
                );
            })
            .executeAsync(function (done) {
                setTimeout(function () {
                    done(window.allReq);
                }, 200);
            })
            .then(({ value: requests }) => {
                const req = requests.map(e2eUtils.getRequestParams);
                const counters = req.map((e) => e.counterId);
                const pageViews = req
                    .map((e) => e.brInfo && e.brInfo.pv)
                    .filter(Boolean);
                chai.expect(counters).to.include('3');
                chai.expect(counters).to.include(`${counterId}`);
                chai.expect(pageViews).lengthOf(2);
                req.forEach((e) => {
                    if (e.counterId === `${counterId}`) {
                        chai.expect(e.telemetry.gdpr).to.be.equal(
                            '7,10,0,19-0',
                        );
                        chai.expect(e.brInfo.gdpr).to.be.equal('7,10,0,19-0');
                    }
                    if (e.counterId === `3`) {
                        chai.expect(e.brInfo.gdpr).to.be.equal('');
                    }
                });

                const paramsReq = requests
                    .map(e2eUtils.getRequestParams)
                    .find(({ brInfo }) => brInfo.pa);
                chai.expect(paramsReq).to.be.ok;
                chai.expect(paramsReq.siteInfo).to.be.deep.equal({
                    gdpr: ['ok', 'ok-default'],
                });

                return this.browser.getCookie('gdpr_popup');
            })
            .then((gdprPopup) => {
                chai.expect(gdprPopup).to.be.equal(null);
            });
    });
});
