import crypto from 'crypto';
import {Unzipped, unzipSync} from 'fflate';
import type {TestContext} from 'hermione';
import {parseSpreadSheetJSON} from 'tests/e2e/helper/parse-spreadsheet';
import createImageFile from 'tests/e2e/utils/create-image-file';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {DbTable} from '@/src/entities/const';
import {E2E_MAX_SPREADSHEET_ROWS} from 'config/import';

describe('Экспорт', function () {
    async function getContentProductImagesArchive(browser: WebdriverIO.Browser) {
        const archiveBuffer = await browser.getDownloadedFile('product-images.zip', {purge: true});

        const decompressedArchive = unzipSync(archiveBuffer);

        return decompressedArchive;
    }

    function makeImagesSnapshot(testContext: TestContext, images: Unzipped) {
        const hash = crypto.createHash('md5').update(images.toString());

        expect(hash.digest('hex')).to.matchSnapshot(testContext);
    }

    it('Экспорт товаров с атрибутами из таблицы (настройка по-умолчанию)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto('export-icon', {waitRender: true});
        await this.browser.clickInto(['export-menu', 'export-from-table'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('confirmation-modal');

        await this.browser.clickInto('confirmation-modal__ok-button', {waitForClickable: true, waitRender: true});
        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});

        const parsed = parseSpreadSheetJSON(file);
        expect(parsed.length).to.equal(E2E_MAX_SPREADSHEET_ROWS);
        expect(parsed).to.matchSnapshot(this);
    });

    it('Экспорт таблицы со всеми типами атрибутов в России', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                columnIds: [
                    'boolean_attribute_code_0_0',
                    'number_attribute_code_3_1',
                    'number_attribute_code_3_0',
                    'string_attribute_code_5_1',
                    'string_attribute_code_5_0',
                    'text_attribute_code_6_1',
                    'text_attribute_code_6_0',
                    'select_attribute_code_4_0',
                    'multiselect_attribute_code_2_0',
                    'shortNameLoc',
                    'image'
                ].join()
            },
            region: 'ru'
        });

        await this.browser.clickInto('export-icon', {waitRender: true});
        await this.browser.clickInto(['export-menu', 'export-from-table'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('confirmation-modal');

        await this.browser.clickInto('confirmation-modal__ok-button', {waitForClickable: true, waitRender: true});

        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    it('Экспорт всех атрибутов в Израиле', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'il'});

        await this.browser.clickInto('export-icon', {waitRender: true});
        await this.browser.clickInto(['export-menu', 'export-all'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('confirmation-modal');

        await this.browser.clickInto('confirmation-modal__ok-button', {waitForClickable: true, waitRender: true});

        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});

        const parsed = parseSpreadSheetJSON(file);
        expect(parsed.length).to.equal(E2E_MAX_SPREADSHEET_ROWS);
        expect(parsed).to.matchSnapshot(this);
    });

    it('Экспорт одного выбранного товара с пустым атрибутом в таблице', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                columnIds: 'image'
            },
            region: 'ru'
        });
        await this.browser.clickInto(['products-table-row_10000002', 'checkbox']);
        await this.browser.waitForTestIdSelectorInDom('products-bottom-panel');

        await this.browser.clickInto(['products-bottom-panel', 'export'], {waitRender: true});
        await this.browser.clickInto(['bottom-panel-export-menu', 'export-from-table'], {waitRender: true});

        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    it('Экспорт двух выбранных товаров со всеми атрибутами в Великобритании', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'gb'});
        await this.browser.clickInto(['products-table-row_10000051', 'checkbox']);
        await this.browser.clickInto(['products-table-row_10000052', 'checkbox']);

        await this.browser.waitForTestIdSelectorInDom('products-bottom-panel');

        await this.browser.clickInto(['products-bottom-panel', 'export'], {waitRender: true});

        await this.browser.clickInto(['bottom-panel-export-menu', 'export-all'], {waitRender: true});

        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    it('Экспорт товара с множественными изображениями', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                columnIds: 'image_attribute_code_1_1'
            },
            region: 'ru'
        });
        await this.browser.clickInto(['products-table-row_10000001', 'checkbox']);

        await this.browser.waitForTestIdSelectorInDom('products-bottom-panel');

        await this.browser.clickInto(['products-bottom-panel', 'export'], {waitRender: true});
        await this.browser.clickInto(['bottom-panel-export-menu', 'export-from-table'], {waitRender: true});

        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    it('Ограничение на количество экспортируемых товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);

        await this.browser.clickInto(['products-table', 'select-all-checkbox'], {waitRender: true});
        await this.browser.assertImage('products-bottom-panel', {removeShadows: true});

        await this.browser.clickInto(['action-bar', 'export-icon'], {waitRender: true});
        await this.browser.clickInto(['export-menu', 'export-all'], {waitRender: true});

        await this.browser.waitForTestIdSelectorInDom('confirmation-modal');
        await this.browser.assertImage('confirmation-modal', {removeShadows: true});
    });

    it('Экспорт всех выбранных товаров со всеми атрибутами, Россия', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);

        await this.browser.clickInto(['products-table', 'select-all-checkbox'], {waitRender: true});
        await this.browser.clickInto(['products-bottom-panel', 'export'], {waitRender: true});
        await this.browser.clickInto(['bottom-panel-export-menu', 'export-all'], {waitRender: true});

        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    it('Экспорт всех выбранных товаров со всеми атрибутами из таблицы, Россия', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);

        await this.browser.clickInto(['products-table', 'select-all-checkbox'], {waitRender: true});
        await this.browser.clickInto(['products-bottom-panel', 'export'], {waitRender: true});
        await this.browser.clickInto(['bottom-panel-export-menu', 'export-from-table'], {waitRender: true});

        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    it('Экспорт больше лимита невозможен', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);

        await this.browser.clickInto(['products-table', 'select-all-checkbox'], {waitRender: true});

        await this.browser.performScroll(['products-table', 'table-container'], {
            direction: 'down',
            beforeIterationDelay: () => this.browser.waitForTestIdSelectorNotInDom('products_table__spinner'),
            afterIterationDelay: () => this.browser.waitUntilRendered()
        });

        await this.browser.clickInto(['products-table-row_10000044', 'checkbox'], {waitRender: true});
        await this.browser.assertImage('products-table');
    });

    it('Отображение в экспорте пустого атрибута', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.clickInto('boolean_attribute_code_0_0_unset');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {search: '10000001', columnIds: 'boolean_attribute_code_0_0'}
        });
        await this.browser.clickInto('export-icon');
        await this.browser.clickInto(['export-menu', 'export-from-table'], {waitRender: true});
        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file, {blankrows: true, defval: ''})).to.matchSnapshot(this);
    });

    it('Экспорт нескольких товаров с типом номенклатуры', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {columnIds: ['id', 'nomenclatureType'].join()}
        });

        await this.browser.clickInto('export-icon', {waitRender: true});
        await this.browser.clickInto(['export-menu', 'export-from-table']);
        await this.browser.clickInto('confirmation-modal__ok-button', {waitForClickable: true, waitRender: true});

        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    it('Локализация не отображается в таблице экспорта Франции', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'fr',
            queryParams: {columnIds: ['id', 'localization', 'localization_en', 'localization_ru'].join()}
        });
        await this.browser.clickInto(['products-table-row_10000101', 'checkbox']);

        await this.browser.waitForTestIdSelectorInDom('products-bottom-panel');

        await this.browser.clickInto(['products-bottom-panel', 'export'], {waitRender: true});

        await this.browser.clickInto(['bottom-panel-export-menu', 'export-from-table'], {waitRender: true});

        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file, {blankrows: true, defval: ''})).to.matchSnapshot(this);
    });

    it('Предупреждение об экспорте фотографий, превышающих пороговое значение', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);

        await this.browser.clickInto('export-icon', {waitRender: true});
        await this.browser.clickInto(['export-menu', 'export-images'], {waitRender: true});

        await this.browser.assertImage('confirmation-modal', {removeShadows: true});

        await this.browser.clickInto('confirmation-modal__cancel-button', {waitForClickable: true, waitRender: true});

        await this.browser.waitForTestIdSelectorNotInDom('\\.ant-modal-mask');
    });

    it('Экспорт максимального количества фотографий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);

        await this.browser.clickInto('export-icon', {waitRender: true});
        await this.browser.clickInto(['export-menu', 'export-images']);
        await this.browser.clickInto('confirmation-modal__ok-button', {waitForClickable: true, waitRender: true});

        const images = await getContentProductImagesArchive(this.browser);

        makeImagesSnapshot(this, images);
    });

    it('Экспорт фото нескольких товаров, у которых нет фото', async function () {
        await this.browser.executeSql(`
            DELETE FROM ${DbTable.PRODUCT_ATTRIBUTE_VALUE} WHERE id in (SELECT pav.id
            FROM ${DbTable.PRODUCT_ATTRIBUTE_VALUE} pav
            JOIN ${DbTable.PRODUCT} p ON pav.product_id = p.id
            WHERE pav.attribute_id = 23 AND p.identifier in ('10000001', '10000002', '10000003'));
        `);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);

        await this.browser.clickInto('export-icon', {waitRender: true});
        await this.browser.clickInto(['export-menu', 'export-images']);
        await this.browser.clickInto('confirmation-modal__ok-button', {waitForClickable: true, waitRender: true});

        const images = await getContentProductImagesArchive(this.browser);

        expect(images).to.deep.equal({});
    });

    it('Экспорт товаров с фото и мета-товаров. Выбор балком', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {filters: {id: {rule: 'equal', values: [10000001, 10000002, 10000201].join()}}}
        });

        await this.browser.clickInto(['products-table-row_10000001', 'checkbox']);
        await this.browser.clickInto(['products-table-row_10000002', 'checkbox']);
        await this.browser.clickInto(['products-table-row_10000201', 'checkbox']);

        await this.browser.waitForTestIdSelectorInDom('products-bottom-panel');
        await this.browser.clickInto(['products-bottom-panel', 'export'], {waitRender: true});
        await this.browser.clickInto(['bottom-panel-export-menu', 'export-images'], {waitRender: true});

        const images = await getContentProductImagesArchive(this.browser);

        makeImagesSnapshot(this, images);
    });

    it('Экспорт фото отфильтрованных товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {filters: {id: {rule: 'equal', values: [10000001, 10000002].join()}}}
        });

        await this.browser.clickInto('export-icon', {waitRender: true});
        await this.browser.clickInto(['export-menu', 'export-images'], {waitRender: true});

        const images = await getContentProductImagesArchive(this.browser);

        makeImagesSnapshot(this, images);
    });

    it('Экспорт фото товара с несколькими баркодами и несколькими фото', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.uploadFileInto(['product-image', 'file-input'], createImageFile('product_image_1.png'));
        await this.browser.uploadFileInto(['product-image', 'file-input'], createImageFile('product_image_2.png'));
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);

        await this.browser.clickInto(['products-table-row_10000001', 'checkbox']);

        await this.browser.waitForTestIdSelectorInDom('products-bottom-panel');
        await this.browser.clickInto(['products-bottom-panel', 'export'], {waitRender: true});
        await this.browser.clickInto(['bottom-panel-export-menu', 'export-images'], {waitRender: true});

        const images = await getContentProductImagesArchive(this.browser);

        makeImagesSnapshot(this, images);
    });
});
