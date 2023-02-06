const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('webvisor2', function () {
    describe('eof', function () {
        const pageUrl = 'test/webvisor2/eof.hbs';

        const checkEOFEvent = function (browser, isProto, pauseBeforeReload) {
            const searchParams = isProto ? '' : '?_ym_debug=1';

            return browser
                .timeoutsAsyncScript(15000)
                .url(`${pageUrl}${searchParams}`)
                .then(
                    e2eUtils.provideServerHelpers(browser, {
                        cb(serverHelpers, options, done) {
                            const id = Math.random().toString().slice(2);
                            document.cookie = `forceIO=yandexCookie${id}; path=/;`;

                            new Ya.Metrika2({
                                id: 123,
                                webvisor: true,
                            });

                            done(true);
                        },
                    }),
                )
                .pause(5000) // ждем пока отправится страница
                .click('.title')
                .pause(pauseBeforeReload)
                .url(`${pageUrl}${searchParams}`)
                .then(
                    e2eUtils.provideServerHelpers(browser, {
                        cb(serverHelpers, options, done) {
                            window.requests = [];
                            serverHelpers.onRequest(function (request) {
                                window.requests.push(request);
                            }, options.regexp.webvisorRequestRegEx);
                            done(true);
                        },
                    }),
                )
                .pause(1000)
                .execute(function () {
                    return window.requests;
                })
                .then(e2eUtils.getWebvisorData.bind(e2eUtils))
                .then((visorData) => {
                    const pageVisit = visorData.find(
                        (event) => event.type === 'page',
                    );

                    const titleClick = visorData.find(
                        (event) =>
                            event.type === 'event' &&
                            event.data &&
                            event.data.type === 'click',
                    );

                    const eofEvents = visorData.filter(
                        (event) =>
                            event.type === 'event' &&
                            event.data &&
                            event.data.type === 'eof',
                    );

                    // basic events are recorded and sent
                    chai.expect(pageVisit, 'page visit event').to.be.not
                        .undefined;
                    chai.expect(titleClick, 'title click visit event').to.be.not
                        .undefined;
                    // page close event is sent before context is lost
                    chai.expect(eofEvents.length, 'two "eof" events').to.equal(
                        2,
                    );
                });
        };

        beforeEach(function () {
            return this.browser.deleteCookie();
        });

        it('records two "eof" events on page close after other events settled (json)', function () {
            return checkEOFEvent(this.browser, false, 5000);
        });

        it('records two "eof" events on page close after other events settled (proto)', function () {
            return checkEOFEvent(this.browser, true, 5000);
        });

        it('records two "eof" events on page close when other events are in queue (json)', function () {
            return checkEOFEvent(this.browser, false, 0);
        });

        it('records two "eof" events on page close when other events are in queue (proto)', function () {
            return checkEOFEvent(this.browser, true, 0);
        });
    });
});
