import getFixturePath from 'tests/e2e/utils/fixture';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {DbTable} from '@/src/entities/const';
import {assertNumber} from 'service/helper/assert-number';
import type {Language} from 'types/common';

describe('Импорт мета-товаров', function () {
    async function getProductIdentifierByLongName(ctx: Hermione.TestContext, longName: string, locale: Language) {
        const [{identifier}] = await ctx.browser.executeSql(`
            SELECT p.identifier AS identifier FROM ${DbTable.PRODUCT} p
            INNER JOIN ${DbTable.PRODUCT_ATTRIBUTE_VALUE} pav ON pav.product_id = p.id
            INNER JOIN ${DbTable.LANG} l ON l.id = pav.lang_id
            WHERE l.iso_code = '${locale}'
            AND '${longName}' = ANY(pav.value_text)
            LIMIT 1;
        `);

        return assertNumber(identifier, {coerce: true});
    }

    it('Создание мета-товара с необязательными системными атрибутами', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('meta-product-import-with-excessive-attributes.zip')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-create');
        await this.browser.clickInto(['import-info-create', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('import-cell-tooltip-help-icon', {waitRender: true});
        await this.browser.assertImage('import-info-create');

        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');
        const newIdentifier = await getProductIdentifierByLongName(this, 'Тестовый мета-товар', 'ru');
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(newIdentifier));
        await this.browser.assertImage('product_view');
    });

    it('Редактирование товаров с изменением необязательных системных атрибутов', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('meta-product-import-with-unused-required-attributes.xlsx')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('import-cell-tooltip-help-icon', {waitRender: true});
        await this.browser.assertImage('import-info-update');

        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000201));
        await this.browser.assertImage('product_view');
    });

    it('Создание мета-товара с любой МК', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('create-meta-product-with-specified-mc.zip')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-create');
        await this.browser.clickInto(['import-info-create', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('import-cell-tooltip-help-icon', {waitRender: true});
        await this.browser.assertImage('import-info-create');

        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');
    });

    it('Нельзя создать мета-товар без изображения', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('create-meta-product-without-image.xlsx')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-not-upload');
        await this.browser.clickInto(['import-info-not-upload', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('import-cell-tooltip-help-icon', {waitRender: true});
        await this.browser.assertImage('import-info-not-upload');
    });

    it('Нельзя сменить мастер-категорию мета-товару', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('change-meta-product-master-category.xlsx')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-ignore');
        await this.browser.clickInto(['import-info-ignore', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('import-cell-tooltip-help-icon', {waitRender: true});
        await this.browser.assertImage('import-info-ignore');

        await this.browser.waitForTestIdSelectorDisabled('submit-button');
    });

    it('Нельзя изменить мета свойство товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(['import-upload', 'file-input'], getFixturePath('change-is-meta.xlsx'));

        await this.browser.waitForTestIdSelectorInDom('import-info-not-upload');
        await this.browser.clickInto(['import-info-not-upload', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('import-cell-tooltip-help-icon', {waitRender: true});
        await this.browser.assertImage('import-info-not-upload');

        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');

        await this.browser.clickInto('submit-button');
        await this.browser.clickInto('confirmation-modal__ok-button', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');
    });

    it('Нельзя стереть обязательные атрибуты у мета-товара. Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS, {region: 'fr'});
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('remove-required-attributes-from-product.xlsx')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-not-upload');
        await this.browser.clickInto(['import-info-not-upload', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('import-cell-tooltip-help-icon', {waitRender: true});
        await this.browser.assertImage('import-info-not-upload');

        await this.browser.waitForTestIdSelectorDisabled('submit-button');
    });

    it('Нельзя создать мета-товар без системных атрибутов. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS, {region: 'il'});
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('create-meta-product-with-incomplete-required-attributes.zip')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-not-upload');
        await this.browser.clickInto(['import-info-not-upload', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('import-cell-tooltip-help-icon', {waitRender: true});
        await this.browser.assertImage('import-info-not-upload');

        await this.browser.waitForTestIdSelectorDisabled('submit-button');
    });
});
