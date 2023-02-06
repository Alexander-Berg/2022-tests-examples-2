import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Переходы на страницы по прямой ссылке (атрибут)', function () {
    it('Поиск атрибута по прямой ссылке, Россия', async function () {
        const search = 'штрихкод';

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES, {
            region: 'ru',
            queryParams: {search}
        });

        const url = new URL(await this.browser.getUrl());

        expect(url.pathname).to.match(new RegExp('ru/attributes'));
        expect(decodeURIComponent(url.searchParams.toString())).to.match(new RegExp(`search=${search}`));

        await this.browser.assertImage('base-layout');
    });

    it('Открыть атрибут по прямой ссылке, Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(1), {region: 'fr'});
        await this.browser.assertImage('base-layout');
    });

    it('Открыть таблицу атрибутов по прямой ссылке, Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES, {region: 'il'});
        await this.browser.assertImage('base-layout');
    });

    it('Открыть страницу создания атрибута по прямой ссылке, Великобритания', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE, {region: 'gb'});
        await this.browser.assertImage('base-layout');
    });
});
