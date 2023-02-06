const chai = require('chai');
const e2eUtils = require('../../utils/index.js');
const { findNodeWithAttribute, baseUrl, clearBrowser } = require('./utils');

describe('webvisor2', function () {
    const counterId = 3928304;

    const checkScrollData = function (browser, isProto) {
        return browser
            .url(`${baseUrl}scroll.hbs?${isProto ? '' : '_ym_debug=1'}`)
            .getText('h1')
            .then((innerText) => {
                const text = innerText;
                chai.expect(text).to.be.equal('Scroll page');
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

                        setTimeout(() => {
                            document.querySelector(
                                '#scrollingInput',
                            ).scrollTop = 500;
                        }, 1500);

                        done();
                    },
                    counterId,
                    isProto,
                }),
            )
            .pause(1000)
            .scroll('#scrollingInput')
            .pause(6000)
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
                const events = visorData.filter(
                    (event) => event.type === 'event',
                );
                const target = findNodeWithAttribute(page, 'scrollingInput').id;
                const pageScrolls = events.filter(
                    (event) =>
                        event.data.type === 'scroll' && event.data.meta.page,
                );
                chai.expect(
                    pageScrolls.length,
                    'Only initial scroll and one page scroll',
                ).to.equal(2);
                const [initialScroll, pageScroll] = pageScrolls;
                chai.expect(
                    initialScroll.data.meta.x,
                    'initial scroll x',
                ).to.equal(0);
                chai.expect(
                    initialScroll.data.meta.y,
                    'initial scroll y',
                ).to.equal(0);

                const { pageHeight } = events.find(
                    (event) => event.data.type === 'resize',
                ).data.meta;
                const viewportHeight = page.data.meta.viewport.height;
                chai.expect(pageScroll.data.meta.y, 'page scroll y').to.equal(
                    pageHeight - viewportHeight,
                );
                chai.expect(pageScroll.data.meta.x, 'page scroll x').to.equal(
                    0,
                );

                const inputScroll = events.find(
                    (event) =>
                        event.data.type === 'scroll' && !event.data.meta.page,
                );
                chai.expect(inputScroll.data.meta.x, 'input scroll x').to.equal(
                    0,
                );
                chai.expect(inputScroll.data.meta.y, 'input scroll y').to.equal(
                    500,
                );
                chai.expect(
                    inputScroll.data.target,
                    'input scroll target',
                ).to.equal(target);
            });
    };

    beforeEach(function () {
        return clearBrowser(this.browser);
    });

    it('records scroll (json)', function () {
        return checkScrollData(this.browser, false);
    });

    it('records scroll (proto)', function () {
        return checkScrollData(this.browser, true);
    });
});
