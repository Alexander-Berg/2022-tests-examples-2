import crypto from 'crypto';
import {Unzipped, unzipSync} from 'fflate';
import type {TestContext} from 'hermione';
import {parseSpreadSheetJSON} from 'tests/e2e/helper/parse-spreadsheet';
import {attributes, requiredAttributes} from 'tests/e2e/seed-db-map';
import {addAttributeToInfomodelByCode} from 'tests/e2e/utils/add-attribute-to-infomodel-by-code';
import setAttributeConfirmationValue from 'tests/e2e/utils/confirm-attribute';
import {createAttribute} from 'tests/e2e/utils/create-attribute';
import createImageFile from 'tests/e2e/utils/create-image-file';
import getFixturePath from 'tests/e2e/utils/fixture';
import makeAttributeConfirmable from 'tests/e2e/utils/make-attribute-confirmable';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {DbTable} from '@/src/entities/const';
import {E2E_MAX_SPREADSHEET_ROWS} from 'config/import';
import {AttributeType} from 'types/attribute';

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

    // eslint-disable-next-line max-len
    it('При включенной настройке "Подтвержденность атрибутов" в экспорте всех товаров со всеми атрибутами для подтверждаемых атрибутов выгружается колонка "#confirmed"', async function () {
        await makeAttributeConfirmable(this.browser, attributes.boolean_attribute_code_0_0);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                columnIds: ['boolean_attribute_code_0_0', 'attributes_confirmation'].join()
            },
            region: 'ru'
        });
        await this.browser.clickInto(['products-table-row_10000001', 'checkbox']);

        await this.browser.waitForTestIdSelectorInDom('products-bottom-panel');

        await this.browser.clickInto(['products-bottom-panel', 'export'], {waitRender: true});
        await this.browser.clickInto(['bottom-panel-export-menu', 'export-all'], {waitRender: true});

        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);

        await setAttributeConfirmationValue({
            browser: this.browser,
            productIdentifier: 10000001,
            attributeId: attributes.boolean_attribute_code_0_0
        });

        await this.browser.clickInto('export-icon', {waitRender: true});
        await this.browser.clickInto(['export-menu', 'export-all'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('confirmation-modal');

        await this.browser.clickInto('confirmation-modal__ok-button', {waitForClickable: true, waitRender: true});
        const allProductsFile = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(allProductsFile)).to.matchSnapshot(this);
    });

    // eslint-disable-next-line max-len
    it('При включенной настройке "Подтвержденность атрибутов" у локализуемых атрибутов колонка #confirmed отображается для каждой локали', async function () {
        await makeAttributeConfirmable(this.browser, requiredAttributes.shortNameLoc);
        await setAttributeConfirmationValue({
            browser: this.browser,
            productIdentifier: 10000101,
            attributeId: requiredAttributes.shortNameLoc,
            langId: 3
        });

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                columnIds: ['shortNameLoc', 'attributes_confirmation'].join()
            },
            region: 'fr'
        });
        await this.browser.clickInto(['products-table-row_10000101', 'checkbox']);

        await this.browser.waitForTestIdSelectorInDom('products-bottom-panel');

        await this.browser.clickInto(['products-bottom-panel', 'export'], {waitRender: true});
        await this.browser.clickInto(['bottom-panel-export-menu', 'export-from-table'], {waitRender: true});

        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    // eslint-disable-next-line max-len
    it('При включенной настройке "Подтвержденность атрибутов" в экспорте через балк товаров со всеми атрибутами для подтверждаемых атрибутов выгружается колонка "#confirmed"', async function () {
        await makeAttributeConfirmable(this.browser, requiredAttributes.shortNameLoc);
        await setAttributeConfirmationValue({
            browser: this.browser,
            productIdentifier: 10000101,
            attributeId: requiredAttributes.shortNameLoc,
            langId: 3
        });

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                columnIds: ['shortNameLoc', 'attributes_confirmation'].join()
            },
            region: 'fr'
        });

        await this.browser.clickInto(['products-table-row_10000101', 'checkbox']);
        await this.browser.waitForTestIdSelectorInDom('products-bottom-panel');

        await this.browser.clickInto(['products-bottom-panel', 'export'], {waitRender: true});
        await this.browser.clickInto(['bottom-panel-export-menu', 'export-all'], {waitRender: true});

        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    // eslint-disable-next-line max-len
    it('При включенной настройке "Подтвержденность атрибутов" в экспорте через балк товаров с атрибутами из таблицы для подтверждаемых атрибутов выгружается колонка "#confirmed"', async function () {
        await makeAttributeConfirmable(this.browser, requiredAttributes.shortNameLoc);
        await setAttributeConfirmationValue({
            browser: this.browser,
            productIdentifier: 10000101,
            attributeId: requiredAttributes.shortNameLoc,
            langId: 3
        });

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                columnIds: ['shortNameLoc', 'attributes_confirmation'].join()
            },
            region: 'fr'
        });

        await this.browser.clickInto(['products-table-row_10000101', 'checkbox']);
        await this.browser.waitForTestIdSelectorInDom('products-bottom-panel');

        await this.browser.clickInto(['products-bottom-panel', 'export'], {waitRender: true});
        await this.browser.clickInto(['bottom-panel-export-menu', 'export-from-table'], {waitRender: true});

        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    // eslint-disable-next-line max-len
    it('При выключенной настройке "Подтвержденность атрибутов" в экспорте всех товаров со всеми атрибутами для подтверждаемых атрибутов НЕ выгружается колонка "#confirmed"', async function () {
        await makeAttributeConfirmable(this.browser, requiredAttributes.shortNameLoc);
        await setAttributeConfirmationValue({
            browser: this.browser,
            productIdentifier: 10000101,
            attributeId: requiredAttributes.shortNameLoc,
            langId: 3
        });

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                columnIds: ['shortNameLoc'].join()
            },
            region: 'fr'
        });

        await this.browser.clickInto('export-icon', {waitRender: true});
        await this.browser.clickInto(['export-menu', 'export-all'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('confirmation-modal');

        await this.browser.clickInto('confirmation-modal__ok-button', {waitForClickable: true, waitRender: true});
        const allProductsFile = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(allProductsFile)).to.matchSnapshot(this);
    });

    // eslint-disable-next-line max-len
    it('При выключенной настройке "Подтвержденность атрибутов" в экспорте через балк товаров со всеми атрибутами для подтверждаемых атрибутов НЕ выгружается колонка "#confirmed"', async function () {
        await makeAttributeConfirmable(this.browser, requiredAttributes.shortNameLoc);
        await setAttributeConfirmationValue({
            browser: this.browser,
            productIdentifier: 10000101,
            attributeId: requiredAttributes.shortNameLoc,
            langId: 3
        });

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                columnIds: ['shortNameLoc'].join()
            },
            region: 'fr'
        });

        await this.browser.clickInto(['products-table-row_10000101', 'checkbox']);
        await this.browser.waitForTestIdSelectorInDom('products-bottom-panel');

        await this.browser.clickInto(['products-bottom-panel', 'export'], {waitRender: true});
        await this.browser.clickInto(['bottom-panel-export-menu', 'export-all'], {waitRender: true});

        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    // eslint-disable-next-line max-len
    it('При выключенной настройке "Подтвержденность атрибутов" в экспорте через балк товаров с атрибутами из таблицы для подтверждаемых атрибутов НЕ выгружается колонка "#confirmed"', async function () {
        await makeAttributeConfirmable(this.browser, requiredAttributes.shortNameLoc);
        await setAttributeConfirmationValue({
            browser: this.browser,
            productIdentifier: 10000101,
            attributeId: requiredAttributes.shortNameLoc,
            langId: 3
        });

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                columnIds: ['shortNameLoc'].join()
            },
            region: 'fr'
        });

        await this.browser.clickInto(['products-table-row_10000101', 'checkbox']);
        await this.browser.waitForTestIdSelectorInDom('products-bottom-panel');

        await this.browser.clickInto(['products-bottom-panel', 'export'], {waitRender: true});
        await this.browser.clickInto(['bottom-panel-export-menu', 'export-from-table'], {waitRender: true});

        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    // eslint-disable-next-line max-len
    it('В экспорте с атрибутами из таблицы файл видео-атрибута отображается ссылкой', async function () {
        await createAttribute(this, {type: AttributeType.VIDEO});
        await addAttributeToInfomodelByCode(this, {
            code: 'test_video_attribute_code'
        });

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.uploadFileInto(
            ['without-group', 'test_video_attribute_code-container', 'test_video_attribute_code', 'file-input'],
            getFixturePath('correct-video-sample.mp4')
        );
        await this.browser.waitForTestIdSelectorInDom(['header-panel', 'cancel-button']);

        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                columnIds: ['test_video_attribute_code'].join()
            }
        });

        await this.browser.clickInto(['products-table-row_10000001', 'checkbox']);
        await this.browser.waitForTestIdSelectorInDom('products-bottom-panel');

        await this.browser.clickInto(['products-bottom-panel', 'export'], {waitRender: true});
        await this.browser.clickInto(['bottom-panel-export-menu', 'export-from-table'], {waitRender: true});

        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    // eslint-disable-next-line max-len
    it('В экспорте через балк со всеми атрибутами два файла множественного видео-атрибута отображаются ссылками через запятую', async function () {
        await createAttribute(this, {type: AttributeType.VIDEO, max: 2});
        await addAttributeToInfomodelByCode(this, {code: 'test_video_attribute_code'});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.uploadFileInto(
            ['without-group', 'test_video_attribute_code-array', 'file-input'],
            getFixturePath('correct-video-sample.mp4')
        );
        await this.browser.uploadFileInto(
            ['without-group', 'test_video_attribute_code-array', 'file-input'],
            getFixturePath('correct-video-sample.mp4')
        );

        await this.browser.waitUntilRendered();

        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                columnIds: ['test_video_attribute_code'].join()
            }
        });

        await this.browser.clickInto(['products-table-row_10000001', 'checkbox']);
        await this.browser.waitForTestIdSelectorInDom('products-bottom-panel');

        await this.browser.clickInto(['products-bottom-panel', 'export'], {waitRender: true});
        await this.browser.clickInto(['bottom-panel-export-menu', 'export-from-table'], {waitRender: true});

        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });
});
