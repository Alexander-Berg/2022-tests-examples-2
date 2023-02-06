const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Trigger event test', function () {
    const firstCounterId = 1234;
    const eventName = `yacounter${firstCounterId}inited`;
    const baseUrl = 'test/triggerEvent/triggerEvent.hbs';
    const globalKey = `yaCounter${firstCounterId}`;

    beforeEach(function () {
        return this.browser
            .deleteCookie()
            .timeoutsAsyncScript(10000)
            .url(baseUrl)
            .getText('body')
            .then((innerText) => {
                chai.expect('Trigger event page').to.be.equal(innerText);
            });
    });

    it('should trigger event when counter is initialized', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(_serverHelpers, options, done) {
                        document.addEventListener(
                            options.eventName,
                            function (e) {
                                done(e.type);
                            },
                        );

                        new Ya.Metrika2({
                            id: options.firstCounterId,
                            triggerEvent: true,
                        });
                    },
                    firstCounterId,
                    eventName,
                }),
            )
            .then(({ value }) => {
                chai.expect(value).to.be.equal(eventName);
            });
    });
    it('should not trigger event if triggerEvent is false', function () {
        const timeoutText = 'timeout';

        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(_serverHelpers, options, done) {
                        document.addEventListener(
                            options.eventName,
                            function (e) {
                                done(e.type);
                            },
                        );

                        new Ya.Metrika2({
                            id: options.firstCounterId,
                        });

                        setTimeout(function () {
                            done(options.timeoutText);
                        }, 1000);
                    },
                    firstCounterId,
                    eventName,
                    timeoutText,
                }),
            )
            .then(({ value }) => {
                chai.expect(value).to.be.equal(timeoutText);
            });
    });
    it('should trigger event when window.yaCounterXXXX already exists', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(_serverHelpers, options, done) {
                        document.addEventListener(
                            options.eventName,
                            function () {
                                done(window[options.globalKey]);
                            },
                        );

                        window[options.globalKey] = new Ya.Metrika2({
                            id: options.firstCounterId,
                            triggerEvent: true,
                        });
                    },
                    firstCounterId,
                    eventName,
                    globalKey,
                }),
            )
            .then(({ value: counterInstance }) => {
                chai.expect(counterInstance).to.exist;
                // проверяем на наличие популярных методов сч-ка:
                [
                    'addFileExtension',
                    'destruct',
                    'experiments',
                    'file',
                    'params',
                    'getClientID',
                    'hit',
                    'notBounce',
                ].forEach((method) => {
                    chai.expect(counterInstance[method]).to.exist;
                });
            });
    });
});
