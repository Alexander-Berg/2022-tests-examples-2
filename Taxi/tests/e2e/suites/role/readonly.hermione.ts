import {attributes, frontCategories, masterCategories, productCombos, specialAttributes} from 'tests/e2e/seed-db-map';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {DbTable} from '@/src/entities/const';

describe('Readonly', function () {
    it('Нельзя редактировать атрибут типа список', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributes.multiselect_attribute_code_2_0), {
            isReadonly: true
        });

        await this.browser.waitForTestIdSelectorDisabled(['attribute-type', '\\input']);
        await this.browser.waitForTestIdSelectorDisabled('code');
        await this.browser.waitForTestIdSelectorDisabled('ticket-parameter');

        await this.browser.dragAndDrop(
            'select-option-header-attribute_option_code_10_1',
            'select-option-header-attribute_option_code_10_2',
            {offset: 'bottom'}
        );
        await this.browser.clickInto(['select-option', 'select-option-header-attribute_option_code_10_1'], {
            waitRender: true
        });
        await this.browser.assertImage('select-option');

        await this.browser.waitForTestIdSelectorDisabled(['translations', 'name']);
        await this.browser.waitForTestIdSelectorDisabled(['translations', 'description']);
    });

    it('Нельзя редактировать инфомодель', async function () {
        const INFO_MODEL_ID = 5;
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(INFO_MODEL_ID), {isReadonly: true});
        await this.browser.waitForTestIdSelectorDisabled('code');

        await this.browser.waitForTestIdSelectorDisabled(['translations', 'name']);
        await this.browser.waitForTestIdSelectorDisabled(['translations', 'description']);

        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['im_attribute_row_multiselect_attribute_code_2_0', 'switch-important']);

        await this.browser.assertImage('im_attribute_row_multiselect_attribute_code_2_0');
    });

    it('Нельзя редактировать фронт-категорию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0), {
            isReadonly: true
        });
        await this.browser.waitForTestIdSelectorDisabled(['status', 'disabled']);
        await this.browser.waitForTestIdSelectorDisabled(['status', 'active']);
        await this.browser.waitForTestIdSelectorDisabled('parent-category-modal__input');
        await this.browser.waitForTestIdSelectorDisabled('code');
        await this.browser.waitForTestIdSelectorDisabled('promo');
        await this.browser.waitForTestIdSelectorDisabled('deeplink');
        await this.browser.waitForTestIdSelectorDisabled('legal_restrictions');

        await this.browser.waitForTestIdSelectorNotInDom('delete_image');

        await this.browser.waitForTestIdSelectorDisabled(['translations', 'name']);
        await this.browser.waitForTestIdSelectorDisabled(['translations', 'description']);
    });

    it('Нельзя редактировать мастер-категорию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_1_0), {
            isReadonly: true
        });

        await this.browser.waitForTestIdSelectorDisabled(['status', 'disabled']);
        await this.browser.waitForTestIdSelectorDisabled(['status', 'active']);
        await this.browser.waitForTestIdSelectorDisabled('parent-category-modal__input');
        await this.browser.waitForTestIdSelectorDisabled(['info-model-select', '\\input']);

        await this.browser.waitForTestIdSelectorDisabled(['translations', 'name']);
        await this.browser.waitForTestIdSelectorDisabled(['translations', 'description']);
    });

    it('Нельзя редактировать товар', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002), {isReadonly: true});

        await this.browser.waitForTestIdSelectorDisabled(['status', 'disabled']);
        await this.browser.waitForTestIdSelectorDisabled(['status', 'active']);
        await this.browser.waitForTestIdSelectorDisabled('parent-category-modal__input');
        await this.browser.waitForTestIdSelectorDisabled('barcode__0');
        await this.browser.waitForTestIdSelectorDisabled('longName_ru');
        await this.browser.waitForTestIdSelectorDisabled('markCount');

        await this.browser.waitForTestIdSelectorNotInDom(['product-image', 'delete-image']);

        await this.browser.waitForTestIdSelectorDisabled(['boolean_attribute_code_0_0_on', '\\input']);
        await this.browser.waitForTestIdSelectorDisabled(['boolean_attribute_code_0_0_unset', '\\input']);
        await this.browser.waitForTestIdSelectorDisabled(['boolean_attribute_code_0_0_off', '\\input']);
        await this.browser.waitForTestIdSelectorNotInDom(['image_attribute_code_1_0', 'delete-image']);
        await this.browser.waitForTestIdSelectorDisabled('number_attribute_code_3_0');
        await this.browser.waitForTestIdSelectorDisabled('string_attribute_code_5_0');
        await this.browser.waitForTestIdSelectorDisabled('text_attribute_code_6_0');
        await this.browser.waitForTestIdSelectorDisabled(['multiselect_attribute_code_2_0', '\\input']);
        await this.browser.waitForTestIdSelectorDisabled(['select_attribute_code_4_0', '\\input']);

        await this.browser.waitForTestIdSelectorDisabled('substitutions__0');
    });

    it('Нельзя сменить фронт-категорию у товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001), {isReadonly: true, clearLocalStorage: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true});

        await this.browser.waitForTestIdSelectorNotInDom('show-assigned');
        await this.browser.assertImage('action-bar');
        await this.browser.assertImage('product_fc_row_front_category_code_5_0');
    });

    it('Нельзя поменять порядок фронт-категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES, {isReadonly: true});
        await this.browser.assertImage('fc_row_front_category_code_1_0');
    });

    it('Нет кнопки Создать на таблице товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {isReadonly: true});
        await this.browser.waitForTestIdSelectorNotInDom('create-button');
        await this.browser.assertImage('action-bar');
    });

    it('Нет кнопки Создать на списке мастер-категорий товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES, {isReadonly: true});
        await this.browser.waitForTestIdSelectorNotInDom('create-button');
        await this.browser.assertImage('action-bar');
        await this.browser.waitForTestIdSelectorNotInDom('category-row-more-button');
    });

    it('Нет кнопки Создать на списке фронт-категорий товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES, {isReadonly: true});
        await this.browser.waitForTestIdSelectorNotInDom('create-button');
        await this.browser.assertImage('action-bar');
        await this.browser.waitForTestIdSelectorNotInDom('category-row-more-button');
    });

    it('Нет кнопки Создать на списке инфомоделей', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS, {isReadonly: true});
        await this.browser.waitForTestIdSelectorNotInDom('create-button');
        await this.browser.assertImage('action-bar');
    });

    it('Нет кнопки Создать на списке атрибутов', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES, {isReadonly: true});
        await this.browser.waitForTestIdSelectorNotInDom('create-button');
        await this.browser.assertImage('action-bar');
    });

    it('В меню нет раздела импорт', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {isReadonly: true});
        await this.browser.assertImage(['sidebar', 'menu']);
    });

    it('Нельзя открыть страницу импорта по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS, {isReadonly: true});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage();
    });

    it('Нельзя открыть страницу создания товара по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS_CREATE, {isReadonly: true});
        await this.browser.waitForTestIdSelectorInDom('not-found');
    });

    it('Нельзя открыть страницу создания фронт-категории по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY, {isReadonly: true});
        await this.browser.waitForTestIdSelectorInDom('not-found');
    });

    it('Нельзя открыть страницу создания мастер-категории по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY, {isReadonly: true});
        await this.browser.waitForTestIdSelectorInDom('not-found');
    });

    it('Нельзя открыть страницу создания инфомодели по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL, {isReadonly: true});
        await this.browser.waitForTestIdSelectorInDom('not-found');
    });

    it('Нельзя открыть страницу создания атрибута по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE, {isReadonly: true});
        await this.browser.waitForTestIdSelectorInDom('not-found');
    });

    it('Открыть таблицу товаров по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {isReadonly: true});
        await this.browser.waitForTestIdSelectorInDom('table-container');
    });

    it('Открыть таблицу МК по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES, {isReadonly: true});
        await this.browser.waitForTestIdSelectorInDom('tree-table');
    });

    it('Открыть таблицу ФК по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES, {isReadonly: true});
        await this.browser.waitForTestIdSelectorInDom('tree-table');
    });

    it('Открыть таблицу ИМ по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS, {isReadonly: true});
        await this.browser.waitForTestIdSelectorInDom('infomodels-table');
    });

    it('Открыть таблицу атрибутов по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES, {isReadonly: true});
        await this.browser.waitForTestIdSelectorInDom('attributes-table_table');
    });

    it('Нельзя открыть страницу создания комбинации по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS_CREATE, {isReadonly: true});
        await this.browser.waitForTestIdSelectorInDom('not-found');
    });

    it('Открыть страницу редактирования комбинации по прямой ссылке', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['0dd1fb51-36d9-4788-94bf-bd87d311894c']),
            {isReadonly: true}
        );
        await this.browser.assertImage('header-panel');
        await this.browser.assertImage('base-layout-content');
    });

    it('Нельзя добавить фото в режиме readonly', async function () {
        const productId = 10000001;
        await this.browser.executeSql(
            `
            DELETE FROM ${DbTable.PRODUCT_ATTRIBUTE_VALUE}
            WHERE id IN (
                SELECT pav.id
                FROM ${DbTable.PRODUCT_ATTRIBUTE_VALUE} pav
                JOIN ${DbTable.PRODUCT} p ON pav.product_id = p.id
                WHERE
                    pav.attribute_id IN (${specialAttributes.image}, ${attributes.image_attribute_code_1_1})
                    AND p.identifier in (${productId})
            )
            `
        );
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001), {isReadonly: true});
        await this.browser.waitForTestIdSelectorNotInDom(['image-drag-0', 'delete-image']);
        await this.browser.assertImage('main-image', {removeShadows: true});
        await this.browser.assertImage('image_attribute_code_1_1-array');
    });
});
