import {describe, expect, it} from 'tests/hermione.globals';

describe('Страница не найдено', function () {
    it('Некорректный регион', async function () {
        await this.browser.openPage('/', {region: 'unknown-region' as never});
        await this.browser.waitUntilRendered();
        expect(await this.browser.getUrl()).to.match(new RegExp(/\/unknown-region/));
        await this.browser.assertImage('base-layout');
    });

    it('Неизвестная страница', async function () {
        await this.browser.openPage('/unknown-path');
        await this.browser.waitUntilRendered();
        expect(await this.browser.getUrl()).to.match(new RegExp(/\/ru\/unknown-path/));
        await this.browser.assertImage('base-layout');
    });
});
