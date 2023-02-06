import type {OpenPageOptions} from 'tests/e2e/config/commands/open-page';
import getFixturePath from 'tests/e2e/utils/fixture';
import makeDataTestIdSelector from 'tests/e2e/utils/make-data-test-id-selector';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {DbTable} from '@/src/entities/const';
import assertDefined from '@/src/utils/assert-defined';
import {assertString} from 'service/helper/assert-string';

describe('Обратный импорт - импорт', function () {
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

    it('Обратное изменение свойств товара после изменений через интерфейс', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('change-product-parameters-for-reversed-import.xlsx')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000008), {
            localStorageItems: {
                frontCategoryProductList: {
                    isAllSelected: false,
                    isAllActive: true,
                    isAllCollapsed: false,
                    isAllExpanded: true
                }
            }
        });

        await this.browser.clickInto('parent-category-modal__input', {waitForClickable: true});
        await this.browser.clickInto(['parent-category-modal', 'row_master_category_code_28_1'], {
            waitForClickable: true
        });
        await this.browser.clickInto(['parent-category-modal', 'parent-category-modal__ok-button'], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true});
        await this.browser.clickInto('product_fc_row_front_category_code_5_1', {waitForClickable: true});

        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorNotInDom('submit-button');

        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        const pathToFile = await downloadReversedImport(this, 'download-reverse-import-link');

        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(['import-upload', 'file-input'], pathToFile, {useBrowserFs: true});
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Обратный импорт после создания товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('create-products-for-reversed-import.xlsx')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-create');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');

        const [{identifier: newProductIdentifier}] = await this.browser.executeSql<[{identifier: string}]>(`
            SELECT new_row -> 'identifier' as identifier
            FROM history
            WHERE source = 'import'
            AND table_name = '${DbTable.PRODUCT}'
            AND action = 'I'
            ORDER BY id DESC
            LIMIT 1;
        `);

        await openProductHistoryPage(this, Number(newProductIdentifier));
        const pathToFile = await downloadReversedImport(this, 'download-reverse-import-link');

        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(['import-upload', 'file-input'], pathToFile, {useBrowserFs: true});

        await this.browser.waitForTestIdSelectorInDom('import-info-ignore');
        await this.browser.clickInto(['import-info-ignore', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-ignore', {
            ignoreElements: makeDataTestIdSelector(['import-info-ignore', 'cell_1_1'])
        });

        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});

        await this.browser.assertImage('import-info-update', {
            ignoreElements: makeDataTestIdSelector(['import-info-update', 'cell_1_1'])
        });
    });

    it('Обратное изменение категорий после импорта', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('change-mc-and-fc-for-reversed-import.xlsx')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');

        await openProductHistoryPage(this, 10000008);
        const pathToFile = await downloadReversedImport(this, 'download-reverse-import-link');

        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(['import-upload', 'file-input'], pathToFile, {useBrowserFs: true});
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });
});
