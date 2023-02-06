import {openChangeAttributesBulkPage, selectAttribute} from 'tests/e2e/helper/bulk';
import {infoModels, masterCategories} from 'tests/e2e/seed-db-map';
import getFixturePath from 'tests/e2e/utils/fixture';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Полнота инфомоделей', function () {
    it('Общая и средняя полнота в таблице ИМ России', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);

        await this.browser.assertImage(['infomodels-table', '\\thead']);
        await this.browser.assertImage(['infomodels-table', 'im_row_root']);
    });

    it('Общая и средняя полнота в карточке ИМ Израиля', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.il.info_model_code_4_19), {
            region: 'il'
        });

        await this.browser.assertImage(['info-model-tabs', 'entity-info-bar']);
    });

    it('У пустой только созданной ИМ общая и средняя полнота равны 100%', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL);

        await this.browser.typeInto('code', 'some_code');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.processTaskQueue();

        await this.browser.refresh();
        await this.browser.assertImage(['info-model-tabs', 'entity-info-bar']);
    });

    it('У пустой ИМ, которую удалили из МК, полнота равна 100%', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_25_0));
        await this.browser.clickInto('info-model-select');
        await this.browser.clickInto(['info-model-select_dropdown-menu', 'im_node_compatible_info_model_code_1_13']);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_14));
        await this.browser.assertImage(['info-model-tabs', 'entity-info-bar']);
    });

    it('Увеличить общую полноту до 100%, заполнив товар Франции через UI', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000101), {region: 'fr'});
        await this.browser.typeInto('string_attribute_code_5_0', 'some text');
        await this.browser.typeInto('text_attribute_code_6_0', 'some another text');
        await this.browser.clickInto('multiselect_attribute_code_2_0');
        await this.browser.clickInto(['multiselect_attribute_code_2_0_dropdown-menu', 'attribute_option_code_10_1']);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000121), {region: 'fr'});
        await this.browser.typeInto('string_attribute_code_5_0', 'some text');
        await this.browser.typeInto('text_attribute_code_6_0', 'some another text');

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000141), {region: 'fr'});
        await this.browser.typeInto('string_attribute_code_5_0', 'some text');
        await this.browser.typeInto('text_attribute_code_6_0', 'some another text');

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.fr.info_model_code_3_14), {
            region: 'fr'
        });
        await this.browser.assertImage(['info-model-tabs', 'entity-info-bar']);

        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS, {
            region: 'fr',
            queryParams: {search: 'info_model_code_3_14'}
        });
        await this.browser.assertImage(['im_row_info_model_code_3_14', 'total-fullness', 'fullness']);
    });

    it('Увеличить общую полноту до 50%, заполнив товар России через балк', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.clickInto(['status', 'disabled_label']);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await openChangeAttributesBulkPage(this, [10000021], {queryParams: {search: '10000021'}});
        await selectAttribute(this, 'string_attribute_code_5_0');
        await this.browser.typeInto('string_attribute_code_5_0', 'test');

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('import-info-update');

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');
        await this.browser.clickInto('import-info-update', {waitRender: true});

        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_14));
        await this.browser.assertImage(['info-model-tabs', 'entity-info-bar']);

        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS, {queryParams: {search: 'info_model_code_1_14'}});
        await this.browser.assertImage(['im_row_info_model_code_1_14', 'total-fullness', 'fullness']);
    });

    it('Уменьшить общую полноту до 0%, очистив товар Великобритании через импорт', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS, {region: 'gb'});

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('clear-products-important-attributes.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');

        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.gb.info_model_code_2_19), {
            region: 'gb'
        });
        await this.browser.assertImage(['info-model-tabs', 'entity-info-bar']);

        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS, {
            region: 'gb',
            queryParams: {search: 'info_model_code_2_19'}
        });
        await this.browser.assertImage(['im_row_info_model_code_2_19', 'total-fullness', 'fullness']);
    });

    it('Перенос товара изменяет полноту ИМ', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.clickInto('parent-category-modal__input');
        await this.browser.typeInto(['parent-category-modal', 'search_input'], 'Поняли назвал');
        await this.browser.clickInto(['parent-category-modal', 'row_master_category_code_27_1', 'title']);
        await this.browser.clickInto(['parent-category-modal', 'parent-category-modal__ok-button'], {waitRender: true});

        await this.browser.clickInto('multiselect_attribute_code_2_0');
        await this.browser.clickInto(['multiselect_attribute_code_2_0_dropdown-menu', 'attribute_option_code_10_1']);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_14));
        await this.browser.assertImage(['info-model-tabs', 'entity-info-bar']);

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_19));
        await this.browser.assertImage(['info-model-tabs', 'entity-info-bar']);
    });

    it('При добавлении неактивного товара полнота ИМ не изменяется', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000005));

        await this.browser.clickInto('parent-category-modal__input');
        await this.browser.typeInto(['parent-category-modal', 'search_input'], 'Несло бы иной');
        await this.browser.clickInto(['parent-category-modal', 'row_master_category_code_25_0', 'title']);
        await this.browser.clickInto(['parent-category-modal', 'parent-category-modal__ok-button'], {waitRender: true});

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_14));
        await this.browser.assertImage(['info-model-tabs', 'entity-info-bar']);
    });

    it('При деактивации товара ИМ ее полнота изменяется', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.clickInto(['status', 'disabled_label']);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_14));
        await this.browser.assertImage(['info-model-tabs', 'entity-info-bar']);
    });

    it('При изменении полноты неактивного товара полнота ИМ не изменяется', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));

        await this.browser.clickInto('boolean_attribute_code_0_1_on');

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_15));
        await this.browser.assertImage(['info-model-tabs', 'entity-info-bar']);
    });

    it('При привязке ИМ к другой категории ее полнота изменяется', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_27_1));

        await this.browser.clickInto('info-model-select');
        await this.browser.typeInto(['info-model-select', '\\input'], 'По восхваляющих великие');
        await this.browser.clickInto(['info-model-select_dropdown-menu', 'im_node_compatible_info_model_code_1_14']);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_14));
        await this.browser.assertImage(['info-model-tabs', 'entity-info-bar']);
    });

    it('Изменение обязательности атрибута в ИМ изменяет ее полноту', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_14));

        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto('im_attribute-group_row_attribute_group_code_3');
        await this.browser.clickInto(['im_attribute_row_string_attribute_code_5_0', 'switch-important']);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.processTaskQueue();

        await this.browser.refresh();
        await this.browser.assertImage(['info-model-tabs', 'entity-info-bar']);
    });

    it('Добавление обязательного атрибута в ИМ изменяет ее полноту', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_14));

        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['attributes-search'], {waitRender: true});
        await this.browser.typeInto('attributes-search', 'string_attribute_code_5_2_loc', {clear: true});
        await this.browser.waitUntilRendered();
        await this.browser.clickInto(['attribute-select-virtual-list', 'string_attribute_code_5_2_loc']);
        await this.browser.clickInto('im-user_attributes-table', {
            waitRender: true
        });
        await this.browser.clickInto('im_attribute-group_row_attribute_group_code_3');
        await this.browser.clickInto(['im_attribute_row_string_attribute_code_5_2_loc', 'switch-important']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.processTaskQueue();

        await this.browser.refresh();
        await this.browser.assertImage(['info-model-tabs', 'entity-info-bar']);
    });
});
