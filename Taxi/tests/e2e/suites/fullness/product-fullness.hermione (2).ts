import {openChangeAttributesBulkPage, openChangeMasterCategoryBulkPage, selectAttribute} from 'tests/e2e/helper/bulk';
import {masterCategories} from 'tests/e2e/seed-db-map';
import getFixturePath from 'tests/e2e/utils/fixture';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Полнота товаров', function () {
    it('Уменьшить полноту, добавив в ИМ новый обязательный атрибут', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000003));

        await this.browser.clickInto('infomodel-link', {waitRender: true, waitNavigation: true});
        await this.browser.clickInto('\\#rc-tabs-1-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['attributes-search'], {waitRender: true});
        await this.browser.typeInto('attributes-search', 'number_attribute_code_3_1', {clear: true});
        await this.browser.waitUntilRendered();
        await this.browser.clickInto(['attribute-select-virtual-list', 'number_attribute_code_3_1']);
        await this.browser.clickInto('im-user_attributes-table', {
            waitRender: true
        });
        await this.browser.clickInto(['infomodel-groups-table', 'im_attribute-group_row_attribute_group_code_2']);
        await this.browser.clickInto(['im_attribute_row_number_attribute_code_3_1', 'switch-important']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000003));
        await this.browser.assertImage('product-fullness');
    });

    it('Уменьшить полноту, сделав один из атрибутов ИМ обязательным', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000003));

        await this.browser.clickInto('infomodel-link', {waitRender: true, waitNavigation: true});
        await this.browser.clickInto('\\#rc-tabs-1-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['infomodel-groups-table', 'im_attribute-group_row_attribute_group_code_2']);
        await this.browser.clickInto(['im_attribute_row_select_attribute_code_4_0', 'switch-important']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000003));
        await this.browser.assertImage('product-fullness');
    });

    it('Увеличить полноту, убрав обязательный атрибут, Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000151), {region: 'il'});

        await this.browser.clickInto('infomodel-link', {waitRender: true, waitNavigation: true});
        await this.browser.clickInto('\\#rc-tabs-1-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['infomodel-groups-table', 'im_attribute-group_row_attribute_group_code_3']);
        await this.browser.clickInto(['im_attribute_row_string_attribute_code_5_1', 'switch-important']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000151), {region: 'il'});
        await this.browser.assertImage('product-fullness');
    });

    it('Изменить полноту, изменив МК товара через UI', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.clickInto(['basic-attributes', 'parent-category-modal__input'], {waitRender: true});
        await this.browser.clickInto(['hide-inactive']);
        await this.browser.clickInto(['row_master_category_code_5_1', '\\[class*=switcher]'], {waitRender: true});
        await this.browser.clickInto(['row_master_category_code_26_0', 'title'], {waitRender: true});
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
        await this.browser.assertImage('product-fullness');
    });

    it('Изменить полноту, изменив МК товара через импорт, Великобритания', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS, {region: 'gb'});
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('change-product-mc-in-gb.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');

        await this.browser.processTaskQueue();
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'gb',
            queryParams: {search: '10000051'}
        });
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Изменить полноту, изменив МК товара через балк', async function () {
        await openChangeMasterCategoryBulkPage(this, [10000001]);
        await this.browser.clickInto(['show-inactive']);
        await this.browser.clickInto('mc_row_master_category_code_1_0', {waitRender: true});
        await this.browser.clickInto('mc_row_master_category_code_5_1', {waitRender: true});
        await this.browser.clickInto('mc_row_master_category_code_26_0', {waitRender: true});
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');

        await this.browser.processTaskQueue();
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {queryParams: {search: '10000001'}});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Все типы атрибутов учитываются в полноте (кроме логических)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.clickInto(['multiselect_attribute_code_2_1', '\\[class*=select-clear]'], {waitRender: true});
        await this.browser.assertImage('product-fullness');

        await this.browser.clickInto('string_attribute_code_5_1__2_remove', {waitRender: true});
        await this.browser.clickInto('string_attribute_code_5_1__1_remove', {waitRender: true});
        await this.browser.clickInto('string_attribute_code_5_1__0_remove', {waitRender: true});
        await this.browser.assertImage('product-fullness');

        await this.browser.typeInto('number_attribute_code_3_0', '', {clear: true});
        await this.browser.assertImage('product-fullness');

        await this.browser.clickInto(['select_attribute_code_4_0', '\\[class*=select-clear]'], {waitRender: true});
        await this.browser.assertImage('product-fullness');

        await this.browser.typeInto('string_attribute_code_5_0', '', {clear: true});
        await this.browser.assertImage('product-fullness');
    });

    it('Полнота при локализуемых атрибутах, Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000113), {region: 'fr'});

        await this.browser.typeInto('string_attribute_code_5_2_loc_en', 'abc');
        await this.browser.assertImage('product-fullness');

        await this.browser.typeInto('string_attribute_code_5_2_loc_fr', 'abc');
        await this.browser.assertImage('product-fullness');
    });

    it('Изменить полноту через UI, Россия', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000005));

        await this.browser.typeInto('string_attribute_code_5_0', 'abc');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.processTaskQueue();
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {search: '10000005'}
        });
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Изменить полноту через импорт, Великобритания', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS, {region: 'gb'});
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('change-product-attribute-in-gb.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');

        await this.browser.processTaskQueue();
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'gb',
            queryParams: {search: '10000052'}
        });
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Изменить полноту через балк, Израиль', async function () {
        await openChangeAttributesBulkPage(this, [10000151], {region: 'il'});
        await selectAttribute(this, 'text_attribute_code_6_0');
        await this.browser.typeInto(['attributes-list', 'text_attribute_code_6_0'], 'abc');
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');

        await this.browser.processTaskQueue();
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'il', queryParams: {search: '10000151'}});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('При отсутствии обязательных атрибутов полнота 100%', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_25_0));
        await this.browser.typeInto(['info-model-select', '\\input'], 'Корневая инфо модель');
        await this.browser.clickInto(['info-model-select_dropdown-menu', '\\[label="Корневая инфо модель"]'], {
            waitRender: true
        });
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.processTaskQueue();
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {queryParams: {search: '10000041'}});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Фильтрация по полноте', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto('add-filter');
        await this.browser.clickInto(['filters-menu', 'fullness'], {waitRender: true});
        await this.browser.typeInto('input_list_for_fullness_0', '71');
        await this.browser.clickInto('filter-item-progress', {waitRender: true});

        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Полнота при английском языке интерфейса', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001), {uiLang: 'en'});
        await this.browser.assertImage('product-fullness-wrapper');
    });

    it('Полнота при французском языке интерфейса', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {uiLang: 'fr'});
        await this.browser.assertImage(['products-table', '\\thead']);
    });

    it('Увеличить полноту, изменив атрибут на true, через интерфейс', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));
        await this.browser.assertImage('product-fullness-wrapper');
        await this.browser.clickInto('boolean_attribute_code_0_1_on');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('product-fullness-wrapper');
    });

    it('Увеличить полноту, изменив атрибут на false, через балк', async function () {
        await openChangeAttributesBulkPage(this, [10000002]);
        await selectAttribute(this, 'boolean_attribute_code_0_1');
        await this.browser.clickInto('boolean_attribute_code_0_1_off');
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');

        await this.browser.processTaskQueue();
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {queryParams: {search: '10000002'}});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['products-table', 'products-table-row_10000002', 'fullness']);
    });

    it('Уменьшить полноту, изменив атрибут на "не определен", через импорт', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('change-boolean-attribute-from-false-to-unset.xlsx')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');

        await this.browser.processTaskQueue();
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {queryParams: {search: '10000002'}});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['products-table', 'products-table-row_10000002', 'fullness']);
    });

    it('При неполностью заполненном локализуемом атрибуте фильтр "не задано" выдает товары', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000106), {region: 'fr'});
        await this.browser.typeInto('text_attribute_code_6_2_loc_en', 'some text');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'fr',
            queryParams: {search: '10000106', filters: {text_attribute_code_6_2_loc: {rule: 'null'}}}
        });
        await this.browser.assertImage(['table-container', '\\tbody']);
    });

    it('Обнуление общей наполненности через UI в Великобритании', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000054), {region: 'gb'});
        await this.browser.typeInto('text_attribute_code_6_2_loc_en', '', {clear: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'gb',
            queryParams: {
                search: '10000054',
                columnIds: ['image', 'longNameLoc', 'localization'].join()
            }
        });

        await this.browser.assertImage(['products-table', '\\tbody', 'fullness']);
    });

    it('Уменьшение общей наполненности через балк', async function () {
        await openChangeAttributesBulkPage(this, [10000040], {queryParams: {search: '10000040'}});
        await selectAttribute(this, 'text_attribute_code_6_2_loc');

        await this.browser.typeInto('text_attribute_code_6_2_loc_ru', '', {clear: true});

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');

        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {search: '10000040', columnIds: ['image', 'longNameLoc', 'localization'].join()}
        });

        await this.browser.assertImage(['products-table', '\\tbody', 'fullness']);
    });

    it('Увеличение общей наполненности через импорт', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('change-product-localization.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');

        await this.browser.processTaskQueue();
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {search: '10000020', columnIds: ['image', 'longNameLoc', 'localization'].join()}
        });
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['products-table', 'fullness']);
    });

    it('Обнуление наполненности по английской локали товара Франции через UI', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000115), {region: 'fr'});
        await this.browser.typeInto('text_attribute_code_6_2_loc_en', '', {clear: true});
        await this.browser.clickInto(['header-panel', 'submit-button']);

        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'fr',
            queryParams: {search: '10000115', columnIds: ['image', 'longNameLoc', 'localization_en'].join()}
        });

        await this.browser.assertImage(['products-table', '\\tbody', 'localization_en']);
    });

    it('Уменьшение наполненности по локали иврит товара Израиля через балк', async function () {
        await openChangeAttributesBulkPage(this, [10000192], {region: 'il', queryParams: {search: '10000192'}});
        await selectAttribute(this, 'text_attribute_code_6_2_loc');

        await this.browser.typeInto('text_attribute_code_6_2_loc_he', '', {clear: true});

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');

        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'il',
            queryParams: {search: '10000192', columnIds: ['image', 'longNameLoc', 'localization_he'].join()}
        });

        await this.browser.assertImage(['products-table', '\\tbody', 'localization_he']);
    });

    it('Увеличение наполненности по английской локали товара Израиля через импорт', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS, {region: 'il'});
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('change-product-localizable-attribute.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');

        await this.browser.processTaskQueue();
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'il',
            queryParams: {search: '10000152', columnIds: ['image', 'longNameLoc', 'localization_en'].join()}
        });
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['products-table', 'localization_en']);
    });

    it('Для товара c пустой ИМ в Великобритании общая локализация равна 100%', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS_CREATE, {region: 'gb'});
        await this.browser.clickInto(['hide-inactive']);
        await this.browser.clickInto(['row_master_category_code_2_3', 'title'], {waitRender: true});
        await this.browser.clickInto(['row_master_category_code_13_0', 'title'], {waitRender: true});
        await this.browser.clickInto(['row_master_category_code_41_1', 'title'], {waitRender: true});
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});

        await this.browser.clickInto('add_new_barcode', {waitRender: true});
        await this.browser.typeInto('barcode__0', '0000000000000');
        await this.browser.typeInto('longNameLoc_en', 'Foo product');
        await this.browser.typeInto('shortNameLoc_en', 'Foo');
        await this.browser.typeInto('markCount', '12');
        await this.browser.typeInto('markCountUnit', 'gramm');
        await this.browser.clickInto('nomenclatureType');
        await this.browser.clickInto(['nomenclatureType_dropdown-menu', 'product']);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true, waitNavigation: true});

        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'gb',
            queryParams: {
                search: '0000000000000',
                columnIds: ['image', 'longNameLoc', 'localization'].join()
            }
        });

        await this.browser.assertImage(['products-table', '\\tbody', 'fullness']);
    });

    it('Для товара с пустой ИМ во Франции локализация по локалям равна "100% | 0/0"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS_CREATE, {region: 'fr'});
        await this.browser.clickInto(['hide-inactive']);
        await this.browser.clickInto(['row_master_category_code_3_3', 'title'], {waitRender: true});
        await this.browser.clickInto(['row_master_category_code_18_0', 'title'], {waitRender: true});
        await this.browser.clickInto(['row_master_category_code_51_1', 'title'], {waitRender: true});
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});

        await this.browser.clickInto('add_new_barcode', {waitRender: true});
        await this.browser.typeInto('barcode__0', '0000000000000');
        await this.browser.typeInto('longNameLoc_en', 'Foo product');
        await this.browser.typeInto('longNameLoc_fr', 'Foo product');
        await this.browser.typeInto('shortNameLoc_en', 'Foo');
        await this.browser.typeInto('shortNameLoc_fr', 'Foo');
        await this.browser.typeInto('markCount', '12');
        await this.browser.typeInto('markCountUnit', 'gramm');
        await this.browser.clickInto('nomenclatureType');
        await this.browser.clickInto(['nomenclatureType_dropdown-menu', 'product']);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true, waitNavigation: true});

        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'fr',
            queryParams: {
                search: '0000000000000',
                columnIds: ['image', 'longNameLoc', 'localization_fr', 'localization_en'].join()
            }
        });

        await this.browser.assertImage(['products-table', '\\tbody', 'localization_en']);
        await this.browser.assertImage(['products-table', '\\tbody', 'localization_fr']);
    });

    it('Общая локализация обновляется при изменении МК товара России', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000020));

        await this.browser.clickInto(['basic-attributes', 'parent-category-modal__input'], {waitRender: true});
        await this.browser.clickInto(['row_master_category_code_9_0', '\\[class*=switcher]'], {waitRender: true});
        await this.browser.clickInto(['row_master_category_code_33_1', 'title'], {waitRender: true});
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                search: '10000002',
                columnIds: ['image', 'longNameLoc', 'localization'].join()
            }
        });

        await this.browser.assertImage(['products-table', '\\tbody', 'fullness']);
    });

    it('Локализация по стране обновляется при изменении ИМ мастер-категории товара Франции', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.fr.master_category_code_52_0), {
            region: 'fr'
        });
        await this.browser.clickInto('info-model-select');
        await this.browser.clickInto(['info-model-select_dropdown-menu', 'im_node_compatible_root']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000115), {region: 'fr'});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'fr',
            queryParams: {
                search: '10000115',
                columnIds: ['image', 'longNameLoc', 'localization_fr', 'localization', 'fullness'].join()
            }
        });

        await this.browser.assertImage(['products-table', '\\tbody', 'localization_fr']);
    });
});
