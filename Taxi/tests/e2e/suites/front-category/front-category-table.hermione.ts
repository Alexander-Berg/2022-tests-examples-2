import {regions, rootFrontCategories} from 'tests/e2e/seed-db-map';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {DbTable} from '@/src/entities/const';

describe('Таблица фронт-категорий', function () {
    it('Заголовок шапки страницы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        const defaultHeaderElement = await this.browser.findByTestId('default_panel');
        const innerText = await defaultHeaderElement.getText();
        expect(innerText).to.equal('Фронт-категории');
    });

    it('Шапка таблицы фронт-категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.assertImage(['tree-table', '\\:first-child']);
    });

    it('Страница фронт-категорий – общий вид', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.assertImage();
    });

    it('Клик в "Раскрыть все" разворачивает дерево категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);

        await this.browser.clickInto('expand-all', {waitRender: true});
        await this.browser.assertImage('list-holder');
    });

    it('Клик в "Свернуть всё" сворачивает дерево категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);

        await this.browser.clickInto('expand-all', {waitRender: true});
        await this.browser.clickInto('collapse-all', {waitRender: true});

        await this.browser.assertImage('list-holder');
    });

    it('Клик в "Показать неактивные" показывает неактивные категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);

        await this.browser.clickInto('show-inactive', {waitRender: true});
        await this.browser.performScroll(['tree-table', 'list-holder'], {direction: 'down'});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('list-holder');
    });

    it('Клик в "Создать категорию" открывает страницу создания категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);

        await this.browser.clickInto('create-button', {waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.CREATE_FRONT_CATEGORY));
        await this.browser.assertImage('parent-category-modal__input');
    });

    it('Клик в строку таблицы открывает страницу фронт-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto('fc_row_front_category_code_1_0', {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.FRONT_CATEGORY('\\d')));
    });

    it('Клик в три точки открывает контекстное меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto('category-row-more-button', {waitRender: true});
        await this.browser.assertImage(['category-row-more-button', 'more-menu']);
    });

    it('Клик в "Создать подкатегорию" в контекстном меню открывает модалку "Создать категорию"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto('category-row-more-button', {waitRender: true});
        await this.browser.clickInto(['category-row-more-button', 'more-menu', 'create'], {waitRender: true});
        await this.browser.assertImage('parent-category-modal', {removeShadows: true});
    });

    it('Клик в "Создать подкатегорию" в контекстном меню и выбор родительской категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto('category-row-more-button', {waitRender: true});
        await this.browser.clickInto(['category-row-more-button', 'more-menu', 'create'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('parent-category-modal');
        await this.browser.clickInto('row_front_category_code_1_1');
        await this.browser.clickInto('parent-category-modal__ok-button');
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.CREATE_FRONT_CATEGORY));
        await this.browser.assertImage('parent-category-modal__input');
    });

    it('Изменить статус категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto('show-inactive');
        await this.browser.clickInto('expand_icon');

        await this.browser.waitForTestIdSelectorInDom(['fc_row_front_category_code_5_0', 'status', 'active']);

        await this.browser.clickInto(['fc_row_front_category_code_5_0', 'category-row-more-button'], {
            waitRender: true
        });
        await this.browser.clickInto(['category-row-more-button', 'more-menu', 'disable']);
        await this.browser.waitForTestIdSelectorInDom(['fc_row_front_category_code_5_0', 'status', 'inactive']);
        await this.browser.assertImage('fc_row_front_category_code_5_0');
    });

    it('Изменить статус категории – включить категорию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto('show-inactive');
        await this.browser.clickInto('expand_icon');

        await this.browser.waitForTestIdSelectorInDom(['fc_row_front_category_code_1_19', 'status', 'inactive']);

        await this.browser.clickInto(['fc_row_front_category_code_1_19', 'category-row-more-button'], {
            waitRender: true
        });
        await this.browser.clickInto(['category-row-more-button', 'more-menu', 'enable']);
        await this.browser.waitForTestIdSelectorInDom(['fc_row_front_category_code_1_19', 'status', 'active']);
        await this.browser.pause(2000);
        await this.browser.assertImage('fc_row_front_category_code_1_19');
    });

    it('Клик в количество товаров фронт-категории открывает таблицу товаров этой категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto('products-count-link', {waitRender: true, waitNavigation: true});
        await this.browser.assertImage('filter-list');
    });

    it('Сtrl+клик в строку таблицы фронт-категории открывает страницу товара в новом табе', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto('fc_row_front_category_code_1_0', {button: 'middle'});

        const handles = await this.browser.getWindowHandles();
        expect(handles.length).to.equal(2);

        await this.browser.switchToWindow(handles[1]);
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.FRONT_CATEGORY('\\d')));

        await this.browser.closeWindow();
        await this.browser.switchToWindow(handles[0]);
    });

    it('Скролл свернутой таблицы фронт-категорий при свернутом меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES, {collapseSidebar: true});
        await this.browser.performScroll(['tree-table', 'list-holder'], {direction: 'down'});

        await this.browser.waitUntilRendered();
        await this.browser.assertImage('tree-table');
    });

    it('Скролл развернутой таблицы фронт-категорий при развернутом меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto(['action-bar', 'expand-all'], {waitRender: true});

        await this.browser.performScroll(['tree-table', 'list-holder'], {direction: 'down'});

        await this.browser.waitUntilRendered();
        await this.browser.assertImage('tree-table');
    });

    it('Поменять местами родительские фронт-категории России', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.dragAndDrop('fc_row_front_category_code_1_0', 'fc_row_front_category_code_1_2', {
            offset: 'bottom'
        });
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('tree-table');
    });

    it('Поменять местами листовые фронт-категории Франции', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES, {region: 'fr'});
        await this.browser.clickInto(['fc_row_front_category_code_3_0', 'expand_icon']);
        await this.browser.dragAndDrop('fc_row_front_category_code_45_0', 'fc_row_front_category_code_45_2', {
            offset: 'bottom'
        });
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('tree-table');
    });

    it('Поиск дочерней ФК по названию (Израиль)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES, {
            region: 'il',
            dataLang: 'he',
            queryParams: {search: 'وكأنه حيث'}
        });
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('tree-table');
    });

    it('Поиск ФК по коду (Великобритания)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES, {region: 'gb', queryParams: {search: 'code_2_0'}});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('tree-table');
    });

    it('Экшн-бар таблицы фронт-категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.assertImage('action-bar');
    });

    it('Развенуть дерево фронт-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto(['fc_row_front_category_code_1_0', 'expand_icon'], {waitRender: true});
        await this.browser.assertImage('table-body');
    });

    it('Свернуть дерево фронт-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto('expand-all', {waitRender: true});
        await this.browser.clickInto(['fc_row_front_category_code_1_0', 'expand_icon'], {waitRender: true});
        await this.browser.assertImage('table-body');
    });

    it('Смена языка данных на странице фронт-категорий (Израиль)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES, {region: 'il', dataLang: 'he', uiLang: 'en'});
        await this.browser.waitUntilRendered();
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('data-lang-select', {waitRender: true});
        await this.browser.clickInto(['data-lang-select_dropdown-menu', 'en'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Клик в меню фронт-категории второго уровня открывает контекстное меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.waitUntilRendered();

        await this.browser.clickInto(['fc_row_front_category_code_1_0', 'expand_icon'], {waitRender: true});
        await this.browser.clickInto(['fc_row_front_category_code_5_0', 'category-row-more-button'], {
            waitRender: true
        });
        await this.browser.assertImage(['fc_row_front_category_code_5_0', 'more-menu']);
    });

    it('Массовая деактивация категорий', async function () {
        const [{max: rootSortOrder}] = await this.browser.executeSql<[{max: number}]>(`
            SELECT MAX(sort_order)
            FROM ${DbTable.FRONT_CATEGORY}
            WHERE parent_id = ${rootFrontCategories.ru.front};
        `);

        const [{id: emptyProductsRootId}] = await this.browser.executeSql<[{id: number}]>(
            `
            INSERT INTO ${DbTable.FRONT_CATEGORY} (
                code,
                parent_id,
                region_id,
                status,
                sort_order,
                name_translation_map,
                image_url
            )
            VALUES (
                'empty_products_root_1',
                '${rootFrontCategories.ru.front}',
                ${regions.ru},
                'active',
                ${rootSortOrder + 1},
                '{"ru": "empty_products_root_1"}'::jsonb,
                ''
            )
            RETURNING id;`
        );

        await this.browser.executeSql<[{id: number}, {id: number}]>(`
            INSERT INTO ${DbTable.FRONT_CATEGORY} (
                code,
                parent_id,
                region_id,
                status,
                sort_order,
                name_translation_map,
                image_url
            )
            VALUES
                (
                    'empty_products_child_1_0_0',
                    ${emptyProductsRootId},
                    ${regions.ru},
                    'active',
                    0,
                    '{"ru": "empty_products_child_1_0_0"}'::jsonb,
                    ''
                ),
                (
                    'empty_products_child_1_0_1',
                    ${emptyProductsRootId},
                    ${regions.ru},
                    'disabled',
                    1,
                    '{"ru": "empty_products_child_1_0_1"}'::jsonb,
                    ''
                )
            RETURNING id;`);

        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto(['action-bar', 'show-inactive'], {waitRender: true});
        await this.browser.performScroll(['tree-table', 'list-holder'], {direction: 'down'});

        await this.browser.clickInto(['fc_row_empty_products_root_1', 'expand_icon'], {waitRender: true});
        await this.browser.performScroll(['tree-table', 'list-holder'], {direction: 'down'});

        await this.browser.clickInto(['fc_row_empty_products_root_1', 'category-row-more-button'], {waitRender: true});
        await this.browser.clickInto(
            ['fc_row_empty_products_root_1', 'category-row-more-button', 'more-menu', 'disable'],
            {
                waitRender: true
            }
        );

        await this.browser.assertImage('table-body');
    });

    it('Предупреждение о наличии товаров в выключаемых категориях', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto(['action-bar', 'show-inactive'], {waitRender: true});

        await this.browser.clickInto(['fc_row_front_category_code_1_1', 'expand_icon'], {waitRender: true});
        await this.browser.clickInto(['fc_row_front_category_code_1_1', 'category-row-more-button'], {
            waitRender: true
        });

        await this.browser.clickInto(
            ['fc_row_front_category_code_1_1', 'category-row-more-button', 'more-menu', 'disable'],
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
            FROM ${DbTable.FRONT_CATEGORY}
            WHERE parent_id = ${rootFrontCategories.ru.front};
        `);

        const [{id: emptyProductsRootId}] = await this.browser.executeSql<[{id: number}]>(
            `
            INSERT INTO ${DbTable.FRONT_CATEGORY} (
                code,
                parent_id,
                region_id,
                status,
                sort_order,
                name_translation_map,
                image_url
            )
            VALUES (
                'empty_products_root_2',
                '${rootFrontCategories.ru.front}',
                ${regions.ru},
                'active',
                ${rootSortOrder + 1},
                '{"ru": "empty_products_root_2"}'::jsonb,
                ''
            )
            RETURNING id;`
        );

        await this.browser.executeSql<[{id: number}, {id: number}]>(`
            INSERT INTO ${DbTable.FRONT_CATEGORY} (
                code,
                parent_id,
                region_id,
                status,
                sort_order,
                name_translation_map,
                image_url
            )
            VALUES
                (
                    'empty_products_child_2_0_0',
                    ${emptyProductsRootId},
                    ${regions.ru},
                    'active',
                    0,
                    '{"ru": "empty_products_child_2_0_0"}'::jsonb,
                    ''
                ),
                (
                    'empty_products_child_2_0_1',
                    ${emptyProductsRootId},
                    ${regions.ru},
                    'disabled',
                    1,
                    '{"ru": "empty_products_child_2_0_1"}'::jsonb,
                    ''
                )
            RETURNING id;`);

        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto(['action-bar', 'show-inactive'], {waitRender: true});
        await this.browser.performScroll(['tree-table', 'list-holder'], {direction: 'down'});

        await this.browser.clickInto(['fc_row_empty_products_root_2', 'expand_icon'], {waitRender: true});
        await this.browser.performScroll(['tree-table', 'list-holder'], {direction: 'down'});

        await this.browser.clickInto(['fc_row_empty_products_root_2', 'category-row-more-button'], {waitRender: true});
        await this.browser.clickInto(
            ['fc_row_empty_products_root_2', 'category-row-more-button', 'more-menu', 'enable-recursive'],
            {
                waitRender: true
            }
        );

        await this.browser.assertImage('table-body');
    });

    it('Активация родителя с подкатегориями без товаров', async function () {
        const [{max: rootSortOrder}] = await this.browser.executeSql<[{max: number}]>(`
        SELECT MAX(sort_order)
        FROM ${DbTable.FRONT_CATEGORY}
        WHERE parent_id = ${rootFrontCategories.ru.front};
    `);

        const [{id: emptyProductsRootId}] = await this.browser.executeSql<[{id: number}]>(
            `
        INSERT INTO ${DbTable.FRONT_CATEGORY} (
            code,
            parent_id,
            region_id,
            status,
            sort_order,
            name_translation_map,
            image_url
        )
        VALUES (
            'empty_products_root_3',
            '${rootFrontCategories.ru.front}',
            ${regions.ru},
            'disabled',
            ${rootSortOrder + 1},
            '{"ru": "empty_products_root_2"}'::jsonb,
            ''
        )
        RETURNING id;`
        );

        await this.browser.executeSql<[{id: number}, {id: number}]>(`
        INSERT INTO ${DbTable.FRONT_CATEGORY} (
            code,
            parent_id,
            region_id,
            status,
            sort_order,
            name_translation_map,
            image_url
        )
        VALUES
            (
                'empty_products_child_3_0_0',
                ${emptyProductsRootId},
                ${regions.ru},
                'disabled',
                0,
                '{"ru": "empty_products_child_3_0_0"}'::jsonb,
                ''
            ),
            (
                'empty_products_child_3_0_1',
                ${emptyProductsRootId},
                ${regions.ru},
                'disabled',
                1,
                '{"ru": "empty_products_child_3_0_1"}'::jsonb,
                ''
            )
        RETURNING id;`);

        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto(['action-bar', 'show-inactive'], {waitRender: true});
        await this.browser.performScroll(['tree-table', 'list-holder'], {direction: 'down'});

        await this.browser.clickInto(['fc_row_empty_products_root_3', 'expand_icon'], {waitRender: true});
        await this.browser.performScroll(['tree-table', 'list-holder'], {direction: 'down'});

        await this.browser.clickInto(['fc_row_empty_products_root_3', 'category-row-more-button'], {waitRender: true});
        await this.browser.clickInto(
            ['fc_row_empty_products_root_3', 'category-row-more-button', 'more-menu', 'enable-recursive'],
            {
                waitRender: true
            }
        );

        await this.browser.assertImage('table-body');
    });

    it('Предупреждение о наличии товаров в активируемых подкатегориях', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto(['action-bar', 'show-inactive'], {waitRender: true});
        await this.browser.performScroll(['tree-table', 'list-holder'], {direction: 'down'});

        await this.browser.clickInto(['fc_row_front_category_code_1_18', 'expand_icon'], {waitRender: true});
        await this.browser.performScroll(['tree-table', 'list-holder'], {direction: 'down'});

        await this.browser.clickInto(['fc_row_front_category_code_1_18', 'category-row-more-button'], {
            waitRender: true
        });

        await this.browser.clickInto(
            ['fc_row_front_category_code_1_18', 'category-row-more-button', 'more-menu', 'enable-recursive'],
            {
                waitRender: true
            }
        );

        await this.browser.waitForTestIdSelectorInDom('confirmation-modal');
        await this.browser.assertImage('confirmation-modal', {removeShadows: true});
        await this.browser.clickInto('confirmation-modal__ok-button', {waitRender: true});

        await this.browser.assertImage('table-body');
    });

    // eslint-disable-next-line max-len
    it('Поиск неактивной фронт-категории по названию при создании фронт-категории через контекстное меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto('category-row-more-button', {waitRender: true});
        await this.browser.clickInto(['category-row-more-button', 'more-menu', 'create'], {waitRender: true});

        const frontCategoryName = 'Наслаждению предпочел';

        await this.browser.clickInto('hide-inactive');
        await this.browser.typeInto('search_input', frontCategoryName);

        await this.browser.assertImage(['parent-category-modal__tree-list', 'row_front_category_code_1_18']);
    });

    it('При создании из под активной фронт-категории стоит чекбокс скрытия неактивных', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto(['fc_row_front_category_code_1_0', 'category-row-more-button'], {
            waitRender: true
        });
        await this.browser.clickInto(['category-row-more-button', 'more-menu', 'create'], {waitRender: true});

        await this.browser.assertImage(['parent-category-modal__tree-list', 'hide-inactive']);
    });

    it('При создании из под неактивной фронт-категории стоит чекбокс скрытия неактивных', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto('show-inactive', {waitRender: true});
        await this.browser.clickInto(['fc_row_front_category_code_1_18', 'category-row-more-button'], {
            waitRender: true
        });
        await this.browser.clickInto(['category-row-more-button', 'more-menu', 'create'], {waitRender: true});

        await this.browser.assertImage(['parent-category-modal__tree-list', 'hide-inactive']);
    });

    it('Свернуть и развернуть меню на странице ФК Франции', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES, {region: 'fr'});
        await this.browser.clickInto('sidebar-switcher', {waitRender: true});
        await this.browser.assertImage();
        await this.browser.clickInto('sidebar-switcher', {waitRender: true});
        await this.browser.assertImage();
    });
});
