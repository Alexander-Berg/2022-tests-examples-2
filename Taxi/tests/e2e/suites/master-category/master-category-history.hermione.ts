import getEntityIdFromUrl from 'tests/e2e/helper/get-entity-id-from-url';
import {masterCategories} from 'tests/e2e/seed-db-map';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

const MASTER_CATEGORY_ID = 65;
const MASTER_CATEGORY_ID_IN_UK = 35;

describe('История изменений мастер-категории', function () {
    async function assertListItemImageStretched(ctx: Hermione.TestContext, selector: string) {
        const initialSize = await ctx.browser.getWindowSize();
        const container = await ctx.browser.findByTestId('history-of-changes_list');

        await container.execute((container) => {
            if (container instanceof HTMLElement) {
                container.style.removeProperty('height');
            }
        }, container);

        await ctx.browser.setWindowSize(initialSize.width, 9999);
        await ctx.browser.assertImage(['history-of-changes_list', selector]);
        await ctx.browser.setWindowSize(initialSize.width, initialSize.height);
    }

    it('Запись о создании подкатегории с наследуемой инфомоделью', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.waitUntilRendered();

        await this.browser.clickInto('parent-category-modal__input');
        const path = ['row_master_category_code_1_0', 'row_master_category_code_5_0'];
        for (const mc of path) {
            await this.browser.clickInto([mc, '\\.ant-tree-switcher'], {waitRender: true});
        }
        await this.browser.clickInto('row_master_category_code_25_0', {waitRender: true});
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
        await this.browser.typeInto('code', 'subcategory_code');
        await this.browser.clickInto('submit-button', {waitRender: true});

        // Вы создаёте первую подкатегорию «subcategory_code» в категории «Несло бы иной»,
        // все товары из категории «Несло бы иной» будут перемещены в неё.
        // Вы действительно хотите переместить 3 позиции?
        await this.browser.clickInto('confirmation-modal__ok-button');
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitForClickable: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись о создании мастер-категории в корне с конкретной инфомоделью. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY, {region: 'il'});
        await this.browser.waitUntilRendered();

        await this.browser.typeInto('code', 'subcategory_code');
        await this.browser.clickInto('info-model-select', {waitRender: true});
        await this.browser.clickInto('im_node_compatible_info_model_code_4_1', {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitForClickable: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Наличие автора, времени и способа изменений в истории мастер-категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(MASTER_CATEGORY_ID));
        await this.browser.waitUntilRendered();

        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitForClickable: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage('history-of-changes_list');
    });

    it('Запись о смене статуса мастер-категории со страницы списка мастер-категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.waitUntilRendered();

        await this.browser.clickInto(['mc_row_master_category_code_1_0', 'expand_icon'], {waitForClickable: true});
        await this.browser.clickInto(['mc_row_master_category_code_5_0', 'expand_icon'], {waitForClickable: true});
        await this.browser.clickInto(['mc_row_master_category_code_25_0', 'category-row-more-button'], {
            waitForClickable: true
        });
        await this.browser.clickInto(['more-menu', 'disable'], {waitForClickable: true});
        await this.browser.clickInto('mc_row_master_category_code_25_0', {x: -200, waitNavigation: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitForClickable: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись об изменении sort-order для мастер-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(MASTER_CATEGORY_ID));
        await this.browser.waitUntilRendered();

        await this.browser.typeInto('sort-order', '2', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitForClickable: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись о смене инфомодели у мастер-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(MASTER_CATEGORY_ID));
        await this.browser.waitUntilRendered();

        await this.browser.clickInto('info-model-select', {waitRender: true});
        await this.browser.clickInto('im_node_compatible_info_model_code_1_10', {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitForClickable: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись о добавлении названия мастер-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.waitUntilRendered();

        await this.browser.typeInto('code', 'subcategory_code');
        await this.browser.typeInto(['translations', 'ru', 'name'], 'New name');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitForClickable: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись о удалении описания мастер-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(MASTER_CATEGORY_ID));
        await this.browser.waitUntilRendered();

        await this.browser.typeInto('description', '', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitForClickable: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись о смене названия мастер-категории. Великобритания', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(MASTER_CATEGORY_ID_IN_UK), {region: 'gb'});
        await this.browser.waitUntilRendered();

        await this.browser.typeInto(['translations', 'en', 'name'], 'Changed name', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitForClickable: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Поиск по истории мастер-категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(MASTER_CATEGORY_ID));
        await this.browser.waitUntilRendered();

        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitRender: true});
        await this.browser.typeInto('history-of-changes_search', 'несло');

        await this.browser.assertImage(['query-state-spinner', 'query-state-spinner']);
    });

    it('Удаленная из системы бывшая ИМ в истории МК', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL);
        await this.browser.typeInto('code', 'info_model_code');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        const infoModelUrl = await this.browser.getUrl();
        const infoModeId = getEntityIdFromUrl(infoModelUrl);

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_25_0));
        await this.browser.typeInto(['info-model-select', '\\input'], 'info_model_code');
        await this.browser.clickInto(['info-model-select_dropdown-menu', 'im_node_compatible_info_model_code']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.typeInto(['info-model-select', '\\input'], 'По восхваляющих великие');
        await this.browser.clickInto(['info-model-select_dropdown-menu', 'im_node_compatible_info_model_code_1_14']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModeId));
        await this.browser.clickInto(['header-panel', 'delete-button'], {waitRender: true});
        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_25_0));
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab');
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await assertListItemImageStretched(this, 'list-item-3');
    });

    it('Удаленная из системы бывшая родительская категория в истории МК', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.typeInto('code', 'parent_category_code');
        await this.browser.clickInto(['status', 'disabled']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        const parentCategoryUrl = await this.browser.getUrl();
        const parentCategoryId = getEntityIdFromUrl(parentCategoryUrl);

        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.typeInto('code', 'category_code');
        await this.browser.clickInto('parent-category-modal__input');
        await this.browser.clickInto(['hide-inactive']);
        await this.browser.clickInto(['row_parent_category_code', 'title']);
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        const categoryUrl = await this.browser.getUrl();
        const categoryId = getEntityIdFromUrl(categoryUrl);

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto('expand-all', {waitRender: true});
        await this.browser.dragAndDrop('mc_row_category_code', 'mc_row_master_category_code_34_0', {offset: 'top'});
        await this.browser.clickInto('confirmation-modal__ok-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(parentCategoryId));
        await this.browser.clickInto(['header-panel', 'delete-button'], {waitRender: true});
        await this.browser.clickInto('confirmation-modal__ok-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(categoryId));
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab');
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await assertListItemImageStretched(this, 'list-item-2');
    });

    it('Поиск удаленной ИМ в истории категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL);
        await this.browser.typeInto('code', 'test_info_model_code');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        const infoModelUrl = await this.browser.getUrl();
        const infoModeId = getEntityIdFromUrl(infoModelUrl);

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_25_0));
        await this.browser.typeInto(['info-model-select', '\\input'], 'test_info_model_code');
        await this.browser.clickInto(['info-model-select_dropdown-menu', 'im_node_compatible_test_info_model_code']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.typeInto(['info-model-select', '\\input'], 'По восхваляющих великие');
        await this.browser.clickInto(['info-model-select_dropdown-menu', 'im_node_compatible_info_model_code_1_14']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModeId));
        await this.browser.clickInto(['header-panel', 'delete-button'], {waitRender: true});
        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_25_0));
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab');
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await this.browser.typeInto('history-of-changes_search', 'test_info_model_code');
        await this.browser.assertImage('history-of-changes_list', {stretch: true});
    });
});
