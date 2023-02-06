const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('insertDebugScript', function () {
    const baseUrl = 'test/insertDebugScript/insertDebugScript.hbs';
    const DEBUG_URL_PARAM = '_ym_debug';
    const counterId = '20320';
    const resourceUrl = 'https://mc.yandex.ru/metrika/tag_debug.js';

    function testInsertDebugScript(
        debug = '',
        debugBuildVersion = 0,
        result = false,
    ) {
        return (
            this.browser
                .url(`${baseUrl}${debug && `?${DEBUG_URL_PARAM}=${debug}`}`)
                .getText('.content')
                .then((innerText) => {
                    chai.expect('Insert Debug Script page').to.be.equal(
                        innerText,
                    );
                })
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options, done) {
                            window.loadTagJs(options.debugBuildVersion);
                            window.ym(options.counterId, 'init');

                            setTimeout(done, 1000);
                        },
                        counterId,
                        debugBuildVersion,
                    }),
                )
                // check for script tag
                .execute(function () {
                    return Array.prototype.slice
                        .call(document.getElementsByTagName('script'))
                        .map((item) => item.src);
                })
                .then(({ value: scripts }) => {
                    chai.expect(
                        !!scripts.filter((src) => src === resourceUrl).length,
                    ).to.eq(result);
                })
        );
    }

    beforeEach(function () {
        return this.browser.deleteCookie().timeoutsAsyncScript(10000);
    });

    it('loads no script when a relevant debug URL parameter is not provided', function () {
        return testInsertDebugScript.call(this);
    });

    it('loads no script when a relevant debug URL parameter is provided but with wrong value', function () {
        return testInsertDebugScript.call(this, '1');
    });

    it('loads proper script when a relevant debug URL parameter is provided', function () {
        return testInsertDebugScript.call(this, '200500', 0, true);
    });

    it('loads proper script when a relevant cookie is provided', function () {
        return testInsertDebugScript.call(this, '', 25, true);
    });
});
