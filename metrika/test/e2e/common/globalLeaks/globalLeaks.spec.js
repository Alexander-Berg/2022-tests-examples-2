const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Global Leaks e2e test', function () {
    const baseUrl = 'test/globalLeaks/globalLeaks.hbs';
    const yandexNamespace = 'Ya';
    const metrikaNamespace = '_metrika';
    const metrikaConstructor = 'Metrika2';
    const counterId = 26302566;

    beforeEach(function () {
        return this.browser.deleteCookie().timeoutsAsyncScript(10000);
    });

    it('should exists Metrika namespace', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(onRequest, options, done) {
                        const ctxKeysBeforeCounterInit = Object.keys(window);
                        // eslint-disable-next-line no-undef
                        const script = initCounterFromLocalJs();
                        script.onload = function () {
                            const ctxKeysAfterCounterInit = Object.keys(window);
                            done({
                                ctxKeysBeforeCounterInit,
                                ctxKeysAfterCounterInit,
                                [options.yandexNamespace]:
                                    window[options.yandexNamespace],
                            });
                        };
                    },
                    counterId,
                    yandexNamespace,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: ctx }) => {
                const { ctxKeysBeforeCounterInit, ctxKeysAfterCounterInit } =
                    ctx;
                const diffCtxKeys =
                    ctxKeysAfterCounterInit.length -
                    ctxKeysBeforeCounterInit.length;

                chai.expect(diffCtxKeys).to.be.equal(1);
                chai.expect(ctxKeysBeforeCounterInit).to.not.includes(
                    yandexNamespace,
                );
                chai.expect(ctxKeysAfterCounterInit).to.includes(
                    yandexNamespace,
                );

                chai.expect(ctx).to.have.property(yandexNamespace);
                chai.expect(ctx[yandexNamespace]).to.have.property(
                    metrikaNamespace,
                );
                chai.expect(ctx[yandexNamespace]).to.have.property(
                    metrikaConstructor,
                );
            });
    });

    it('should exists counter in Metrika namespace', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(onRequest, options, done) {
                        // eslint-disable-next-line no-undef
                        const script = initCounterFromLocalJs();
                        script.onload = function () {
                            const yandexNamespaceVal = options.yandexNamespace;
                            const metrikaNamespaceVal =
                                options.metrikaNamespace;

                            const ctxCounterBeforeInit =
                                window[yandexNamespaceVal][metrikaNamespaceVal]
                                    .counters || null;

                            new Ya.Metrika2({ id: options.counterId });

                            done({
                                ctxCounterBeforeInit,
                                ctxCounterAfterInit:
                                    window[yandexNamespaceVal][
                                        metrikaNamespaceVal
                                    ].counters,
                            });
                        };
                    },
                    counterId,
                    yandexNamespace,
                    metrikaNamespace,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(
                ({ value: { ctxCounterBeforeInit, ctxCounterAfterInit } }) => {
                    chai.expect(ctxCounterBeforeInit).to.be.null;
                    chai.expect(ctxCounterAfterInit[`${counterId}:0`]).to.be.ok;
                },
            );
    });
});
