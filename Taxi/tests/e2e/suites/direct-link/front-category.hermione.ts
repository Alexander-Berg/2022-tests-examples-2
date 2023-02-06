import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Переходы на страницы по прямой ссылке (фронт категория)', function () {
    it('Поиск ФК по прямой ссылке, Франция', async function () {
        const search = 'dignissimos';

        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES, {
            region: 'fr',
            queryParams: {search}
        });

        const url = new URL(await this.browser.getUrl());

        expect(url.pathname).to.match(new RegExp('fr/categories/front'));
        expect(decodeURIComponent(url.searchParams.toString())).to.match(new RegExp(`search=${search}`));

        await this.browser.assertImage('base-layout');
    });

    it('Открыть ФК по прямой ссылке, Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(67), {region: 'il'});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('base-layout');
    });

    it('Открыть таблицу ФК по прямой ссылке, Великобритания', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES, {region: 'gb'});
        await this.browser.assertImage('base-layout');
    });

    it('Открыть страницу создания ФК по прямой ссылке, Россия', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY, {region: 'ru'});
        await this.browser.assertImage('base-layout');
    });
});
