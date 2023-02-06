import {productCombos, requiredAttributes} from 'tests/e2e/seed-db-map';
import createImageFile from 'tests/e2e/utils/create-image-file';
import makeAttributeConfirmable from 'tests/e2e/utils/make-attribute-confirmable';
import {describe, expect, it} from 'tests/hermione.globals';

import {META_PRODUCT_INFO_MODEL_CODE, META_PRODUCT_MASTER_CATEGORY_CODE} from '@/src/constants';
import {ROUTES} from '@/src/constants/routes';

describe('Мета-товары', function () {
    async function assertListItemImageStretched(ctx: Hermione.TestContext, selector: string) {
        const container = await ctx.browser.findByTestId('history-of-changes_list');

        await container.execute(
            (container, selector) => {
                if (container instanceof HTMLElement) {
                    container.style.removeProperty('height');
                    [...container.querySelectorAll('[data-testid^=list-item')]
                        .filter((it): it is HTMLElement => it instanceof HTMLElement)
                        .filter((it) => it.dataset.testid !== selector)
                        .forEach((it) => it.style.setProperty('display', 'none', 'important'));
                }
            },
            container,
            selector
        );

        await ctx.browser.assertImage(['history-of-changes_list', selector], {stretch: true});
    }

    it('Фильтр товаров по наличию свойства мета. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'il'});
        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});
        await this.browser.typeInto(['filters-menu', 'search'], 'мета');
        await this.browser.clickInto(['filters-menu', 'is_meta'], {waitRender: true, waitForClickable: true});
        await this.browser.clickInto(['filter-list', 'boolean-picker', 'true'], {
            waitRender: true,
            waitForClickable: true
        });
        await this.browser.assertImage('base-layout-content');
    });

    it('Фильтр товаров по отсутствию свойства мета', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {queryParams: {filters: {is_meta: {values: false}}}});
        await this.browser.assertImage('base-layout-content');
    });

    it('Открытие фильтра товаров по наличию свойства мета по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {queryParams: {filters: {is_meta: {values: true}}}});
        await this.browser.assertImage('base-layout-content');
    });

    it('Отключение отображения свойства мета в таблице товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {queryParams: {filters: {is_meta: {values: true}}}});
        await this.browser.clickInto('table-settings-button', {waitRender: true});
        await this.browser.typeInto(['columns-menu', 'search'], 'мета');
        await this.browser.clickInto(['columns-menu', 'is_meta'], {waitRender: true, waitForClickable: true});
        await this.browser.clickInto('filter-list', {waitRender: true});
        await this.browser.assertImage('base-layout-content');
    });

    it('Удаление фильтра по мета-товарам', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {queryParams: {filters: {is_meta: {values: true}}}});
        await this.browser.clickInto(['filter-item-is-meta', 'delete'], {waitRender: true});
        await this.browser.assertImage('base-layout-content');
    });

    it('Поиск мета-товара по ID', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {filters: {is_meta: {values: true}, id: {rule: 'equal', values: 10000201}}}
        });
        await this.browser.clickInto(['filter-item-is-meta', 'delete'], {waitRender: true});
        await this.browser.assertImage('base-layout-content');
    });

    it('Показ в таблице товаров мастер-категорий и инфомоделей для метатоваров. Великобритания', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                filters: {
                    is_meta: {values: true}
                },
                columnIds: ['longName', 'image', 'is_meta', 'info_model', 'master_category'].join()
            },
            region: 'gb'
        });
        await this.browser.assertImage('base-layout-content');
    });

    it('Нельзя найти скрытую мастер-категорию поиском по списку мастер-категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'master_category'], {waitRender: true, waitForClickable: true});
        await this.browser.typeInto(['filter-list', 'category-picker', 'search_input'], 'мета');

        await this.browser.assertImage(['filter-list', 'category-picker']);
    });

    it('Нельзя найти скрытую инфомодель поиском по списку инфомоделей', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'info_model'], {waitRender: true, waitForClickable: true});
        await this.browser.typeInto(['filter-list', 'info-model-list', 'search-input'], 'мета');

        await this.browser.assertImage(['filter-list', 'info-model-list'], {removeShadows: true});
    });

    it('Открытие страницы создания мета-товара по прямой ссылке', async function () {
        await this.browser.openPage([ROUTES.CLIENT.PRODUCTS_CREATE, 'meta'].join('?'));
        await this.browser.assertImage('header-panel');
        await this.browser.assertImage('base-layout-content');
    });

    it('Страница мета-товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000201));
        await this.browser.waitForTestIdSelectorInDom('product-fullness');
        await this.browser.assertImage('base-layout-content');
    });

    it('Нельзя создать мастер-категорию с зарезервированным кодом скрытой мастер-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY, {patchStyles: {enableNotifications: true}});
        const currentUrl = await this.browser.getUrl();
        await this.browser.typeInto('code', META_PRODUCT_MASTER_CATEGORY_CODE);
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('notification');

        expect(await this.browser.getUrl()).to.equal(currentUrl);
        await this.browser.assertImage('notification', {removeShadows: true});
    });

    it('Нельзя создать инфомодель с зарезервированным кодом скрытой инфомодели', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL, {patchStyles: {enableNotifications: true}});
        const currentUrl = await this.browser.getUrl();
        await this.browser.typeInto('code', META_PRODUCT_INFO_MODEL_CODE);
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('notification');

        expect(await this.browser.getUrl()).to.equal(currentUrl);
        await this.browser.assertImage('notification', {removeShadows: true});
    });

    it('Нельзя создать мета-товар без изображения через интерфейс', async function () {
        await this.browser.openPage([ROUTES.CLIENT.PRODUCTS_CREATE, 'meta'].join('?'));
        const currentUrl = await this.browser.getUrl();
        await this.browser.typeInto('longName_ru', 'foo');
        await this.browser.typeInto('shortNameLoc_ru', 'foo');
        await this.browser.clickInto('submit-button');

        expect(await this.browser.getUrl()).to.equal(currentUrl);
        await this.browser.waitForTestIdSelectorEnabled('submit-button');
        await this.browser.assertImage('product-image');
    });

    it('Нельзя создать мета-товар без системных атрибутов через интерфейс. Израиль', async function () {
        await this.browser.openPage([ROUTES.CLIENT.PRODUCTS_CREATE, 'meta'].join('?'), {region: 'il'});
        const currentUrl = await this.browser.getUrl();
        await this.browser.typeInto('longName_ru', 'foo');
        await this.browser.typeInto('shortNameLoc_ru', 'foo');
        await this.browser.uploadFileInto(['product-image', 'file-input'], createImageFile('test_meta_product-1.png'));
        await this.browser.waitForTestIdSelectorInDom(['product-image', 'thumbnail']);
        await this.browser.clickInto('submit-button', {waitRender: true});

        expect(await this.browser.getUrl()).to.equal(currentUrl);
        await this.browser.waitForTestIdSelectorEnabled('submit-button');
        await this.browser.assertImage('basic-attributes', {removeShadows: true});
    });

    it('Нельзя удалить изображение у мета-товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000201));
        await this.browser.clickInto(['product-image', 'image-drag-0', 'delete-image'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('product-image');
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000201));
        await this.browser.assertImage('product-image');
    });

    it('Нельзя стереть значения системных атрибутов у мета-товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000201));
        await this.browser.typeInto('longName_ru', '', {clear: true});
        await this.browser.typeInto('shortNameLoc_ru', '', {clear: true, blur: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('basic-attributes', {removeShadows: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000201));
        await this.browser.assertImage('basic-attributes', {removeShadows: true});
    });

    it('Редактирование всех атрибутов мета-товара с проверкой истории. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000210), {
            region: 'il',
            clearLocalStorage: true,
            localStorageItems: {
                frontCategoryProductList: {
                    isAllSelected: false,
                    isAllActive: true,
                    isAllCollapsed: false,
                    isAllExpanded: true
                }
            }
        });

        await this.browser.clickInto(['status', 'active']);

        await this.browser.typeInto('longName_ru', 'foo', {clear: true});
        await this.browser.typeInto('shortNameLoc_ru', 'bar', {clear: true, blur: true});

        await this.browser.clickInto(['product-image', 'image-drag-0', 'delete-image'], {waitRender: true});
        await this.browser.uploadFileInto(['product-image', 'file-input'], createImageFile('test_meta_product-2.png'));
        await this.browser.waitForTestIdSelectorInDom(['product-image', 'thumbnail']);

        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true});
        await this.browser.clickInto(['product_fc_row_front_category_code_65_2', 'checkbox']);
        await this.browser.clickInto(['product_fc_row_front_category_code_65_3', 'checkbox']);

        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom('submit-button');

        await this.browser.clickInto('\\#rc-tabs-0-tab-parameters', {waitForClickable: true});
        await this.browser.assertImage('base-layout-content');

        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await assertListItemImageStretched(this, 'list-item-2');
    });

    it('Создание активного мета-товара - с добавлением фк', async function () {
        await this.browser.openPage([ROUTES.CLIENT.PRODUCTS_CREATE, 'meta'].join('?'), {
            clearLocalStorage: true
        });

        await this.browser.typeInto('longName_ru', 'foo', {clear: true});
        await this.browser.typeInto('shortNameLoc_ru', 'bar', {clear: true, blur: true});
        await this.browser.uploadFileInto(['product-image', 'file-input'], createImageFile('test_meta_product-3.png'));
        await this.browser.waitForTestIdSelectorInDom(['product-image', 'thumbnail']);

        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories-tab', {waitRender: true});
        await this.browser.clickInto('product_fc_row_front_category_code_1_0', {waitRender: true});
        await this.browser.clickInto(['product_fc_row_front_category_code_5_0', 'checkbox']);

        await this.browser.clickInto('submit-button', {waitRender: true, waitNavigation: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.PRODUCT('\\d+')));
        await this.browser.assertImage('base-layout-content', {ignoreElements: '[data-testid=product_id]'});
    });

    it('Нельзя изменить мастер-категорию у мета-товара балком', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {queryParams: {filters: {is_meta: {values: true}}}});
        await this.browser.clickInto(['products-table-row_10000201', 'checkbox']);
        await this.browser.clickInto(['products-bottom-panel', 'bulk-edit'], {waitForClickable: true});
        await this.browser.clickInto('change-master-category', {waitForClickable: true});
        await this.browser.clickInto('mc_row_master_category_code_1_0', {waitRender: true});
        await this.browser.clickInto('mc_row_master_category_code_5_0', {waitRender: true});
        await this.browser.clickInto('mc_row_master_category_code_25_0', {waitRender: true});
        await this.browser.clickInto('submit-button');

        await this.browser.waitForTestIdSelectorInDom('import-info-ignore');
        await this.browser.waitForTestIdSelectorDisabled('submit-button');
        await this.browser.clickInto(['import-info-ignore', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('import-cell-tooltip-help-icon', {waitRender: true});
        await this.browser.assertImage('import-info-ignore');
    });

    it('Нельзя изменить markCountUnit, markCount у мета-товара балком', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {queryParams: {filters: {is_meta: {values: true}}}});
        await this.browser.clickInto(['products-table-row_10000201', 'checkbox']);
        await this.browser.clickInto(['products-bottom-panel', 'bulk-edit'], {waitForClickable: true});
        await this.browser.clickInto('change-attributes-values', {waitForClickable: true});
        await this.browser.clickInto('add-attribute', {waitRender: true});
        await this.browser.typeInto(['select-user-attributes', 'search'], 'mark');
        await this.browser.clickInto(['select-user-attributes', 'markCount']);
        await this.browser.clickInto(['select-user-attributes', 'markCountUnit']);
        await this.browser.assertImage('select-user-attributes', {removeShadows: true});
    });

    it('Нельзя удалить обязательные атрибуты у мета-товара балком. Великобритания', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {filters: {is_meta: {values: true}}},
            region: 'gb'
        });
        await this.browser.clickInto(['products-table-row_10000204', 'checkbox']);
        await this.browser.clickInto(['products-bottom-panel', 'bulk-edit'], {waitForClickable: true});
        await this.browser.clickInto('change-attributes-values', {waitForClickable: true});
        await this.browser.clickInto('add-attribute', {waitRender: true});
        await this.browser.typeInto(['select-user-attributes', 'search'], 'longName');
        await this.browser.clickInto(['select-user-attributes', 'longName'], {waitForClickable: true});
        await this.browser.clickInto(['confirm-select'], {waitRender: true});
        await this.browser.typeInto('longName_en', '', {clear: true});

        await this.browser.clickInto('submit-button');
        await this.browser.assertImage('attributes-list');
    });

    it('Редактирование атрибутов у мета-товара балком', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {queryParams: {filters: {is_meta: {values: true}}}});
        await this.browser.clickInto(['products-table-row_10000201', 'checkbox']);
        await this.browser.clickInto(['products-bottom-panel', 'bulk-edit'], {waitForClickable: true});
        await this.browser.clickInto('change-attributes-values', {waitForClickable: true});

        await this.browser.clickInto('add-attribute', {waitRender: true});
        await this.browser.typeInto(['select-user-attributes', 'search'], 'longName', {clear: true});
        await this.browser.clickInto(['select-user-attributes', 'longName'], {waitForClickable: true});
        await this.browser.typeInto(['select-user-attributes', 'search'], 'shortNameLoc', {clear: true});
        await this.browser.clickInto(['select-user-attributes', 'shortNameLoc'], {waitForClickable: true});
        await this.browser.clickInto(['confirm-select'], {waitRender: true});

        await this.browser.typeInto('longName_ru', 'foo', {clear: true});
        await this.browser.typeInto('shortNameLoc_ru', 'bar', {clear: true});

        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-info-update');

        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');

        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');
    });

    it('Ссылка на связанную комбинацию открывается в новом окне', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000201));

        await this.browser.clickInto([
            'linked-product-combos',
            'pigeon_combo_b6b0eb6f-c701-4aa2-a830-910f5745f6aa',
            'product-combo-link'
        ]);

        const handles = await this.browser.getWindowHandles();
        expect(handles.length).to.equal(2);

        await this.browser.switchToWindow(handles[1]);
        expect(await this.browser.getUrl()).to.match(
            new RegExp(ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['b6b0eb6f-c701-4aa2-a830-910f5745f6aa']))
        );

        await this.browser.closeWindow();
        await this.browser.switchToWindow(handles[0]);
    });

    // eslint-disable-next-line max-len
    it('МП: В мета-товарах нет UI функционала подтверждаемости атрибутов (если у атрибутов есть свойство подтверждаемости)', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});
        await makeAttributeConfirmable(this.browser, requiredAttributes.longName);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000201));

        await this.browser.assertImage('base-layout-content');
    });
});
