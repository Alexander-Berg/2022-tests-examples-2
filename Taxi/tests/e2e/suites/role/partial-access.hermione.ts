import {parseSpreadSheetJSON} from 'tests/e2e/helper/parse-spreadsheet';
import {
    attributeGroups,
    attributes,
    frontCategories,
    infoModels,
    masterCategories,
    productCombos
} from 'tests/e2e/seed-db-map';
import createImageFile from 'tests/e2e/utils/create-image-file';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {DbTable} from '@/src/entities/const';
import {allRules, Rules} from 'types/role';

describe('Роль с доступом к конкретным атрибутам', function () {
    const rules: Rules = {
        product: {
            canEditAttribute: [
                'boolean_attribute_code_0_0',
                'image_attribute_code_1_1',
                'multiselect_attribute_code_2_0',
                'number_attribute_code_3_0',
                'select_attribute_code_4_0',
                'string_attribute_code_5_0',
                'text_attribute_code_6_0'
            ]
        }
    };

    it('Может редактировать доступные атрибуты', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000102), {region: 'fr'});

        await this.browser.clickInto('boolean_attribute_code_0_0_on');
        await this.browser.typeInto('string_attribute_code_5_0', 'test');
        await this.browser.typeInto('text_attribute_code_6_0', 'test', {clear: true});
        await this.browser.typeInto('number_attribute_code_3_0', '1', {clear: true});

        await this.browser.clickInto('select_attribute_code_4_0');
        await this.browser.clickInto(['select_attribute_code_4_0_dropdown-menu', 'attribute_option_code_14_1']);
        await this.browser.clickInto('select_attribute_code_4_0');

        await this.browser.clickInto('multiselect_attribute_code_2_0');
        await this.browser.clickInto(['multiselect_attribute_code_2_0_dropdown-menu', 'attribute_option_code_10_1']);
        await this.browser.clickInto('multiselect_attribute_code_2_0');

        const element = await this.browser.findByTestId('image-drag-0');
        await element.moveTo();
        await this.browser.clickInto(['image-drag-0', 'delete-image']);

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000102), {region: 'fr'});

        await this.browser.assertImage('attribute_group_code_1', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_2', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_3', {removeShadows: true});
    });

    it('Не может менять фронт-категорию', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000102), {region: 'fr'});
        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true});

        await this.browser.assertImage('action-bar');
        await this.browser.assertImage('tree-table');
    });

    it('Не может менять недоступные атрибуты', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000102), {region: 'fr'});
        await this.browser.assertImage('basic-attributes', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_1', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_2', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_3', {removeShadows: true});
    });

    it('Не может открыть страницу импорта по прямой ссылке', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS, {region: 'fr'});
        await this.browser.waitForTestIdSelectorInDom('not-found');
    });

    it('Не может открыть страницу балковых действий', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'fr'});
        await this.browser.clickInto(['products-table-row_10000101', 'checkbox']);
        await this.browser.assertImage('products-bottom-panel', {removeShadows: true});
    });

    it('Не видит кнопки импорта товара и создания товара', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'fr'});
        await this.browser.assertImage('action-bar');
    });

    it('Не видит кнопки импорта инфомодели и создания инфомодели', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS, {region: 'fr'});
        await this.browser.assertImage('action-bar');
    });

    it('Видит название своей роли', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'fr'});
        await this.browser.clickInto('account');
        await this.browser.assertImage('account-settings', {removeShadows: true});
    });

    it('Не может редактировать группу атрибутов', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUP(attributeGroups.attribute_group_code_1), {
            region: 'fr'
        });
        await this.browser.assertImage('base-layout-content');
    });

    it('Не может редактировать мета-товар', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000207), {region: 'fr'});
        await this.browser.assertImage('base-layout-content');
    });

    it('Не видит кнопки создания атрибута', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS, {region: 'fr'});
        await this.browser.assertImage('action-bar');
    });

    it('Не может редактировать доступные для Франции атрибуты в России', async function () {
        await this.browser.addUserRole({rules, region: 'fr', clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));

        await this.browser.assertImage('attribute_group_code_1', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_2', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_3', {removeShadows: true});
    });
});

