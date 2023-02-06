const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('inline proxy test', function () {
    const baseUrl = 'test/stackProxy/inlinePass.hbs';
    const counterId = 10;
    const counterId2 = 20;
    const counterId3 = 30;
    beforeEach(function () {
        return this.browser
            .timeoutsAsyncScript(10000)
            .url(baseUrl)
            .getText('body')
            .then((text) => {
                chai.expect(text).to.be.equal('inline proxy page');
            });
    });
    /* eslint-disable */
    it('understands witch constructor belongs counterID', function () {
        return (
            this.browser
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            serverHelpers.collectRequests(
                                700,
                                null,
                                options.defaultRequestRegEx,
                            );
                            window.ym = function () {
                                window.ym.a.push(arguments);
                            };
                            window.ym.a = [];
                            const insertCounter = (js, counterId) => {
                                const script = document.createElement('script');
                                script.src = `${js}?counterID=${counterId}`;
                                document.head.appendChild(script);
                                return script;
                            };
                            setTimeout(() => {
                                const metrika2Script = insertCounter(
                                    localJsSrc,
                                    options.counterId,
                                );
                                metrika2Script.onload = function () {
                                    ym(this.src, 'init', {
                                        webvisor: true,
                                    });
                                };
                                setTimeout(() => {
                                    const debugScript = insertCounter(
                                        watchJsSrc,
                                        options.counterId2,
                                    );
                                    debugScript.onload = function () {
                                        ym(this.src, 'init');
                                    };
                                    setTimeout(() => {
                                        const secondMertika2Script =
                                            insertCounter(
                                                localJsSrc,
                                                options.counterId3,
                                            );
                                        secondMertika2Script.onload =
                                            function () {
                                                ym(this.src, 'init', {
                                                    webvisor: false,
                                                });
                                            };
                                    }, 100);
                                }, 100);
                            }, 100);
                        },
                        counterId,
                        counterId2,
                        counterId3,
                        defaultRequestRegEx: e2eUtils.defaultRequestRegEx,
                    }),
                )
                /* eslint-enable */
                .then(e2eUtils.handleRequest(this.browser))
                .then(({ value: results }) => {
                    const requests = results.map(e2eUtils.getRequestParams);
                    const counters = requests.reduce((result, req) => {
                        result[req.counterId] = 1;
                        return result;
                    }, {});
                    chai.expect(Object.keys(counters)).to.be.lengthOf(3);
                    const vfList = requests.reduce((result, request) => {
                        result[request.brInfo.vf] = 1;
                        return result;
                    }, {});
                    chai.expect(Object.keys(vfList)).to.be.lengthOf(2);
                })
        );
    });
});
