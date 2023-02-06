'use strict';

const {PAGEDATA, getClassName} = require('../PAGEDATA');

const storefrontTest = function (path = PAGEDATA.url.path) {
    it.skip('открывается страница, включается правильный экран', async function() {
        await this.browser.yaOpenMorda({
            path: path,
            expectations: {
                ignoreErrorsMessage: /\/\/an\.yandex\.ru.*video-category-id/
            }
        });

        await this.browser.$(PAGEDATA.classNames.screens.storefront).then(elem => elem.waitForDisplayed());
        const streamClassName = await this.browser.$(PAGEDATA.classNames.stream).then(elem => elem.getAttribute('className'));
        streamClassName.should.have.string(getClassName(PAGEDATA.classNames.active.storefront));
    });

    hermione.skip.in('chromeMobile', 'Только десктоп', {silent: true});
    it.skip('Cтраница как-то выглядит - desktop', async function() {
        await this.browser.yaOpenMorda({
            path: path,
            expectations: {
                ignoreErrorsMessage: /\/\/an\.yandex\.ru.*video-category-id/
            }
        });

        await this.browser.execute(function () {
            document.documentElement.className += ' font_loaded';
        });

        await this.browser.$(PAGEDATA.classNames.screens.storefront).then(elem => elem.waitForDisplayed());
        await this.browser.$(PAGEDATA.classNames.screens.sidemenu).then(elem => elem.waitForDisplayed());

        await this.browser.yaIgnoreElement([
            PAGEDATA.classNames.storefront.embed,
            PAGEDATA.classNames.storefront.top,
            PAGEDATA.classNames.storefront.feed,
            PAGEDATA.classNames.header.categories,
            PAGEDATA.classNames.sidemenu.toggles,
            PAGEDATA.classNames.sidemenu.channels,
            PAGEDATA.classNames.sidemenu.blocks
        ]);

        await this.browser.yaAssertViewport('storefront', {
            ignoreElements: [
                PAGEDATA.classNames.header.searchInput
            ]
        });
    });

    hermione.only.in('chromeMobile', 'Только тач');
    it.skip('Cтраница как-то выглядит - touch', async function() {
        await this.browser.yaOpenMorda({
            path: path,
            expectations: {
                ignoreErrorsMessage: /\/\/an\.yandex\.ru.*video-category-id/
            }
        });

        await this.browser.execute(function () {
            document.documentElement.className += ' font_loaded';
        });

        await this.browser.$(PAGEDATA.classNames.screens.storefront).then(elem => elem.waitForDisplayed());

        await this.browser.yaIgnoreElement([
            PAGEDATA.classNames.storefront.embed,
            PAGEDATA.classNames.storefront.top,
            PAGEDATA.classNames.storefront.feed,
            PAGEDATA.classNames.header.categories
        ]);

        await this.browser.assertView('storefront', 'body');
    });

};

module.exports = {
    storefrontTest
};

