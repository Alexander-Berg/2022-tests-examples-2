import {describe, expect, it} from 'tests/hermione.globals';
import {URL} from 'url';

import {ROUTES} from '@/src/constants/routes';

describe('Переходы на страницы по прямой ссылке (инфо модель)', function () {
    it('Поиск инфомодели по прямой ссылке, Россия', async function () {
        const search = 'возлюбил';

        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS, {
            region: 'ru',
            queryParams: {search}
        });

        const url = new URL(await this.browser.getUrl());

        expect(url.pathname).to.match(new RegExp('ru/infomodels'));
        expect(decodeURIComponent(url.searchParams.toString())).to.match(new RegExp(`search=${search}`));

        await this.browser.assertImage('base-layout');
    });

    it('Открыть инфомодель по прямой ссылке, Россия', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(5), {region: 'ru'});
        await this.browser.assertImage('base-layout');
    });

    it('Открыть таблицу инфомоделей по прямой ссылке, Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS, {region: 'fr'});
        await this.browser.assertImage('base-layout');
    });

    it('Открыть страницу создания инфомодели по прямой ссылке, Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL, {region: 'il'});
        await this.browser.assertImage('base-layout');
    });
});