describe('Роль с запретом доступа к конкретным атрибутам', function () {
    const rules: Rules = {
        product: {
            canEditAttributeAll: true,
            canNotEditAttribute: [
                'boolean_attribute_code_0_0',
                'image_attribute_code_1_1',
                'multiselect_attribute_code_2_0',
                'number_attribute_code_3_0',
                'select_attribute_code_4_0',
                'string_attribute_code_5_0',
                'text_attribute_code_6_0'
            ]
        }
    };

    it('Не может редактировать запрещенные атрибуты', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));
        await this.browser.assertImage('basic-attributes', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_1', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_2', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_3', {removeShadows: true});
    });

    it('Может редактировать остальные атрибуты', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));

        await this.browser.typeInto('markCount', '123', {clear: true});

        await this.browser.clickInto('boolean_attribute_code_0_1_on');
        await this.browser.typeInto('string_attribute_code_5_2_loc_ru', 'test');
        await this.browser.typeInto('text_attribute_code_6_2_loc_ru', 'test', {clear: true});
        await this.browser.typeInto('number_attribute_code_3_1__0', '1', {clear: true});

        await this.browser.clickInto('select_attribute_code_4_1');
        await this.browser.clickInto(['select_attribute_code_4_1_dropdown-menu', 'attribute_option_code_15_2']);
        await this.browser.clickInto('select_attribute_code_4_1');

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));

        await this.browser.assertImage('basic-attributes', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_1', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_2', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_3', {removeShadows: true});
        await this.browser.assertImage('without-group', {removeShadows: true});
    });

    it('Не может менять фронт-категорию у товара', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));
        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true});

        await this.browser.assertImage('action-bar');
        await this.browser.assertImage('tree-table');
    });

    it('Не видит кнопки импорта товара и создания товара', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.assertImage('action-bar');
    });

    it('Не может открыть страницу балковых действий', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'fr'});
        await this.browser.clickInto(['products-table-row_10000101', 'checkbox']);
        await this.browser.assertImage('products-bottom-panel', {removeShadows: true});
    });

    it('Не может создать мастер-категорию по прямой ссылке', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.waitForTestIdSelectorInDom('not-found');
    });

    it('Не видит кнопки импорта инфомодели и создания инфомодели', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.assertImage('action-bar');
    });

    it('Не видит кнопку создания фронт-категорий', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.assertImage('action-bar');
    });

    it('Не может редактировать атрибут', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributes.boolean_attribute_code_0_0));
        await this.browser.assertImage('base-layout-content');
    });

    it('Видит название своей роли', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'fr'});
        await this.browser.clickInto('account');
        await this.browser.assertImage('account-settings', {removeShadows: true});
    });

    it('Не может создать группу атрибутов по прямой ссылке', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE_GROUP);
        await this.browser.waitForTestIdSelectorInDom('not-found');
    });

    it('Не может редактировать мастер-категорию', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_1_0));
        await this.browser.assertImage('base-layout-content');
    });

    it('Не видит кнопки создания комбинации', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS);
        await this.browser.assertImage('action-bar');
    });

    it('Не может редактировать запрещенные атрибуты в Израиле', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000151), {region: 'il'});
        await this.browser.assertImage('basic-attributes', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_1', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_2', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_3', {removeShadows: true});
    });
});

