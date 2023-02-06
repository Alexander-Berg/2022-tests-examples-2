import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Переходы на страницы по прямой ссылке (мастер категория)', function () {
    it('Поиск МК по прямой ссылке, Израиль', async function () {
        const search = 'отвергает';

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES, {
            region: 'il',
            queryParams: {search}
        });

        const url = new URL(await this.browser.getUrl());

        expect(url.pathname).to.match(new RegExp('il/categories/master'));
        expect(decodeURIComponent(url.searchParams.toString())).to.match(new RegExp(`search=${search}`));

        await this.browser.assertImage('base-layout');
    });

    it('Открыть МК по прямой ссылке, Великобритания', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(10), {region: 'gb'});
        await this.browser.assertImage('base-layout');
    });

    it('Открыть таблицу МК по прямой ссылке, Россия', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES, {region: 'ru'});
        await this.browser.assertImage('base-layout');
    });

    it('Открыть страницу создания МК по прямой ссылке, Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY, {region: 'fr'});
        await this.browser.assertImage('base-layout');
    });
});
