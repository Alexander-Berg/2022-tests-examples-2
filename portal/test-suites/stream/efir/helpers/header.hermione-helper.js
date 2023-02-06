'use strict';

const {PAGEDATA, getClassName} = require('../PAGEDATA');

const chai = require('chai');
const assert = chai.assert;

const headerTest = function (path = PAGEDATA.url.path) {
    hermione.skip.in('chromeMobile', 'Только десктоп', {silent: true});

    it.skip('прокликивание категорий', async function () {
        let tabItemSelector = PAGEDATA.classNames.header.tabs.item;

        await this.browser.yaOpenMorda({
            path: path,
            expectations: {
                ignoreErrorsMessage: /\/\/an\.yandex\.ru.*video-category-id/
            }
        });

        await this.browser.execute(function () {
            document.documentElement.className += ' font_loaded';
        });

        let categories = await this.browser.$$(tabItemSelector);

        for (let i = 1; i < categories.length; i++) {
            const data = {};

            await this.browser.execute(function (categories, tab) {
                // скроллим, чтобы могли покликать
                document.querySelector(categories).parentNode.scrollLeft = document.querySelector(tab).offsetLeft;
            }, PAGEDATA.classNames.header.categories, tabItemSelector + ':nth-child(' + i + ')');

            await this.browser.$(tabItemSelector + ':nth-child(' + i + ')').then(elem => elem.click());
            const cls = await this.browser.$(tabItemSelector + ':nth-child(' + i + ')').then(elem => elem.getAttribute('class'));
            assert.include(cls, getClassName(PAGEDATA.classNames.header.tabs.active), 'вкладка не активна');

            const active = await this.browser.$(tabItemSelector + ':nth-child(' + i + ')').then(elem => elem.getAttribute('data-active'));
            data.active = active;

            const category = await this.browser.$(tabItemSelector + ':nth-child(' + i + ')').then(elem => elem.getAttribute('data-category'));
            data.category = category;

            const url = await this.browser.getUrl();
            if (data.active === 'storefront') {
                return;
            }

            assert.include(url, data.active, 'url не содержит корректный stream_active');

            if (data.category) {
                assert.include(url, data.category, 'url не содержит корректный stream_category');
            }
        }
    });
};

module.exports = {
    headerTest
};