describe('Роль с доступом до фк,мк и статуса', function () {
    const rules: Rules = {
        product: {
            canEditMasterCategory: true,
            canEditFrontCategory: true,
            canEditStatus: true
        }
    };

    it('Может менять фронт-категории у товара', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000101), {region: 'fr'});
        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true});

        await this.browser.clickInto('expand-all', {waitRender: true});
        await this.browser.clickInto('product_fc_row_front_category_code_45_0');
        await this.browser.clickInto('product_fc_row_front_category_code_45_1');
        await this.browser.clickInto('product_fc_row_front_category_code_45_2');

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000101), {region: 'fr'});
        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true});
        await this.browser.clickInto('expand-all', {waitRender: true});
        await this.browser.assertImage('table-body');
    });

    it('Может менять мастер-категорию товара', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000101), {region: 'fr'});

        await this.browser.clickInto('parent-category-modal__input', {waitRender: true});
        await this.browser.clickInto(['row_master_category_code_45_1', 'title']);
        await this.browser.clickInto('parent-category-modal__ok-button');

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000101), {region: 'fr'});
        await this.browser.assertImage('parent-category-modal__input');
    });

    it('Не может менять другие атрибуты', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000103), {region: 'fr'});

        await this.browser.assertImage('basic-attributes', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_1', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_2', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_3', {removeShadows: true});
        await this.browser.assertImage('without-group', {removeShadows: true});
        await this.browser.assertImage('substitutions-container');
    });

    it('Может менять статус товара', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000101), {region: 'fr'});
        await this.browser.clickInto('disabled_label');

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000101), {region: 'fr'});
        await this.browser.assertImage('status');
    });

    it('Не может открыть создание товара по прямой ссылке', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS_CREATE, {region: 'fr'});
        await this.browser.waitForTestIdSelectorInDom('not-found');
    });

    it('Не видит кнопки импорта товара и создания товара', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'fr'});
        await this.browser.assertImage('action-bar');
    });

    it('Не может открыть импорт инфомоделей по прямой ссылке', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_INFOMODELS, {region: 'fr'});
        await this.browser.waitForTestIdSelectorInDom('not-found');
    });

    it('Видит название своей роли', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'fr'});
        await this.browser.clickInto('account');
        await this.browser.assertImage('account-settings', {removeShadows: true});
    });

    it('Не может открыть страницу балковых действий', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'fr'});
        await this.browser.clickInto(['products-table-row_10000101', 'checkbox']);
        await this.browser.assertImage('products-bottom-panel', {removeShadows: true});
    });

    it('Не может редактировать фронт-категорию', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.fr.front_category_code_3_0), {
            region: 'fr'
        });
        await this.browser.assertImage('base-layout-content');
    });

    it('Не может редактировать инфомодель', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.fr.info_model_code_3_1), {
            region: 'fr'
        });
        await this.browser.assertImage('base-layout-content');
    });

    it('Может экспортировать товары', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'fr'});

        await this.browser.clickInto(['products-table-row_10000101', 'checkbox']);
        await this.browser.clickInto(['products-bottom-panel', 'export']);
        await this.browser.clickInto(['bottom-panel-export-menu', 'export-from-table'], {waitRender: true});

        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    it('Не может редактировать комбинацию', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.fr['0c98ca19-22c3-4500-ac13-0c67a14f6ed5']),
            {region: 'fr'}
        );
        await this.browser.assertImage('base-layout-content');
    });

    it('Не может создать мета-товар по прямой ссылке', async function () {
        await this.browser.addUserRole({rules, region: 'fr'});
        await this.browser.openPage([ROUTES.CLIENT.PRODUCTS_CREATE, 'meta'].join('?'), {region: 'fr'});
        await this.browser.waitForTestIdSelectorInDom('not-found');
    });

    it('Не может менять фк,мк и статус в России', async function () {
        await this.browser.addUserRole({rules, region: 'fr', clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.assertImage('basic-attributes', {removeShadows: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true});

        await this.browser.assertImage('action-bar');
        await this.browser.assertImage('tree-table');
    });
});

