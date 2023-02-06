const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Informer', function () {
    const baseUrl = 'test/informer/informer.hbs';
    const selectors = {
        informerImage: '#informer-image',
        nonInformerImage: '#not-an-informer-image',
        container: '#test',
        popup: '#ym-informer',
        link: '#link-to-page',
    };
    const scriptNotFoudnErrorMessage =
        'informer script element not found on page';

    beforeEach(function () {
        return this.browser
            .deleteCookie()
            .timeoutsAsyncScript(10000)
            .url(baseUrl);
    });

    it('Should show informer on clicking the informer image', function () {
        return this.browser
            .click(selectors.informerImage)
            .waitForVisible(selectors.popup, 2000)
            .then(e2eUtils.handleRequest(this.browser));
    });

    it('loads the informer script', function () {
        return this.browser
            .click(selectors.informerImage)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const scripts = document.getElementsByTagName('script');
                        const informerScriptUrl =
                            'http://informer.yandex.ru/metrika/informer.js';
                        done(
                            Boolean(
                                // eslint-disable-next-line no-undef
                                findScriptFromURL(informerScriptUrl, scripts),
                            ),
                        );
                    },
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: informerScriptExists }) => {
                chai.expect(informerScriptExists, scriptNotFoudnErrorMessage).to
                    .be.true;
            });
    });

    it('Should hide informer', function () {
        return this.browser
            .click(selectors.informerImage)
            .click(selectors.informerImage)
            .click(selectors.informerImage)
            .waitForVisible(selectors.popup, 2000)
            .click(selectors.container)
            .waitForVisible(selectors.popup, 2000, true) // true означает что selectors.popup должен спрятаться
            .then(e2eUtils.handleRequest(this.browser));
    });

    it('Upon click NOT on the informer image should show popup only 1st time', function () {
        return this.browser
            .click(selectors.nonInformerImage)
            .waitForVisible(selectors.popup, 2000)
            .click(selectors.container)
            .waitForVisible(selectors.popup, 2000, true)
            .click(selectors.nonInformerImage)
            .waitForVisible(selectors.popup, 2000, true)
            .then(e2eUtils.handleRequest(this.browser));
    });

    it('Should not prevent default if click happened NOT on the informer image', function () {
        return this.browser
            .click(selectors.link)
            .getText('body')
            .then((innerText) => {
                chai.expect(
                    innerText,
                    "click on link didn't send the user to a new page, perhaps event.preventDefault() was called?",
                ).to.be.equal('Another page');
            });
    });

    it('UA feature', function () {
        return this.browser
            .url('test/informer/ua-informer.hbs')
            .click(selectors.informerImage)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const scripts = document.getElementsByTagName('script');
                        const informerScriptUrl =
                            'https://metrika-informer.com/metrika/informer.js';
                        done(
                            Boolean(
                                // eslint-disable-next-line no-undef
                                findScriptFromURL(informerScriptUrl, scripts),
                            ),
                        );
                    },
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: informerScriptExists }) => {
                chai.expect(informerScriptExists, scriptNotFoudnErrorMessage).to
                    .be.true;
            });
    });
});
