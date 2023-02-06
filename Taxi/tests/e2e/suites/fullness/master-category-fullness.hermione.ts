import {openChangeAttributesBulkPage, selectAttribute} from 'tests/e2e/helper/bulk';
import {masterCategories} from 'tests/e2e/seed-db-map';
import getFixturePath from 'tests/e2e/utils/fixture';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Полнота мастер-категорий', function () {
    it('Общая и средняя полнота в таблице МК России', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);

        await this.browser.assertImage('tree-table');
    });

    it('Общая и средняя полнота в карточке МК Франции', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.fr.master_category_code_45_0), {
            region: 'fr'
        });

        await this.browser.assertImage(['master-category-tabs', '\\.ant-tabs-nav']);
    });

    it('Увеличить полноту до 100%, заполнив товар Франции через UI', async function () {
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

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.fr.master_category_code_45_0), {
            region: 'fr'
        });

        await this.browser.assertImage(['master-category-tabs', 'entity-info-bar']);

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES, {region: 'fr'});
        await this.browser.typeInto('search', 'master_category_code_45_0');
        await this.browser.waitUntilRendered();

        await this.browser.assertImage(['mc_row_master_category_code_45_0', 'total-fullness']);
    });

    it('Увеличить полноту до 50%, заполнив товар Израиля через балк', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000196), {region: 'il'});
        await this.browser.clickInto(['status', 'disabled_label']);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await openChangeAttributesBulkPage(this, [10000156], {region: 'il'});
        await selectAttribute(this, 'multiselect_attribute_code_2_0');
        await this.browser.clickInto('multiselect_attribute_code_2_0');
        await this.browser.clickInto(['multiselect_attribute_code_2_0_dropdown-menu', 'attribute_option_code_10_1']);

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('import-info-update');

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');
        await this.browser.clickInto('import-info-update', {waitRender: true});

        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.il.master_category_code_57_1), {
            region: 'il'
        });

        await this.browser.assertImage(['master-category-tabs', 'entity-info-bar']);

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES, {region: 'il'});
        await this.browser.typeInto('search', 'master_category_code_57_1');
        await this.browser.waitUntilRendered();

        await this.browser.assertImage(['mc_row_master_category_code_57_1', 'total-fullness']);
    });

    it('Уменьшить полноту до 0%, очистив товар Великобритании через импорт', async function () {
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

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.gb.master_category_code_37_1), {
            region: 'gb'
        });
        await this.browser.assertImage(['master-category-tabs', 'entity-info-bar']);

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES, {region: 'gb'});
        await this.browser.typeInto('search', 'master_category_code_37_1');
        await this.browser.waitUntilRendered();

        await this.browser.assertImage(['mc_row_master_category_code_37_1', 'total-fullness']);
    });

    it('Перенос товара изменяет полноту категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.clickInto('parent-category-modal__input');
        await this.browser.typeInto(['parent-category-modal', 'search_input'], 'Поняли назвал');
        await this.browser.clickInto(['parent-category-modal', 'row_master_category_code_27_1', 'title']);
        await this.browser.clickInto(['parent-category-modal', 'parent-category-modal__ok-button'], {waitRender: true});

        await this.browser.clickInto('multiselect_attribute_code_2_0');
        await this.browser.clickInto(['multiselect_attribute_code_2_0_dropdown-menu', 'attribute_option_code_10_1']);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_27_1));
        await this.browser.assertImage(['master-category-tabs', 'entity-info-bar']);

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_25_0));
        await this.browser.assertImage(['master-category-tabs', 'entity-info-bar']);
    });

    it('При добавлении неактивного товара полнота не изменяется', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000005));

        await this.browser.clickInto('parent-category-modal__input');
        await this.browser.typeInto(['parent-category-modal', 'search_input'], 'Возлюбил а');
        await this.browser.clickInto(['parent-category-modal', 'row_master_category_code_29_0', 'title']);
        await this.browser.clickInto(['parent-category-modal', 'parent-category-modal__ok-button'], {waitRender: true});

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_29_0));
        await this.browser.assertImage(['master-category-tabs', 'entity-info-bar']);
    });

    it('У пустой МК общая и средняя полнота равны 100%', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);

        await this.browser.typeInto('code', 'some_code');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.processTaskQueue();

        await this.browser.refresh();
        await this.browser.assertImage(['master-category-tabs', 'entity-info-bar']);
    });

    it('При деактивации товара категории ее полнота изменяется', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.clickInto(['status', 'disabled_label']);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_25_0));
        await this.browser.assertImage(['master-category-tabs', 'entity-info-bar']);
    });

    it('При заполнении неактивного товара категории ее полнота не изменяется', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));

        await this.browser.clickInto('boolean_attribute_code_0_1_on');

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_25_1));
        await this.browser.assertImage(['master-category-tabs', 'entity-info-bar']);
    });

    it('При изменении ИМ категории ее полнота изменяется', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_25_0));

        await this.browser.clickInto('info-model-select');
        await this.browser.typeInto(['info-model-select', '\\input'], 'Корневая');
        await this.browser.clickInto(['info-model-select_dropdown-menu', 'im_node_compatible_root']);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.processTaskQueue();

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_25_0));
        await this.browser.assertImage(['master-category-tabs', 'entity-info-bar']);
    });
});
