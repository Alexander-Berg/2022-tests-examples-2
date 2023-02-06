const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Remote Control', function () {
    const baseUrl = 'test/remoteControl/remoteControl.hbs';
    const expectedScriptUrl =
        'https://yastatic.net/s3/metrika/_/sIQtYfSNmxJiDSvoOuumD7_OuDs.js';

    beforeEach(function () {
        return this.browser
            .deleteCookie()
            .url(baseUrl)
            .timeoutsAsyncScript(10000);
    });

    it('Should create an iframe when the message of the correct format is sent', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const sameOriginIframe =
                            document.getElementById('sameOriginIframe');
                        const iframeWindow = sameOriginIframe.contentWindow;

                        iframeWindow.addEventListener('message', function (e) {
                            let data = null;

                            try {
                                data = JSON.parse(e.data);
                            } catch (_) {
                                /* ignoramus */
                            }

                            if (!data || data.action !== 'appendremote') {
                                return;
                            }

                            /* код внизу должен отработать в конце Event Loop-a. Т.к. после этого Event Handler-a есть
                            еще один, который должен отработать ( это onMessage из remoteControl.ts ), юзаем setTimeout */
                            setTimeout(function () {
                                // eslint-disable-next-line no-undef
                                done(hasIframeBeenInserted(iframeWindow));
                            });
                        });

                        iframeWindow.postMessage(
                            JSON.stringify({
                                action: 'appendremote',
                                resource:
                                    'https://yastatic.net/s3/metrika/_/sIQtYfSNmxJiDSvoOuumD7_OuDs.js',
                                id: '0.fliljnaqlfe',
                                initMessage: '0.z443i1dizsd',
                                inpageMode: 'clickmap',
                            }),
                            '*',
                        );
                    },
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: hasIframeBeenInserted }) => {
                chai.expect(
                    hasIframeBeenInserted,
                    "iframe wasn't inserted for some reason",
                ).to.be.true;
            });
    });

    it('Should not create an iframe in case the message is of invalid format', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const sameOriginIframe =
                            document.getElementById('sameOriginIframe');
                        const iframeWindow = sameOriginIframe.contentWindow;
                        const invalidActionName = 'action?!*&0';

                        iframeWindow.addEventListener('message', function (e) {
                            let data = null;

                            try {
                                data = JSON.parse(e.data);
                            } catch (_) {
                                /* ignoramus */
                            }

                            if (!data || data.action !== invalidActionName) {
                                return;
                            }

                            setTimeout(function () {
                                // eslint-disable-next-line no-undef
                                done(hasIframeBeenInserted(iframeWindow));
                            });
                        });

                        iframeWindow.postMessage(
                            JSON.stringify({
                                action: invalidActionName,
                                resource:
                                    'https://yastatic.net/s3/metrika/_/sIQtYfSNmxJiDSvoOuumD7_OuDs.js',
                            }),
                            '*',
                        );
                    },
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: hasIframeBeenInserted }) => {
                chai.expect(
                    hasIframeBeenInserted,
                    "iframe shouldn't have been inserted",
                ).to.be.false;
            });
    });

    it('Should insert a script inside iframe element', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const sameOriginIframe =
                            document.getElementById('sameOriginIframe');
                        const iframeWindow = sameOriginIframe.contentWindow;

                        iframeWindow.postMessage(
                            JSON.stringify({
                                action: 'appendremote',
                                resource:
                                    'https://yastatic.net/s3/metrika/_/sIQtYfSNmxJiDSvoOuumD7_OuDs.js',
                                id: '0.fliljnaqlfe',
                                initMessage: '0.z443i1dizsd',
                                inpageMode: 'clickmap',
                            }),
                            '*',
                        );

                        iframeWindow.addEventListener('message', function (e) {
                            let data = null;

                            try {
                                data = JSON.parse(e.data);
                            } catch (_) {
                                /* ignoramus */
                            }

                            if (!data || data.action !== 'appendremote') {
                                return;
                            }

                            setTimeout(function () {
                                const remoteIframeElem =
                                    iframeWindow._ym__remoteIframeEl;
                                const scriptSrcs = [];
                                const scripts =
                                    remoteIframeElem.contentDocument.getElementsByTagName(
                                        'script',
                                    );

                                for (let i = 0; i < scripts.length; i += 1) {
                                    const script = scripts[i];
                                    if (script.src) {
                                        scriptSrcs.push(script.src);
                                    }
                                }

                                done(scriptSrcs);
                            });
                        });
                    },
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: scriptSrcs }) => {
                chai.expect(scriptSrcs).to.include(expectedScriptUrl);
            });
    });
});
