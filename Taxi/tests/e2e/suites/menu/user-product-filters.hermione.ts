import makeDataTestIdSelector from 'tests/e2e/utils/make-data-test-id-selector';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

const menuPath = ['sidebar', 'menu'];

const search = '1000001';
const filters = {
    info_model: {values: 29},
    master_category: {values: 76},
    front_category: {values: 120},
    boolean_attribute_code_0_0: {values: false}
};
const columnIds = ['longName', 'barcode', 'image', 'status', 'shortNameLoc'].join();
const name = 'filter_name';

describe('Фильтры товаров', () => {
    it('Свернуть-развернуть сохранённые фильтры товаров. Великобритания', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'gb'});
        await this.browser.clickInto([...menuPath, 'products-menu-item', 'expand'], {waitRender: true});
        await this.browser.assertImage(menuPath);
        await this.browser.clickInto([...menuPath, 'products-menu-item', 'expand'], {waitRender: true});
        await this.browser.assertImage(menuPath);
    });

    it('Отменить сохранение фильтра товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {expandUserProductFilters: true});
        await this.browser.clickInto([...menuPath, 'add-user-product-filter'], {waitRender: true});
        await this.browser.clickInto(['form-modal', 'form-modal__cancel-button']);
        await this.browser.waitForTestIdSelectorNotInDom('form-modal');
    });

    it('Копирование ссылки при сохранении фильтра товаров. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            expandUserProductFilters: true,
            region: 'il',
            queryParams: {search}
        });
        const url = await this.browser.getUrl();
        await this.browser.clickInto([...menuPath, 'add-user-product-filter'], {waitRender: true});
        await this.browser.clickInto(['form-modal', 'copy-query'], {waitRender: true});
        await this.browser.assertImage('form-modal', {ignoreElements: makeDataTestIdSelector('query')});
        const inputElement = await this.browser.findByTestId(['form-modal', 'query']);
        const value = await inputElement.getValue();
        expect(value).to.equal(url);
    });

    it('Сохранение фильтра товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            expandUserProductFilters: true,
            queryParams: {search, filters}
        });
        await this.browser.clickInto([...menuPath, 'add-user-product-filter'], {waitRender: true});
        await this.browser.typeInto(['form-modal', 'name'], name);
        await this.browser.clickInto(['form-modal', 'form-modal__ok-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom([...menuPath, name]);
        await this.browser.assertImage(menuPath);
    });

    it('Открытие сохраненного фильтра товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            expandUserProductFilters: true,
            queryParams: {search, filters}
        });
        await this.browser.clickInto([...menuPath, 'add-user-product-filter'], {waitRender: true});
        await this.browser.typeInto(['form-modal', 'name'], name);
        await this.browser.clickInto(['form-modal', 'form-modal__ok-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            expandUserProductFilters: true
        });
        await this.browser.clickInto([...menuPath, name], {waitNavigation: true, waitRender: true});
        await this.browser.assertImage('filter-list');
    });

    it('Удаление сохраненного фильтра товаров. Великобритания', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            expandUserProductFilters: true,
            region: 'gb'
        });
        const element = await this.browser.findByTestId('product_filter_2_1');
        await element.moveTo();
        await this.browser.assertImage(menuPath);
        await this.browser.clickInto([...menuPath, 'product_filter_2_1', 'delete']);
        await this.browser.clickInto('confirmation-modal__ok-button', {waitRender: true, waitForClickable: true});
        await this.browser.assertImage(menuPath);
    });

    it('Редактирование сохраненного фильтра товаров. Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            expandUserProductFilters: true,
            region: 'fr'
        });
        const element = await this.browser.findByTestId('product_filter_3_1');
        await element.moveTo();
        await this.browser.assertImage(menuPath);
        await this.browser.clickInto([...menuPath, 'product_filter_3_1', 'settings'], {waitRender: true});
        await this.browser.typeInto(['form-modal', 'name'], 'new_name', {clear: true});
        await this.browser.clickInto(['form-modal', 'form-modal__ok-button'], {waitRender: true});
        await this.browser.assertImage(menuPath);
    });

    it('Скролл списка сохраненных фильтров. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            expandUserProductFilters: true,
            region: 'il'
        });
        await this.browser.performScroll('sub-menu_products-menu-item');
        await this.browser.assertImage('sidebar');
    });

    it('Переход к другому разделу меню при развернутом списке фильтров товаров. Великобритания', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'gb',
            expandUserProductFilters: true
        });
        await this.browser.clickInto([...menuPath, 'infomodels-menu-item'], {waitRender: true, waitNavigation: true});
        await this.browser.assertImage(menuPath);
    });

    it('Фильтры товаров не видны в другом регионе', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            expandUserProductFilters: true,
            queryParams: {search, filters}
        });

        await this.browser.clickInto([...menuPath, 'add-user-product-filter'], {waitRender: true});
        await this.browser.typeInto(['form-modal', 'name'], name);
        await this.browser.clickInto(['form-modal', 'form-modal__ok-button'], {waitRender: true});

        await this.browser.assertImage(menuPath, {screenshotDelay: 1000});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            expandUserProductFilters: true,
            region: 'gb'
        });

        await this.browser.assertImage(menuPath, {screenshotDelay: 1000});
    });

    it('Название сохраненного фильтра товаров уникально', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            expandUserProductFilters: true,
            queryParams: {search, filters}
        });
        await this.browser.clickInto([...menuPath, 'add-user-product-filter'], {waitRender: true});
        await this.browser.typeInto(['form-modal', 'name'], name);
        await this.browser.clickInto(['form-modal', 'form-modal__ok-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            expandUserProductFilters: true,
            queryParams: {filters},
            patchStyles: {enableNotifications: true}
        });
        await this.browser.clickInto([...menuPath, 'add-user-product-filter'], {waitRender: true});
        await this.browser.typeInto(['form-modal', 'name'], name);
        await this.browser.clickInto(['form-modal', 'form-modal__ok-button']);
        await this.browser.waitForTestIdSelectorInDom('notification');
        await this.browser.assertImage('notification', {removeShadows: true});
    });

    it('Нельзя сохранить два одинаковых фильтра по товарам', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            expandUserProductFilters: true,
            queryParams: {search, filters}
        });
        await this.browser.clickInto([...menuPath, 'add-user-product-filter'], {waitRender: true});
        await this.browser.typeInto(['form-modal', 'name'], name);
        await this.browser.clickInto(['form-modal', 'form-modal__ok-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            expandUserProductFilters: true,
            queryParams: {search, filters},
            patchStyles: {enableNotifications: true}
        });
        await this.browser.clickInto([...menuPath, 'add-user-product-filter'], {waitRender: true});
        await this.browser.typeInto(['form-modal', 'name'], `${name}_1`);
        await this.browser.clickInto(['form-modal', 'form-modal__ok-button']);
        await this.browser.waitForTestIdSelectorInDom('notification');
        await this.browser.assertImage('notification', {removeShadows: true});
    });

    it('Сохранение выбранных столбцов таблицы вместе с фильтром', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            expandUserProductFilters: true,
            queryParams: {filters, columnIds}
        });
        await this.browser.clickInto([...menuPath, 'add-user-product-filter'], {waitRender: true});
        await this.browser.typeInto(['form-modal', 'name'], name);
        await this.browser.clickInto(['form-modal', 'form-modal__ok-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom([...menuPath, name]);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            expandUserProductFilters: true
        });
        await this.browser.clickInto([...menuPath, name], {waitRender: true, waitNavigation: true});
        await this.browser.assertImage(['products-table', 'product-table-header']);
        await this.browser.assertImage('filter-list');
    });

    it('Фильтр с подтвержденностью можно сохранить', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            expandUserProductFilters: true,
            queryParams: {
                search,
                filters: {confirmation: {rule: 'equal', values: 0}}
            }
        });

        await this.browser.clickInto([...menuPath, 'add-user-product-filter'], {waitRender: true});
        await this.browser.typeInto(['form-modal', 'name'], name);
        await this.browser.clickInto(['form-modal', 'form-modal__ok-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom([...menuPath, name]);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            expandUserProductFilters: true
        });

        await this.browser.clickInto([...menuPath, name], {waitNavigation: true, waitRender: true});

        await this.browser.assertImage('filter-list');
    });
});