describe('Роль с доступом до всего кроме балка и импорта', function () {
    const rules: Rules = {
        ...allRules
    };
    delete rules.canBulk;

    it('Может создавать товары по кнопке', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto('create-button');
        await this.browser.clickInto(['create-product-menu', 'create-real'], {waitRender: true});
        await this.browser.clickInto('row_master_category_code_1_0', {waitForClickable: true});
        await this.browser.clickInto('row_master_category_code_5_0', {waitForClickable: true});
        await this.browser.clickInto('row_master_category_code_25_0', {waitForClickable: true});
        await this.browser.clickInto('parent-category-modal__ok-button', {waitNavigation: true});

        await this.browser.clickInto('add_new_barcode');
        await this.browser.typeInto('barcode__0', '1234567890');
        await this.browser.typeInto('longName_ru', 'long name');
        await this.browser.typeInto('shortNameLoc_ru', 'long name');
        await this.browser.typeInto('markCount', '1');
        await this.browser.typeInto('markCountUnit', '1');
        await this.browser.clickInto('nomenclatureType');
        await this.browser.clickInto(['nomenclatureType_dropdown-menu', 'product']);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.PRODUCT('\\d')));
    });

    it('Может создавать фронт-категории', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.typeInto('code', 'test_code');
        await this.browser.typeInto('name', 'Test name');

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.FRONT_CATEGORY('\\d')));
    });

    it('Может создавать мета-товары', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto('create-button');
        await this.browser.clickInto(['create-product-menu', 'create-meta'], {waitNavigation: true});

        await this.browser.typeInto('longName_ru', 'long name');
        await this.browser.typeInto('shortNameLoc_ru', 'long name');
        await this.browser.uploadFileInto('file-input', createImageFile('img1.png'));

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.PRODUCT('\\d')));
    });

    it('Не может открыть страницу балковых действий', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto(['products-table-row_10000001', 'checkbox']);
        await this.browser.assertImage('products-bottom-panel', {removeShadows: true});
    });

    it('Не может открыть страницу импорта по прямой ссылке', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.waitForTestIdSelectorInDom('not-found');
    });

    it('Не может перейти к импорту продуктов по кнопке из интерфейса', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.assertImage('action-bar');
    });

    it('Не может перейти к импорту инфомоделей по кнопке из интерфейса', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.assertImage('action-bar');
    });

    it('Может создавать атрибуты', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.typeInto('code', 'test_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-123456789');

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.ATTRIBUTE('\\d')));
    });

    it('Может создавать комбинации товаров', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS_CREATE);

        await this.browser.clickInto('base.type', {waitRender: true});
        await this.browser.clickInto(['base.type_dropdown-menu', 'discount']);
        await this.browser.clickInto(['groups-parameters', 'search'], {waitRender: true});
        await this.browser.clickInto('product-combo-option_10000001');
        await this.browser.clickInto('product-combo-option_10000002');

        await this.browser.clickInto(['base.status', 'active']);
        await this.browser.typeInto('groups.0.nameTranslations.ru', 'Test group');

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.PRODUCT_COMBO('\\d')));
    });

    it('Не может открыть импорт в Израиле', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS, {region: 'il'});
        await this.browser.waitForTestIdSelectorInDom('not-found');
    });

    it('Может создать товар в Израиле', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS_CREATE, {region: 'il'});
        await this.browser.clickInto('row_master_category_code_4_0', {waitForClickable: true});
        await this.browser.clickInto('row_master_category_code_20_0', {waitForClickable: true});
        await this.browser.clickInto('row_master_category_code_55_0', {waitForClickable: true});
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});

        await this.browser.clickInto('add_new_barcode');
        await this.browser.typeInto('barcode__0', '1234567890');
        await this.browser.typeInto('longName_he', 'long name');
        await this.browser.typeInto('shortNameLoc_he', 'long name');
        await this.browser.typeInto('longName_en', 'long name');
        await this.browser.typeInto('shortNameLoc_en', 'long name');
        await this.browser.typeInto('longName_ru', 'long name');
        await this.browser.typeInto('shortNameLoc_ru', 'long name');
        await this.browser.typeInto('markCount', '1');
        await this.browser.typeInto('markCountUnit', '1');
        await this.browser.clickInto('nomenclatureType');
        await this.browser.clickInto(['nomenclatureType_dropdown-menu', 'product']);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.PRODUCT('\\d')));
    });
});

async function makeUnusedAttributes(ctx: Hermione.TestContext) {
    await ctx.browser.executeSql(
        `
        DELETE FROM ${DbTable.INFO_MODEL_ATTRIBUTE}
        WHERE attribute_id IN (
            ${[
                attributes.text_attribute_code_6_2_loc,
                attributes.text_attribute_code_6_0,
                attributes.boolean_attribute_code_0_0
            ].join()}
        ) AND info_model_id = ${infoModels.ru.info_model_code_1_15}
        `
    );
}

