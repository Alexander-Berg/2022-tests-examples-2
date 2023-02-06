const chai = require('chai');
const e2eUtils = require('../../utils/index.js');
const { findNodeWithAttribute, baseUrl, clearBrowser } = require('./utils');

describe('webvisor2', function () {
    const counterId = 123;

    const checkFocusData = function (browser, isProto) {
        return browser
            .url(`${baseUrl}focus.hbs?${isProto ? '' : '_ym_debug=1'}`)
            .getText('h1')
            .then((innerText) => {
                const text = innerText;
                chai.expect(text).to.be.equal('Focus page');
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
            .click('#firstFocus')
            .pause(100)
            .click('#secondFocus')
            .pause(4000)
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
                const page = visorData.find((event) => event.type === 'page');
                const focusEvents = visorData.filter(
                    (event) =>
                        event.type === 'event' && event.data.type === 'focus',
                );
                const firstTarget = findNodeWithAttribute(
                    page,
                    'firstFocus',
                ).id;
                const secondTarget = findNodeWithAttribute(
                    page,
                    'secondFocus',
                ).id;
                chai.expect(focusEvents.length, 'only 2 focuses').to.equal(2);
                chai.expect(focusEvents[0].data.target, 'first focus').to.equal(
                    firstTarget,
                );
                chai.expect(focusEvents[1].data.target, 'first focus').to.equal(
                    secondTarget,
                );
            });
    };

    beforeEach(function () {
        return clearBrowser(this.browser);
    });

    it('records focus (json)', function () {
        return checkFocusData(this.browser, false);
    });

    it('records focus (proto)', function () {
        return checkFocusData(this.browser, true);
    });
});
