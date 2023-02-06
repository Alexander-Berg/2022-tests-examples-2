import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Переходы на страницы по прямой ссылке (импорт)', function () {
    it('Открыть страницу импорта по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS, {region: 'gb'});
        await this.browser.assertImage('base-layout');
    });
});