describe('Роль с доступом к группе атрибутов', function () {
    const rules: Rules = {product: {canEditAttributeGroup: ['attribute_group_code_1']}};

    it('Может редактировать разрешенные атрибуты', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));

        await this.browser.assertImage('attribute_group_code_1', {removeShadows: true});

        await this.browser.clickInto('multiselect_attribute_code_2_0');
        await this.browser.clickInto(['multiselect_attribute_code_2_0_dropdown-menu', 'attribute_option_code_10_2']);
        await this.browser.clickInto('multiselect_attribute_code_2_0');

        const arrayImage = await this.browser.findByTestId(['image_attribute_code_1_1-array', 'image-drag-0']);
        await arrayImage.moveTo();
        await this.browser.clickInto(['image_attribute_code_1_1-array', 'image-drag-0', 'delete-image']);

        const image = await this.browser.findByTestId('image_attribute_code_1_0');
        await image.moveTo();
        await this.browser.clickInto(['image_attribute_code_1_0', 'delete-image']);

        await this.browser.clickInto('boolean_attribute_code_0_0_off');
        await this.browser.clickInto('boolean_attribute_code_0_1_off');

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));

        await this.browser.assertImage('attribute_group_code_1', {removeShadows: true});
    });

    it('Не может редактировать атрибуты других групп', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));

        await this.browser.assertImage('basic-attributes', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_2', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_3', {removeShadows: true});
        await this.browser.assertImage('without-group', {removeShadows: true});
        await this.browser.assertImage('substitutions-container', {removeShadows: true});
    });

    it('Может редактировать неиспользуемые атрибуты только из доступной группы', async function () {
        await makeUnusedAttributes(this);
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));
        await this.browser.assertImage('unused-attributes', {removeShadows: true});

        await this.browser.clickInto('boolean_attribute_code_0_0_off');

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));

        await this.browser.assertImage('unused-attributes', {removeShadows: true});
    });
});

describe('Роль с запретом доступа к группе атрибутов', function () {
    const rules: Rules = {product: {canEditAttributeAll: true, canNotEditAttributeGroup: ['attribute_group_code_1']}};

    it('Не может редактировать атрибуты из запрещенной группы', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));

        await this.browser.assertImage('attribute_group_code_1', {removeShadows: true});
    });

    it('Может редактировать атрибуты других групп', async function () {
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));

        await this.browser.assertImage('attribute_group_code_2', {removeShadows: true});
        await this.browser.assertImage('without-group', {removeShadows: true});

        await this.browser.typeInto('text_attribute_code_6_2_loc_ru', 'some text', {clear: true});
        await this.browser.typeInto('number_attribute_code_3_0', '123');

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));

        await this.browser.assertImage('attribute_group_code_2', {removeShadows: true});
        await this.browser.assertImage('without-group', {removeShadows: true});
    });

    it('Не может редактировать неиспользуемые атрибуты из запрещенной группы', async function () {
        await makeUnusedAttributes(this);
        await this.browser.addUserRole({rules, clear: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));

        await this.browser.assertImage('unused-attributes', {removeShadows: true});
    });
});

