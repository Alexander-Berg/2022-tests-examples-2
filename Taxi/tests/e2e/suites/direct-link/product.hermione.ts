import {chooseMasterCategory} from 'tests/e2e/suites/product/util';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Переходы на страницы по прямой ссылке (товар)', function () {
    it('Поиск товара по прямой ссылке, Израиль', async function () {
        const code = 'shortNameLoc';
        const values = 'aperiam';
        const rule = 'contain';

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'il',
            queryParams: {
                filters: {
                    [code]: {rule, values}
                }
            }
        });

        const url = new URL(await this.browser.getUrl());

        expect(url.pathname).to.match(new RegExp('il/products'));
        expect(decodeURIComponent(url.searchParams.toString())).to.match(
            new RegExp(`filters\\[${code}\\]\\[rule\\]=${rule}&filters\\[${code}\\]\\[values\\]=${values}`)
        );

        await this.browser.assertImage('base-layout');
    });

    it('Открыть товар по прямой ссылке, Россия', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000003), {region: 'ru'});
        await this.browser.assertImage('base-layout');
    });

    it('Открыть таблицу товаров по прямой ссылке, Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'fr'});
        await this.browser.assertImage('base-layout');
    });

    it('Открыть страницу создания товара по прямой ссылке, Великобритания', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS_CREATE, {region: 'gb'});
        await chooseMasterCategory(this.browser, 'GB');
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });
});
