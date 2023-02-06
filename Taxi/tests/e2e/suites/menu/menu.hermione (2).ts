import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Меню', function () {
    it('Клик в лого возвращает на страницу товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.clickInto('logo', {waitNavigation: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.PRODUCTS));
    });

    it('Сложить меню + разложить меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {noCookies: true});
        await this.browser.clickInto('sidebar-switcher', {waitRender: true});
        await this.browser.assertImage('sidebar');
        await this.browser.clickInto('sidebar-switcher', {waitRender: true});
        await this.browser.assertImage('sidebar');
    });
});