describe('Последовательная выдача ролей', async function () {
    it('Роль с доступом до атрибутов на Израиль и глобальная роль с полным доступом', async function () {
        await this.browser.addUserRole({rules: {product: {canEditAttribute: ['markCount']}}, region: 'il'});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000151), {region: 'il'});

        await this.browser.assertImage('basic-attributes', {removeShadows: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.assertImage('basic-attributes', {removeShadows: true});
    });

    it('Роли с доступом к статусам на регион Россия и с доступом к смене фк на регион Израиль', async function () {
        await this.browser.addUserRole({rules: {product: {canEditStatus: true}}, region: 'ru'});
        await this.browser.addUserRole({rules: {product: {canEditFrontCategory: true}}, region: 'il'});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.assertImage('status');
        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true});

        await this.browser.assertImage('action-bar');
        await this.browser.assertImage('tree-table');

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000151), {region: 'il'});
        await this.browser.assertImage('status');
        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true});

        await this.browser.assertImage('action-bar');
        await this.browser.assertImage('tree-table');

        await this.browser.clickInto('account');
        await this.browser.assertImage('account-settings', {removeShadows: true});
    });

    it('Последовательная выдача двух разрешающих ролей на один регион', async function () {
        await this.browser.addUserRole({
            rules: {
                product: {
                    canEditMasterCategory: true,
                    canEditAttribute: ['markCount'],
                    canEditAttributeGroup: ['attribute_group_code_1']
                }
            },
            nameTranslationMap: {
                ru: 'Роль 1',
                en: 'Role 1'
            },
            region: 'ru'
        });
        await this.browser.addUserRole({
            rules: {
                product: {
                    canEditFrontCategory: true,
                    canEditAttribute: ['markCountUnit'],
                    canEditAttributeGroup: ['attribute_group_code_2']
                }
            },
            nameTranslationMap: {
                ru: 'Роль 2',
                en: 'Role 2'
            },
            region: 'ru'
        });
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));

        await this.browser.typeInto('markCount', '999', {clear: true});
        await this.browser.typeInto('markCountUnit', 'liter', {clear: true});
        await this.browser.clickInto('boolean_attribute_code_0_0_off');
        await this.browser.typeInto('number_attribute_code_3_0', '999', {clear: true});

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));

        await this.browser.assertImage('basic-attributes', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_1', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_2', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_3', {removeShadows: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true});

        await this.browser.clickInto('expand-all', {waitRender: true});
        await this.browser.clickInto('product_fc_row_front_category_code_6_0');

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));

        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true});

        await this.browser.assertImage('action-bar');
        await this.browser.assertImage('tree-table');

        await this.browser.clickInto('account');
        await this.browser.assertImage('account-settings', {removeShadows: true});
    });

    it('Последовательная выдача двух глобальных ролей', async function () {
        await this.browser.addUserRole({
            rules: {
                product: {
                    canEditStatus: true,
                    canEditAttribute: ['markCount'],
                    canEditAttributeGroup: ['attribute_group_code_1']
                }
            },
            nameTranslationMap: {
                ru: 'Роль 3',
                en: 'Role 3'
            },
            clear: true
        });
        await this.browser.addUserRole({
            rules: {
                product: {
                    canEditStatus: true,
                    canEditAttributeAll: true,
                    canNotEditAttribute: ['markCount', 'barcode'],
                    canNotEditAttributeGroup: ['attribute_group_code_1', 'attribute_group_code_3']
                }
            },
            nameTranslationMap: {
                ru: 'Роль 4',
                en: 'Role 4'
            }
        });
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));

        await this.browser.typeInto('markCount', '999', {clear: true});
        await this.browser.typeInto('markCountUnit', 'liter', {clear: true});
        await this.browser.clickInto('boolean_attribute_code_0_0_off');
        await this.browser.typeInto('number_attribute_code_3_0', '999', {clear: true});

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));

        await this.browser.assertImage('basic-attributes', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_1', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_2', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_3', {removeShadows: true});

        await this.browser.clickInto('account');
        await this.browser.assertImage('account-settings', {removeShadows: true});
    });

    it('Последовательная выдача двух запрещающих ролей на один регион', async function () {
        await this.browser.addUserRole({
            rules: {
                product: {
                    canEditStatus: true,
                    canEditAttributeAll: true,
                    canNotEditAttribute: ['markCount', 'barcode'],
                    canNotEditAttributeGroup: ['attribute_group_code_1', 'attribute_group_code_3']
                }
            },
            nameTranslationMap: {
                ru: 'Роль 4',
                en: 'Role 4'
            },
            region: 'il'
        });
        await this.browser.addUserRole({
            rules: {
                product: {
                    canEditAttributeAll: true,
                    canNotEditAttribute: ['markCountUnit', 'barcode'],
                    canNotEditAttributeGroup: ['attribute_group_code_2', 'attribute_group_code_3']
                }
            },
            nameTranslationMap: {
                ru: 'Роль 5',
                en: 'Role 5'
            },
            region: 'il'
        });
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000152), {region: 'il'});

        await this.browser.clickInto('active_label');
        await this.browser.typeInto('markCount', '999', {clear: true});
        await this.browser.typeInto('markCountUnit', 'liter', {clear: true});
        await this.browser.clickInto('boolean_attribute_code_0_0_off');
        await this.browser.typeInto('number_attribute_code_3_0', '999', {clear: true});

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000152), {region: 'il'});

        await this.browser.assertImage('basic-attributes', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_1', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_2', {removeShadows: true});
        await this.browser.assertImage('attribute_group_code_3', {removeShadows: true});

        await this.browser.clickInto('account');
        await this.browser.assertImage('account-settings', {removeShadows: true});
    });
});
