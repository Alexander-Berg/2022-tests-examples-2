import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Шапка', function () {
    it('Страница товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.assertImage('header');
    });

    it('Можно изменить регион на Францию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {noCookies: true});

        await this.browser.clickInto('region-switcher', {waitRender: true});
        await this.browser.clickInto('FR', {waitNavigation: true, waitRender: true});

        await this.browser.assertImage('header');
    });

    it('Можно изменить язык интерфейса на английский', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {noCookies: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('ui-lang-select', {waitRender: true});
        await this.browser.clickInto('en', {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('header');
    });
});
