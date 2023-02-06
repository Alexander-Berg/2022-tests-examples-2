const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Yan e2e test', function () {
    const baseUrl = 'test/yan/yan.hbs';
    const adId = Math.floor(Math.random() * 1000);
    const input = {
        counterId: 12312,
        adId,
        params: {
            adSessionID: adId,
        },
    };
    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000).deleteCookie();
    });
    it('should send params from children iframe', function () {
        return this.browser
            .url('test/yan/yanFrame.hbs')
            .getText('body')
            .then((innerText) => {
                chai.expect(innerText).to.be.equal('Yan frame');
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        new Ya.Metrika2({
                            id: 5,
                        });
                        new Ya.Metrika2({
                            id: 4,
                        });
                        serverHelpers.collectRequests(200);
                        const iframe = document.getElementById('frame');
                        let iframeWindow;
                        try {
                            iframeWindow = iframe.contentWindow;
                        } catch (e) {
                            return;
                        }
                        setTimeout(function () {
                            iframeWindow.postMessage(
                                JSON.stringify({
                                    ymetrikaEvent: {
                                        type: 'params',
                                        parent: 1,
                                        data: options.params,
                                    },
                                }),
                                '*',
                            );
                        }, 50);
                    },
                    ...input,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: results }) => {
                let paramsCounter = 0;
                results.forEach((request) => {
                    const { brInfo, siteInfo } =
                        e2eUtils.getRequestParams(request);
                    if (!brInfo.pa) {
                        return;
                    }
                    paramsCounter += 1;
                    chai.expect(siteInfo).to.be.deep.equal(input.params);
                });
                chai.expect(paramsCounter).to.be.equal(2);
            });
    });
    it('should send params after push to data layer, only for one counter', function () {
        return this.browser
            .url('test/yan/yanAfter.hbs')
            .getText('body')
            .then((innerText) => {
                chai.expect(innerText).to.be.equal('Yan page');
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(200);
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                        new Ya.Metrika2({
                            id: options.counterId + 1,
                        });
                        window.Ya._metrika.dataLayer.push({
                            ymetrikaEvent: {
                                type: 'params',
                                counter: options.counterId,
                                data: options.params,
                            },
                        });
                    },
                    ...input,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: results }) => {
                let paramsCounter = 0;
                results.forEach((request) => {
                    const { brInfo, siteInfo } =
                        e2eUtils.getRequestParams(request);
                    if (!brInfo.pa) {
                        return;
                    }
                    paramsCounter += 1;
                    chai.expect(siteInfo).to.be.deep.equal(input.params);
                });
                chai.expect(paramsCounter).to.be.equal(1);
            });
    });
    it('should send params after push to data layer', function () {
        return this.browser
            .url('test/yan/yanAfter.hbs')
            .getText('body')
            .then((innerText) => {
                chai.expect(innerText).to.be.equal('Yan page');
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(200);
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                        new Ya.Metrika2({
                            id: options.counterId + 1,
                        });
                        window.Ya._metrika.dataLayer.push({
                            ymetrikaEvent: {
                                type: 'params',
                                data: options.params,
                            },
                        });
                    },
                    ...input,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: results }) => {
                let paramsCounter = 0;
                results.forEach((request) => {
                    const { brInfo, siteInfo } =
                        e2eUtils.getRequestParams(request);
                    if (!brInfo.pa) {
                        return;
                    }
                    paramsCounter += 1;
                    chai.expect(siteInfo).to.be.deep.equal(input.params);
                });
                chai.expect(paramsCounter).to.be.equal(2);
            });
    });
    it('should send params if dataLayer is not empty', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then((innerText) => {
                chai.expect(innerText).to.be.equal('Yan page');
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        window.Ya = {};
                        const ya = window.Ya;
                        ya._metrika = {};
                        ya._metrika.dataLayer = [
                            {
                                ymetrikaEvent: {
                                    type: 'params',
                                    data: options.params,
                                },
                            },
                        ];
                        const script = window.initCounterFromLocalJs();
                        script.onload = function () {
                            serverHelpers.collectRequests(200);
                            new Ya.Metrika2({
                                id: options.counterId,
                            });
                            new Ya.Metrika2({
                                id: options.counterId + 1,
                            });
                        };
                    },
                    ...input,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: results }) => {
                let paramsCounter = 0;
                results.forEach((request) => {
                    const { brInfo, siteInfo } =
                        e2eUtils.getRequestParams(request);
                    if (!brInfo.pa) {
                        return;
                    }
                    paramsCounter += 1;
                    chai.expect(siteInfo).to.be.deep.equal(input.params);
                });
                chai.expect(paramsCounter).to.be.equal(2);
            });
    });
});
