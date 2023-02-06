'use strict';

const {PAGEDATA} = require('../PAGEDATA');

const test404 = function (path = PAGEDATA.url.path) {
    hermione.only.notIn('chromeMobile', 'Десктопные тесты пропущены');
    it.skip('показывает ошибку в витрине на десктопе', async function() {
        await this.browser.yaOpenMorda({
            path: path,
            getParams: {
                'stream_id': 123
            },
            expectations: {
                ignoreErrorsSource: /console-api/,
                ignoreErrorsMessage: /(\/\/an\.yandex\.ru.*video-category-id)|(\/player\/123.json)/
            }
        });

        await this.browser.execute(function () {
            document.documentElement.className += ' font_loaded';
        });

        await this.browser.$(PAGEDATA.classNames.screens['404']).then(elem => elem.waitForDisplayed());
        await this.browser.$(PAGEDATA.classNames.screens.storefront).then(elem => elem.waitForExist());

        await this.browser.yaIgnoreElement([
            PAGEDATA.classNames.storefront.embed,
            PAGEDATA.classNames.storefront.top,
            PAGEDATA.classNames.storefront.feed,
            PAGEDATA.classNames.header.categories,
            PAGEDATA.classNames.sidemenu.toggles,
            PAGEDATA.classNames.sidemenu.blocks
        ]);

        await this.browser.yaAssertViewport('storefront', {
            ignoreElements: [
                PAGEDATA.classNames.header.searchInput
            ]
        });
    });

    hermione.only.in('chromeMobile', 'Тачевые тесты пропущены');
    it.skip('показывает ошибку в витрине на таче', async function() {
        await this.browser.yaOpenMorda({
            path: path,
            getParams: {
                'stream_id': 123
            },
            expectations: {
                ignoreErrorsSource: /console-api/,
                ignoreErrorsMessage: /(\/\/an\.yandex\.ru.*video-category-id)|(\/player\/123.json)/
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

        await this.browser.yaAssertViewport('storefront', {});
    });
};

module.exports = {
    test404
};
