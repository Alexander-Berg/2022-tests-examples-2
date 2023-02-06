import {describe, it} from 'tests/hermione.globals';

describe('Ошибка 500', function () {
    it('Страница 500-й ошибки – "Сервер не отвечает"', async function () {
        await this.browser.openPage('/test/server-error', {region: null});
        await this.browser.assertImage();
    });
});
