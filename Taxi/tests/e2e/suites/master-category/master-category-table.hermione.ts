import {parseSpreadSheetCSV} from 'tests/e2e/helper/parse-spreadsheet';
import {regions, rootMasterCategories} from 'tests/e2e/seed-db-map';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {DbTable} from '@/src/entities/const';

describe('Таблица мастер-категорий', function () {
    async function getBrowserDate(ctx: Hermione.TestContext) {
        return ctx.browser.execute(() => {
            const now = new Date();
            return [now.getDate(), now.getMonth() + 1]
                .map(String)
                .map((part) => part.padStart(2, '0'))
                .concat(String(now.getFullYear()))
                .join('.');
        });
    }

    it('Заголовок шапки страницы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        const defaultHeaderElement = await this.browser.findByTestId('default_panel');
        const innerText = await defaultHeaderElement.getText();
        expect(innerText).to.equal('Мастер-категории');
    });

    it('Шапка таблицы мастер-категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.assertImage(['tree-table', '\\:first-child']);
    });

    it('Общий вид таблицы мастер-категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.assertImage('list-holder');
    });

    it('Клик в "Раскрыть все" разворачивает дерево категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);

        await this.browser.clickInto('expand-all', {waitRender: true});
        await this.browser.assertImage('list-holder');
    });

    it('Клик в "Свернуть всё" сворачивает дерево категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);

        await this.browser.clickInto('expand-all', {waitRender: true});
        await this.browser.clickInto('collapse-all', {waitRender: true});

        await this.browser.assertImage('list-holder');
    });

    it('Клик в "Создать категорию" открывает страницу создания категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto('create-button', {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.CREATE_MASTER_CATEGORY));
        await this.browser.assertImage('parent-category-modal__input');
    });

    it('Клик в строку таблицы открывает страницу просмотра категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto('mc_row_master_category_code_1_0', {
            x: -200,
            waitNavigation: true,
            waitRender: true
        });

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.MASTER_CATEGORY('\\d')));
        await this.browser.assertImage('base-layout-content');
    });

    it('Клик в количество товаров мастер-категории открывает таблицу товаров этой категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto('products-count-link', {waitRender: true, waitNavigation: true});
        await this.browser.assertImage('filter-list');
    });

    // eslint-disable-next-line max-len
    it('Клик в количество заполненных товаров мастер-категории открывает таблицу активных заполненных товаров этой категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto('filled-products-count-link', {waitRender: true, waitNavigation: true});
        await this.browser.assertImage('filter-list');
    });

    // eslint-disable-next-line max-len
    it('Кликв в количество не заполненных товаров мастер-категории открывает таблицу активных незаполненных товаров этой категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto('not-filled-products-count-link', {waitRender: true, waitNavigation: true});
        await this.browser.assertImage('filter-list');
    });

    it('Сtrl+клик в строку таблицы мастер-категории открывает страницу товара в новом табе', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto('mc_row_master_category_code_1_0', {x: -200, button: 'middle'});

        const handles = await this.browser.getWindowHandles();
        expect(handles.length).to.equal(2);

        await this.browser.switchToWindow(handles[1]);
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.MASTER_CATEGORY('\\d')));

        await this.browser.closeWindow();
        await this.browser.switchToWindow(handles[0]);
    });

    it('Клик в три точки открывает контекстное меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto('category-row-more-button', {waitRender: true});
        await this.browser.assertImage(['category-row-more-button', 'more-menu']);
    });

    it('Клик в "Создать подкатегорию" в контекстном меню открывает модалку "Создать категорию"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto('category-row-more-button', {waitRender: true});
        await this.browser.clickInto(['category-row-more-button', 'more-menu', 'create']);
        await this.browser.waitForTestIdSelectorInDom('parent-category-modal__tree-list');
        await this.browser.assertImage('parent-category-modal__tree-list');
    });

    it('Клик в "Переместить" заблокирован для мастер-категории с дочерними мастер-категориями', async function () {
        const basePath = ['mc_row_master_category_code_1_0', 'category-row-more-button'];
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.waitForTestIdSelectorAriaDisabled([...basePath, 'more-menu', 'move']);
    });

    // eslint-disable-next-line max-len
    it('Клик в "Переместить" в контекстном меню листовой мастер-категории открывает модалку "Перемещение категории"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto(['mc_row_master_category_code_1_0', 'expand_icon'], {waitRender: true});
        await this.browser.clickInto(['mc_row_master_category_code_5_0', 'expand_icon'], {waitRender: true});

        const basePath = ['mc_row_master_category_code_25_1', 'category-row-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'move']);
        await this.browser.waitForTestIdSelectorInDom('parent-category-modal__tree-list');
        await this.browser.assertImage('parent-category-modal__tree-list');
    });

    it('Переместить мастер-категорию через контекстное меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto('expand-all', {waitRender: true});

        const basePath = ['mc_row_master_category_code_25_0', 'category-row-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'move']);
        await this.browser.waitForTestIdSelectorInDom('parent-category-modal__tree-list');
        await this.browser.typeInto('search_input', 'Примером физическими');
        await this.browser.clickInto('row_master_category_code_27_0');
        await this.browser.clickInto('parent-category-modal__ok-button');
        await this.browser.clickInto('confirmation-modal__ok-button');
        await this.browser.assertImage('table-body');
    });

    it('Скролл развернутой таблицы мастер-категорий при свернутом меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES, {collapseSidebar: true});
        await this.browser.clickInto(['action-bar', 'expand-all'], {waitRender: true});

        await this.browser.performScroll(['tree-table', 'list-holder'], {direction: 'down'});

        await this.browser.waitUntilRendered();
        await this.browser.assertImage('tree-table');
    });

    it('Скролл развернутой таблицы мастер-категорий при развернутом меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto(['action-bar', 'expand-all'], {waitRender: true});

        await this.browser.performScroll(['tree-table', 'list-holder'], {direction: 'down'});

        await this.browser.waitUntilRendered();
        await this.browser.assertImage('tree-table');
    });

    it('Поменять местами мастер-категории Израиля', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES, {region: 'il'});
        await this.browser.dragAndDrop('mc_row_master_category_code_4_0', 'mc_row_master_category_code_4_1', {
            offset: 'bottom'
        });
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('tree-table');
    });

    it('Переместить мастер-категорию Великобритании', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES, {region: 'gb'});
        await this.browser.clickInto(['mc_row_master_category_code_2_0', 'expand_icon'], {waitRender: true});
        await this.browser.clickInto(['mc_row_master_category_code_10_1', 'expand_icon'], {waitRender: true});

        await this.browser.dragAndDrop('mc_row_master_category_code_36_1', 'mc_row_master_category_code_36_0', {
            offset: 'center'
        });
        await this.browser.waitForTestIdSelectorInDom('confirmation-modal');
        await this.browser.clickInto('confirmation-modal__ok-button');

        await this.browser.waitUntilRendered();
        await this.browser.assertImage('tree-table');
    });

    it('Поиск МК по названию (Франция)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES, {region: 'fr', queryParams: {search: 'neque'}});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('tree-table');
    });

    it('Поиск дочерней МК по коду (Россия)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES, {
            region: 'ru',
            queryParams: {search: 'code_7'}
        });
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('tree-table');
    });

    it('Поиск МК по названию в модале "Создать категорию"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto('category-row-more-button', {waitRender: true});
        await this.browser.clickInto(['category-row-more-button', 'more-menu', 'create']);
        await this.browser.waitForTestIdSelectorInDom('parent-category-modal__tree-list');
        await this.browser.clickInto(['hide-inactive']);
        await this.browser.typeInto(['parent-category-modal__tree-list', 'search_input'], 'обстоятельства');
        await this.browser.assertImage('parent-category-modal__tree-list');
    });

    it('Поиск МК по названию в модале "Перемещение категории"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto('category-row-more-button', {waitRender: true});
        await this.browser.clickInto(['category-row-more-button', 'more-menu', 'create']);
        await this.browser.waitForTestIdSelectorInDom('parent-category-modal__tree-list');
        await this.browser.clickInto(['hide-inactive']);
        await this.browser.typeInto(['parent-category-modal__tree-list', 'search_input'], 'страдание');
        await this.browser.assertImage('parent-category-modal__tree-list');
    });

    it('Создать дочернюю мастер-категорию через контекстное меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto('category-row-more-button', {waitRender: true});
        await this.browser.clickInto(['category-row-more-button', 'more-menu', 'create']);
        await this.browser.clickInto('parent-category-modal__ok-button', {
            waitForClickable: true,
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.typeInto('code', 'category_from_context_menu');
        await this.browser.clickInto('submit-button', {waitRender: true, waitNavigation: true});
        await this.browser.assertImage('base-layout');
        await this.browser.clickInto('master-categories-menu-item', {waitNavigation: true, waitRender: true});
        await this.browser.clickInto('expand_icon', {waitRender: true});
        await this.browser.assertImage('table-body');
    });

    it('Развернуть дерево мастер-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto(['mc_row_master_category_code_1_0', 'expand_icon'], {waitRender: true});
        await this.browser.clickInto(['mc_row_master_category_code_5_0', 'expand_icon'], {waitRender: true});

        await this.browser.assertImage('table-body');
    });

    it('Свернуть дерево мастер-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto('expand-all', {waitRender: true});
        await this.browser.clickInto(['mc_row_master_category_code_5_0', 'expand_icon'], {waitRender: true});
        await this.browser.clickInto(['mc_row_master_category_code_1_0', 'expand_icon'], {waitRender: true});

        await this.browser.assertImage('table-body');
    });

    it('Смена языка данных на странице мастер-категорий (Франция)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES, {region: 'fr', dataLang: 'fr', uiLang: 'fr'});
        await this.browser.waitUntilRendered();
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('data-lang-select', {waitRender: true});
        await this.browser.clickInto(['data-lang-select_dropdown-menu', 'en'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Перенос в МК с товаром подкатегорию с другой ИМ c появлением неиспользуемых атрибутов', async function () {
        const productIdentifier = '10000001';

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(productIdentifier));
        await this.browser.assertImage(['query-state-spinner', 'product_view', 'attribute_group_code_2'], {
            removeShadows: true
        });

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto('expand-all', {waitRender: true});

        await this.browser.clickInto(['list-holder', 'mc_row_master_category_code_31_1', 'category-row-more-button'], {
            waitRender: true
        });
        await this.browser.clickInto(['more-menu', 'move'], {waitRender: true});
        await this.browser.clickInto(['parent-category-modal', 'row_master_category_code_1_0', '\\[class*=switcher]'], {
            waitRender: true
        });
        await this.browser.clickInto(['parent-category-modal', 'row_master_category_code_5_0', '\\[class*=switcher]'], {
            waitRender: true
        });
        await this.browser.clickInto(['parent-category-modal', 'row_master_category_code_25_0', 'title'], {
            waitRender: true
        });
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button'], {waitRender: true});
        await this.browser.clickInto('collapse-all', {waitRender: true});
        await this.browser.clickInto('expand-all', {waitRender: true});
        await this.browser.pause(2000);
        await this.browser.assertImage('mc_row_master_category_code_31_1');

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(productIdentifier));
        await this.browser.assertImage(['query-state-spinner', 'product_view', 'unused-attributes'], {
            removeShadows: true
        });
    });

    it('Перенос подкатегории в категорию с товаром', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto('expand-all', {waitRender: true});
        await this.browser.assertImage('tree-table');
        await this.browser.dragAndDrop('mc_row_master_category_code_26_0', 'mc_row_master_category_code_25_0', {
            offset: 'center'
        });
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('confirmation-modal', {removeShadows: true});
        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button'], {waitRender: true});
        await this.browser.assertImage('tree-table');
    });

    it('Скачать шаблон инфомодели из таблицы мастер-категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto(['mc_row_master_category_code_1_0', 'expand_icon'], {waitRender: true});
        await this.browser.clickInto(['mc_row_master_category_code_5_0', 'expand_icon'], {waitRender: true});

        const basePath = ['mc_row_master_category_code_25_0', 'category-row-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'download-template'], {waitRender: true});

        const date = await getBrowserDate(this);
        const fileName = `template_CAT_master_category_code_25_0_of_IM_info_model_code_1_14_${date}.xlsx`;

        const file = await this.browser.getDownloadedFile(fileName, {purge: true});
        expect(parseSpreadSheetCSV(file)).to.matchSnapshot(this);
    });

    it('Скачать шаблон инфомодели без товаров из таблицы мастер-категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL);
        await this.browser.typeInto('code', 'im_code_test');
        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.typeInto('code', 'mc_code_test');
        await this.browser.clickInto('info-model-select');
        await this.browser.clickInto(['info-model-select_dropdown-menu', 'im_node_compatible_im_code_test']);
        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        const basePath = ['mc_row_mc_code_test', 'category-row-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'download-template'], {waitRender: true});

        const date = await getBrowserDate(this);
        const fileName = `template_CAT_mc_code_test_of_IM_im_code_test_${date}.xlsx`;
        const file = await this.browser.getDownloadedFile(fileName, {purge: true});
        expect(parseSpreadSheetCSV(file)).to.matchSnapshot(this);
    });

    it('Сменить родителя у категории первой по списку', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto('expand-all', {waitRender: true});
        await this.browser.dragAndDrop('mc_row_master_category_code_25_0', 'mc_row_master_category_code_6_0');
        await this.browser.clickInto('confirmation-modal__ok-button', {waitForClickable: true});
        await this.browser.assertImage('table-body');
    });

    it('Массовая деактивация категорий', async function () {
        const [{max: rootSortOrder}] = await this.browser.executeSql<[{max: number}]>(`
            SELECT MAX(sort_order)
            FROM ${DbTable.MASTER_CATEGORY}
            WHERE parent_id = ${rootMasterCategories.ru.master};
        `);

        const [{id: emptyProductsRootId}] = await this.browser.executeSql<[{id: number}]>(
            `
            INSERT INTO ${DbTable.MASTER_CATEGORY} (code, parent_id, region_id, status, sort_order)
            VALUES (
                'empty_products_root_1',
                '${rootMasterCategories.ru.master}',
                ${regions.ru},
                'active',
                ${rootSortOrder + 1}
            )
            RETURNING id;`
        );

        const children1 = await this.browser.executeSql<[{id: number}, {id: number}]>(
            `
            INSERT INTO ${DbTable.MASTER_CATEGORY} (code, parent_id, region_id, status, sort_order)
            VALUES
                ('empty_products_child_1_0_0', ${emptyProductsRootId}, ${regions.ru}, 'active', 0),
                ('empty_products_child_1_0_1', ${emptyProductsRootId}, ${regions.ru}, 'disabled', 1)
            RETURNING id;`
        );

        await this.browser.executeSql(
            `
            INSERT INTO ${DbTable.MASTER_CATEGORY} (code, parent_id, region_id, status, sort_order)
            VALUES
                ('empty_products_child_1_1_0', ${children1[0].id}, ${regions.ru}, 'active', 0),
                ('empty_products_child_1_1_1', ${children1[1].id}, ${regions.ru}, 'disabled', 1);`
        );

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);

        await this.browser.clickInto(['mc_row_empty_products_root_1', 'expand_icon'], {waitRender: true});
        await this.browser.clickInto(['mc_row_empty_products_child_1_0_0', 'expand_icon'], {waitRender: true});
        await this.browser.clickInto(['mc_row_empty_products_child_1_0_1', 'expand_icon'], {waitRender: true});

        await this.browser.clickInto(['mc_row_empty_products_root_1', 'category-row-more-button'], {waitRender: true});
        await this.browser.clickInto(
            ['mc_row_empty_products_root_1', 'category-row-more-button', 'more-menu', 'disable'],
            {
                waitRender: true
            }
        );

        await this.browser.assertImage('table-body');
    });

    it('Предупреждение о наличии товаров в выключаемых категориях', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);

        await this.browser.clickInto(['mc_row_master_category_code_1_1', 'expand_icon'], {waitRender: true});
        await this.browser.clickInto(['mc_row_master_category_code_6_0', 'expand_icon'], {waitRender: true});
        await this.browser.clickInto(['mc_row_master_category_code_6_1', 'expand_icon'], {waitRender: true});

        await this.browser.clickInto(['mc_row_master_category_code_1_1', 'category-row-more-button'], {
            waitRender: true
        });

        await this.browser.clickInto(
            ['mc_row_master_category_code_1_1', 'category-row-more-button', 'more-menu', 'disable'],
            {
                waitRender: true
            }
        );

        await this.browser.waitForTestIdSelectorInDom('confirmation-modal');
        await this.browser.assertImage('confirmation-modal', {removeShadows: true});
        await this.browser.clickInto('confirmation-modal__ok-button', {waitRender: true});

        await this.browser.assertImage('table-body');
    });

    it('Массовая активация подкатегорий без товаров', async function () {
        const [{max: rootSortOrder}] = await this.browser.executeSql<[{max: number}]>(`
            SELECT MAX(sort_order)
            FROM ${DbTable.MASTER_CATEGORY}
            WHERE parent_id = ${rootMasterCategories.ru.master};
        `);

        const [{id: emptyProductsRootId}] = await this.browser.executeSql<[{id: number}]>(
            `
            INSERT INTO ${DbTable.MASTER_CATEGORY} (code, parent_id, region_id, status, sort_order)
            VALUES (
                'empty_products_root_2',
                '${rootMasterCategories.ru.master}',
                ${regions.ru},
                'active',
                ${rootSortOrder + 1}
            )
            RETURNING id;`
        );

        await this.browser.executeSql<[{id: number}, {id: number}]>(
            `
            INSERT INTO ${DbTable.MASTER_CATEGORY} (code, parent_id, region_id, status, sort_order)
            VALUES
                ('empty_products_child_2_0_0', ${emptyProductsRootId}, ${regions.ru}, 'disabled', 0),
                ('empty_products_child_2_0_1', ${emptyProductsRootId}, ${regions.ru}, 'disabled', 1)
            RETURNING id;`
        );

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);

        await this.browser.clickInto(['mc_row_empty_products_root_2', 'expand_icon'], {waitRender: true});
        await this.browser.clickInto(['mc_row_empty_products_root_2', 'category-row-more-button'], {waitRender: true});
        await this.browser.clickInto(
            ['mc_row_empty_products_root_2', 'category-row-more-button', 'more-menu', 'enable-recursive'],
            {
                waitRender: true
            }
        );

        await this.browser.assertImage('table-body');
    });

    it('Активация родителя с подкатегориями без товаров', async function () {
        const [{max: rootSortOrder}] = await this.browser.executeSql<[{max: number}]>(`
            SELECT MAX(sort_order)
            FROM ${DbTable.MASTER_CATEGORY}
            WHERE parent_id = ${rootMasterCategories.ru.master};
        `);

        const [{id: emptyProductsRootId}] = await this.browser.executeSql<[{id: number}]>(
            `
            INSERT INTO ${DbTable.MASTER_CATEGORY} (code, parent_id, region_id, status, sort_order)
            VALUES (
                'empty_products_root_3',
                '${rootMasterCategories.ru.master}',
                ${regions.ru},
                'disabled',
                ${rootSortOrder + 1}
            )
            RETURNING id;`
        );

        await this.browser.executeSql<[{id: number}, {id: number}]>(
            `
            INSERT INTO ${DbTable.MASTER_CATEGORY} (code, parent_id, region_id, status, sort_order)
            VALUES
                ('empty_products_child_3_0_0', ${emptyProductsRootId}, ${regions.ru}, 'disabled', 0),
                ('empty_products_child_3_0_1', ${emptyProductsRootId}, ${regions.ru}, 'disabled', 1)
            RETURNING id;`
        );

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);

        await this.browser.clickInto(['mc_row_empty_products_root_3', 'expand_icon'], {waitRender: true});
        await this.browser.clickInto(['mc_row_empty_products_root_3', 'category-row-more-button'], {waitRender: true});
        await this.browser.clickInto(
            ['mc_row_empty_products_root_3', 'category-row-more-button', 'more-menu', 'enable-recursive'],
            {
                waitRender: true
            }
        );

        await this.browser.assertImage('table-body');
    });

    it('Предупреждение о наличии товаров в активируемых подкатегориях', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);

        await this.browser.clickInto(['mc_row_master_category_code_1_3', 'expand_icon'], {waitRender: true});
        await this.browser.clickInto(['mc_row_master_category_code_8_0', 'expand_icon'], {waitRender: true});
        await this.browser.clickInto(['mc_row_master_category_code_8_1', 'expand_icon'], {waitRender: true});

        await this.browser.clickInto(['mc_row_master_category_code_1_3', 'category-row-more-button'], {
            waitRender: true
        });

        await this.browser.clickInto(
            ['mc_row_master_category_code_1_3', 'category-row-more-button', 'more-menu', 'enable-recursive'],
            {
                waitRender: true
            }
        );

        await this.browser.waitForTestIdSelectorInDom('confirmation-modal');
        await this.browser.assertImage('confirmation-modal', {removeShadows: true});
        await this.browser.clickInto('confirmation-modal__ok-button', {waitRender: true});

        await this.browser.assertImage('table-body');
    });

    it('При создании из под активной мастер-категории стоит чекбокс скрытия неактивных', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto(['mc_row_master_category_code_1_0', 'category-row-more-button'], {
            waitRender: true
        });
        await this.browser.clickInto(['category-row-more-button', 'more-menu', 'create'], {waitRender: true});

        await this.browser.assertImage(['parent-category-modal__tree-list', 'hide-inactive']);
    });

    it('При создании из под неактивной мастер-категории стоит чекбокс скрытия неактивных', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto(['mc_row_master_category_code_1_3', 'category-row-more-button'], {
            waitRender: true
        });
        await this.browser.clickInto(['category-row-more-button', 'more-menu', 'create'], {waitRender: true});

        await this.browser.assertImage(['parent-category-modal__tree-list', 'hide-inactive']);
    });

    it('Свернуть и развернуть меню на странице МК Великобритации', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES, {region: 'gb'});
        await this.browser.clickInto('sidebar-switcher', {waitRender: true});
        await this.browser.clickInto('sidebar-switcher', {waitRender: true});
        await this.browser.assertImage();
    });
});
