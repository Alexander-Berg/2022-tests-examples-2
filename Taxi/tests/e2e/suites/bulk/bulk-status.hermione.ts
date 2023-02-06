import {openChangeStatusBulkPage} from 'tests/e2e/helper/bulk';
import {describe, it} from 'tests/hermione.globals';

describe('Балковые действия для статусов', function () {
    it('Изменить статус всех товаров', async function () {
        await openChangeStatusBulkPage(this, 'all');
        await this.browser.clickInto('status-inactive');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');
        await this.browser.clickInto('import-info-update', {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Изменить статус двух товаров на неактивный', async function () {
        await openChangeStatusBulkPage(this, [10000001, 10000006]);
        await this.browser.clickInto('status-inactive');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');
        await this.browser.clickInto('import-info-update', {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Изменить статус одного товара на активный', async function () {
        await openChangeStatusBulkPage(this, [10000002]);
        await this.browser.clickInto('status-active');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');
        await this.browser.clickInto('import-info-update', {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Страница массового изменения статуса', async function () {
        await openChangeStatusBulkPage(this, [10000001, 10000006]);

        await this.browser.assertImage('base-layout');
    });
});
