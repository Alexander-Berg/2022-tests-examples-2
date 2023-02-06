const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('webvisor2', function () {
    const baseUrl = 'test/webvisor2/';
    const counterId = 123;

    const checkFocusData = function (browser, isProto) {
        return browser
            .timeoutsAsyncScript(15000)
            .url(`${baseUrl}windowfocus.hbs?${isProto ? '' : '_ym_debug=1'}`)
            .getText('h1')
            .then((innerText) => {
                const text = innerText;
                chai.expect(text).to.be.equal('Windowfocus page');
            })
            .then(
                e2eUtils.provideServerHelpers(browser, {
                    cb(serverHelpers, options, done) {
                        if (options.isProto) {
                            document.cookie = '_ym_debug=""';
                        }
                        window.req = [];
                        serverHelpers.onRequest(function (request) {
                            if (request.url.match(/webvisor\//)) {
                                window.req.push(request);
                            }
                        });
                        new Ya.Metrika2({
                            id: options.counterId,
                            webvisor: true,
                        });
                        done();
                    },
                    counterId,
                    isProto,
                }),
            )
            .pause(1000)
            .newWindow(`${baseUrl}webvisor.hbs`)
            .pause(1000)
            .switchTab()
            .pause(12000)
            .then(
                e2eUtils.provideServerHelpers(browser, {
                    cb(serverHelpers, options, done) {
                        done(window.req);
                    },
                }),
            )
            .then(e2eUtils.handleRequest(browser))
            .then(e2eUtils.getWebvisorData.bind(e2eUtils))
            .then((visorData) => {
                const events = visorData.filter(
                    (event) =>
                        event.type === 'event' &&
                        event.data &&
                        ['windowfocus', 'windowblur'].includes(event.data.type),
                );
                const [windowblur] = events;

                chai.expect(windowblur.data.type, 'windowblur').to.equal(
                    'windowblur',
                );
                // TODO после обновления вебдрайвера прочекать виндоуфоус, потому что он не триггерится тут
            });
    };

    beforeEach(function () {
        return this.browser
            .deleteCookie()
            .timeoutsAsyncScript(10000)
            .url(baseUrl)
            .executeAsync(function (done) {
                localStorage.clear();
                done();
            });
    });

    it('records windowfocus (json)', function () {
        return checkFocusData(this.browser, false);
    });

    it('records windowfocus (proto)', function () {
        return checkFocusData(this.browser, true);
    });
});
