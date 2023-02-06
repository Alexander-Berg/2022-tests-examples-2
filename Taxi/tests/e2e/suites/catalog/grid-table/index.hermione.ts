import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Таблица сеток в витрине', function () {
    it('Смена языка данных в таблице сеток. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'), {region: 'il', dataLang: 'he', uiLang: 'en'});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('data-lang-select', {waitRender: true});
        await this.browser.clickInto(['data-lang-select_dropdown-menu', 'ru'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Смена языка интерфейса в таблице сеток', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'));
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('ui-lang-select', {waitRender: true});
        await this.browser.clickInto(['ui-lang-select_dropdown-menu', 'en'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Скролл таблицы сеток с подгрузкой', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'));
        await this.browser.performScroll('grids-table__wrapper', {
            direction: 'down',
            beforeIterationDelay: () => this.browser.waitForTestIdSelectorNotInDom('grids-table__spinner'),
            afterIterationDelay: () => this.browser.waitUntilRendered()
        });
        await this.browser.assertImage('grids-table__wrapper');
    });

    it('Скролл таблицы сеток со свернутым боковым меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'), {collapseSidebar: true});
        await this.browser.performScroll('grids-table__wrapper', {
            direction: 'down',
            beforeIterationDelay: () => this.browser.waitForTestIdSelectorNotInDom('grids-table__spinner'),
            afterIterationDelay: () => this.browser.waitUntilRendered()
        });
        await this.browser.assertImage('grids-table__wrapper');
    });

    it('Показать неактивные в таблице сеток', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'));
        await this.browser.clickInto(['action-bar', 'hide-inactive'], {waitRender: true});
        await this.browser.assertImage('grids-table__wrapper');
    });

    it('Поиск сетки по коду', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'));
        await this.browser.typeInto(['action-bar', 'search'], '1_28');
        await this.browser.waitForTestIdSelectorNotInDom('grids-table__spinner');
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['grids-table__wrapper', '\\tbody']);
    });

    it('Поиск сетки по длинному названию. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'), {region: 'il'});
        await this.browser.typeInto(['action-bar', 'search'], 'Умеет а пользы');
        await this.browser.waitForTestIdSelectorNotInDom('grids-table__spinner');
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['grids-table__wrapper', '\\tbody']);
    });

    it('Поиск сетки по короткому названию - по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'), {
            queryParams: {search: 'Иной то физическими'}
        });
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['grids-table__wrapper', '\\tbody']);
    });

    it('Поиск сетки по описанию - по прямой ссылке. Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'), {
            region: 'fr',
            queryParams: {search: 'doloribus incidunt'}
        });
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['grids-table__wrapper', '\\tbody']);
    });

    it('Ничего не найдено в таблице сеток', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'));
        await this.browser.typeInto(['action-bar', 'search'], 'not-found');
        await this.browser.waitForTestIdSelectorNotInDom('categories-table__spinner');
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('grids-table__wrapper');
    });

    it('Клик в сетку в таблице сеток', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'));
        await this.browser.clickInto('grid_row_grid_code_1_1', {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.GRID('\\d')));
    });

    it('Копирование по ховеру на код и название в таблице сеток', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'), {patchStyles: {showCopyButtons: true}});
        await this.browser.clickInto([
            'grid_row_grid_code_1_1',
            'grid_name_and_code',
            'text-with-copy-button_name',
            'button'
        ]);
        expect(await this.browser.clipboardReadText()).to.equal('Я наслаждения');
        await this.browser.clickInto([
            'grid_row_grid_code_1_1',
            'grid_name_and_code',
            'text-with-copy-button_code',
            'button'
        ]);
        expect(await this.browser.clipboardReadText()).to.equal('grid_code_1_1');
    });

    it('Нельзя удалить сетку через три точки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'));
        const basePath = ['grid_row_grid_code_1_1', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.waitForTestIdSelectorAriaDisabled([...basePath, 'more-menu', 'delete']);
    });

    it('Отмена дублирования сетки через три точки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'));
        const basePath = ['grid_row_grid_code_1_1', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'duplicate'], {waitRender: true});
        await this.browser.assertImage('create-duplicate-modal', {removeShadows: true});
        await this.browser.clickInto(['create-duplicate-modal', 'create-duplicate-modal__cancel_button'], {
            waitRender: true
        });
        await this.browser.assertImage('base-layout');
    });

    it('Нельзя дублировать сетку без названия. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'), {region: 'il'});
        const basePath = ['grid_row_grid_code_4_1', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'duplicate'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('create-duplicate-modal');
        await this.browser.typeInto('code', '', {clear: true});
        await this.browser.waitForTestIdSelectorDisabled([
            'create-duplicate-modal',
            'create-duplicate-modal__ok_button'
        ]);
        await this.browser.assertImage('create-duplicate-modal', {removeShadows: true});
    });

    it('Нельзя дублировать сетку с существующим кодом', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'), {
            patchStyles: {enableNotifications: true}
        });
        const basePath = ['grid_row_grid_code_1_1', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'duplicate'], {waitRender: true});
        await this.browser.typeInto('code', 'grid_code_1_1', {clear: true});
        await this.browser.clickInto(['create-duplicate-modal', 'create-duplicate-modal__ok_button'], {
            waitRender: true
        });
        await this.browser.waitForTestIdSelectorInDom('notification');
        await this.browser.assertImage('notification', {removeShadows: true});
    });

    it('Валидация кода сетки при ее дублировании', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'));
        const basePath = ['grid_row_grid_code_1_1', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'duplicate'], {waitRender: true});
        await this.browser.typeInto('code', 'bad::code', {clear: true});
        await this.browser.clickInto(['create-duplicate-modal', 'create-duplicate-modal__ok_button'], {
            waitRender: true
        });
        await this.browser.waitForTestIdSelectorInDom('create-duplicate-modal');
        await this.browser.assertImage('code_container');
    });

    it('Дублирование сетки через три точки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'));
        const basePath = ['grid_row_grid_code_1_3', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'duplicate'], {waitRender: true});
        await this.browser.clickInto(['create-duplicate-modal', 'create-duplicate-modal__ok_button'], {
            waitRender: true
        });
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Открытие сетки через три точки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'));
        const basePath = ['grid_row_grid_code_1_1', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'open'], {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.GRID('\\d')));
    });

    it('Деактивировать сетку через три точки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'));
        await this.browser.clickInto(['action-bar', 'hide-inactive'], {waitRender: true});
        const basePath = ['grid_row_grid_code_1_1', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'deactivate'], {waitRender: true});
        await this.browser.assertImage('grid_row_grid_code_1_1');
    });

    it('Активировать сетку через три точки. Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'), {region: 'fr'});
        await this.browser.clickInto(['action-bar', 'hide-inactive'], {waitRender: true});
        const basePath = ['grid_row_grid_code_3_5', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'activate'], {waitRender: true});
        await this.browser.assertImage('grid_row_grid_code_3_5');
    });
});
