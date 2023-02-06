const chai = require('chai');
const e2eUtils = require('../../utils/index.js');
const { baseUrl, clearBrowser } = require('./utils');

describe('webvisor2', function () {
    const counterId = 10230493;

    const somewhatEqual = (a, b) => {
        return a + 50 >= b && a - 50 <= b;
    };
    const checkResizeData = function (browser, isProto) {
        return browser
            .setViewportSize({ width: 1000, height: 1000 })
            .url(`${baseUrl}resize.hbs?${isProto ? '' : '_ym_debug=1'}`)
            .getText('h1')
            .then((innerText) => {
                const text = innerText;
                chai.expect(text).to.be.equal('Resize page');
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
            .setViewportSize({ width: 300, height: 200 })
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
                const events = visorData.filter(
                    (event) =>
                        event.type === 'event' && event.data.type === 'resize',
                );
                const [initialResize, resize] = events;
                chai.expect(
                    initialResize.stamp,
                    'initial resize has 0 stamp',
                ).to.equal(0);
                chai.assert(
                    somewhatEqual(initialResize.data.meta.height, 1000),
                    'initial resize height',
                );
                chai.assert(
                    somewhatEqual(initialResize.data.meta.width, 1000),
                    'initial resize width',
                );

                chai.assert(
                    somewhatEqual(resize.data.meta.height, 200),
                    'resize height',
                );
                chai.assert(
                    somewhatEqual(resize.data.meta.width, 300),
                    'resize width',
                );
            });
    };

    beforeEach(function () {
        return clearBrowser(this.browser);
    });

    it('records resize (proto)', function () {
        return checkResizeData(this.browser, true);
    });

    it('records resize (json)', function () {
        return checkResizeData(this.browser, false);
    });
});
