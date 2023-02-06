import type {OpenPageOptions} from 'tests/e2e/config/commands/open-page';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Страница балковых действий', function () {
    async function openBulkPage(ctx: Hermione.TestContext, productIdentifier: number, options?: OpenPageOptions) {
        await ctx.browser.openPage(ROUTES.CLIENT.PRODUCTS, options);
        await ctx.browser.clickInto([`products-table-row_${productIdentifier}`, 'checkbox']);
        await ctx.browser.clickInto(['products-bottom-panel', 'bulk-edit'], {waitRender: true, waitNavigation: true});
    }

    it('Смена языка интерфейса на странице балковых действий (Россия)', async function () {
        await openBulkPage(this, 10000001);
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('ui-lang-select', {waitRender: true});
        await this.browser.clickInto(['ui-lang-select_dropdown-menu', 'en'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Показ модального окна при подготовке изменений балком', async function () {
        await openBulkPage(this, 10000001);
        await this.browser.clickInto('change-status');

        await this.browser.setNetworkConditions({latency: 2500, download_throughput: 25600, upload_throughput: 51200});

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorVisible('message-modal');
        await this.browser.assertImage('message-modal', {removeShadows: true});

        await this.browser.setNetworkConditions({}, 'No throttling');
    });

    it('Показ модального окна при применении изменений балком', async function () {
        await openBulkPage(this, 10000002);
        await this.browser.clickInto('change-status');
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('import-info-update');

        await this.browser.setNetworkConditions({latency: 2500, download_throughput: 25600, upload_throughput: 51200});

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorVisible('message-modal');
        await this.browser.assertImage('message-modal', {removeShadows: true});

        await this.browser.setNetworkConditions({}, 'No throttling');
    });
});
