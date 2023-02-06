import {openChangeMasterCategoryBulkPage} from 'tests/e2e/helper/bulk';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Балковые действия для мастер-категорий', function () {
    it('Нельзя выбрать родительскую мастер-категорию', async function () {
        await openChangeMasterCategoryBulkPage(this, [10000001]);
        await this.browser.clickInto('mc_row_master_category_code_1_0', {waitRender: true});
        await this.browser.clickInto('mc_row_master_category_code_5_0', {waitRender: true});
        await this.browser.clickInto('mc_row_master_category_code_25_1', {waitRender: true});
        await this.browser.assertImage('tree-table');
    });

    it('Перенести все товары в другую МК', async function () {
        await openChangeMasterCategoryBulkPage(this, 'all');
        await this.browser.clickInto('mc_row_master_category_code_1_0', {waitRender: true});
        await this.browser.clickInto('mc_row_master_category_code_5_0', {waitRender: true});
        await this.browser.clickInto('mc_row_master_category_code_25_0', {waitRender: true});
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');
        await this.browser.clickInto('import-info-update', {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Изменить мастер-категорию нескольких товаров без изменения ИМ', async function () {
        const code = 'super_code';
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.typeInto('code', code);
        await this.browser.clickInto('info-model-select', {waitRender: true});
        await this.browser.typeInto(['info-model-select', '\\input'], 'Возникают вы');
        await this.browser.clickInto(['info-model-select_dropdown-menu', 'im_node_compatible_info_model_code_1_6']);
        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});

        await openChangeMasterCategoryBulkPage(this, [10000020, 10000040], {
            queryParams: {'filters[info_model][values]': '10'}
        });
        await this.browser.clickInto(`mc_row_${code}`, {waitRender: true});
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');
        await this.browser.clickInto('import-info-update', {waitRender: true});
        await this.browser.assertImage('import-info-update');

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000020));
        await this.browser.assertImage('parent-category-modal__input');
        await this.browser.assertImage('infomodel-link');
    });

    it('Смена мастер-категории с появлением неиспользуемых атрибутов', async function () {
        await openChangeMasterCategoryBulkPage(this, [10000001]);
        await this.browser.clickInto(['show-inactive']);
        await this.browser.clickInto('mc_row_master_category_code_1_4', {waitRender: true});
        await this.browser.clickInto('mc_row_master_category_code_9_0', {waitRender: true});
        await this.browser.clickInto('mc_row_master_category_code_33_1', {waitRender: true});
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');
        await this.browser.clickInto('import-info-update', {waitRender: true});
        await this.browser.assertImage('import-info-update');

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.waitForTestIdSelectorInDom(['product_view', 'unused-attributes']);
    });

    it('Показ неактивных категорий при изменении мастер-категорий', async function () {
        await openChangeMasterCategoryBulkPage(this, [10000001]);

        await this.browser.clickInto(['action-bar', 'show-inactive'], {waitRender: true});

        await this.browser.assertImage('tree-table');
    });

    it('Поиск неактивной мастер-категории по названию', async function () {
        await openChangeMasterCategoryBulkPage(this, [10000001]);
        await this.browser.clickInto(['show-inactive']);

        const masterCategoryName = 'Мог или';

        await this.browser.typeInto('search', masterCategoryName);

        await this.browser.assertImage(['list-holder', 'mc_row_master_category_code_1_3']);
    });

    it('Страница массового изменения мастер-категории', async function () {
        await openChangeMasterCategoryBulkPage(this, [10000001, 10000002]);

        await this.browser.assertImage('base-layout');
    });
});
