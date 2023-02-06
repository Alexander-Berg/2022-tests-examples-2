import type {OpenPageOptions} from 'tests/e2e/config/commands/open-page';
import {
    openChangeAttributesBulkPage,
    openChangeFrontCategoryBulkPage,
    openChangeMasterCategoryBulkPage,
    openChangeStatusBulkPage,
    selectAttribute
} from 'tests/e2e/helper/bulk';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import assertDefined from '@/src/utils/assert-defined';
import {assertString} from 'service/helper/assert-string';

describe('Обратный импорт - балк', function () {
    async function openProductHistoryPage(
        ctx: Hermione.TestContext,
        productIdentifier: number,
        options?: OpenPageOptions
    ) {
        await ctx.browser.openPage(ROUTES.CLIENT.PRODUCT(productIdentifier), options);
        await ctx.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await ctx.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
    }

    async function downloadReversedImport(ctx: Hermione.TestContext, selector: Hermione.Selector) {
        const getImportKeyFromUrl = async () => {
            const link = await ctx.browser.findByTestId(selector);
            const url = await link.getProperty('href');
            return assertDefined(assertString(url).split('/').pop());
        };

        const clickDownloadLink = async () => {
            await ctx.browser.clickInto(selector, {waitForClickable: true});
            await ctx.browser.waitForTestIdSelectorAriaEnabled(selector);
            await ctx.browser.pause(100); // Чтобы убедится что файл сохранился
        };

        const [importKey] = await Promise.all([getImportKeyFromUrl(), clickDownloadLink()]);
        return `/home/selenium/Downloads/reverse-import-${importKey}.xlsx`;
    }

    it('Обратное изменение статуса после смены через балк', async function () {
        await openChangeStatusBulkPage(this, [10000001, 10000006]);

        await this.browser.clickInto('status-inactive');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');

        await openProductHistoryPage(this, 10000001);
        const pathToFile = await downloadReversedImport(this, 'download-reverse-import-link');

        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(['import-upload', 'file-input'], pathToFile, {useBrowserFs: true});
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Обратное изменение мастер-категории после смены через балк', async function () {
        await openChangeMasterCategoryBulkPage(this, [10000004]);

        await this.browser.clickInto('mc_row_master_category_code_1_0', {waitForClickable: true});
        await this.browser.clickInto('mc_row_master_category_code_5_0', {waitForClickable: true});
        await this.browser.clickInto('mc_row_master_category_code_25_0', {waitForClickable: true});

        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');

        await openProductHistoryPage(this, 10000004);
        const pathToFile = await downloadReversedImport(this, 'download-reverse-import-link');

        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(['import-upload', 'file-input'], pathToFile, {useBrowserFs: true});
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Обратное изменение фронт-категории после смены через балк', async function () {
        await openChangeFrontCategoryBulkPage(this, [10000005], 'add');

        await this.browser.clickInto('fc_row_front_category_code_1_0', {waitForClickable: true});
        await this.browser.clickInto('fc_row_front_category_code_5_0', {waitForClickable: true});
        await this.browser.clickInto('fc_row_front_category_code_5_1', {waitForClickable: true});

        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');

        await openProductHistoryPage(this, 10000005);
        const pathToFile = await downloadReversedImport(this, 'download-reverse-import-link');

        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(['import-upload', 'file-input'], pathToFile, {useBrowserFs: true});
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Обратное изменение фронт-категории после удаления старой', async function () {
        await openChangeFrontCategoryBulkPage(this, [10000005], 'remove');

        await this.browser.clickInto('fc_row_front_category_code_1_2', {waitForClickable: true});
        await this.browser.clickInto('fc_row_front_category_code_7_2', {waitForClickable: true});
        await this.browser.clickInto('fc_row_front_category_code_7_3', {waitForClickable: true});

        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');

        await openProductHistoryPage(this, 10000005);
        const pathToFile = await downloadReversedImport(this, 'download-reverse-import-link');

        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(['import-upload', 'file-input'], pathToFile, {useBrowserFs: true});
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Обратное изменение атрибута после смены через балк', async function () {
        await openChangeAttributesBulkPage(this, [10000006]);

        await selectAttribute(this, 'longName');
        await this.browser.typeInto('longName_ru', 'foo-bar-baz');

        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');

        await openProductHistoryPage(this, 10000006);
        const pathToFile = await downloadReversedImport(this, 'download-reverse-import-link');

        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(['import-upload', 'file-input'], pathToFile, {useBrowserFs: true});
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });
});
