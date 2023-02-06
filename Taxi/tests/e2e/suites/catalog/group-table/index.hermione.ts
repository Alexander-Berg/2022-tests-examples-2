import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Таблица прилавков в витрине', function () {
    it('Смена языка данных в таблице прилавков. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'), {region: 'il', dataLang: 'he', uiLang: 'en'});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('data-lang-select', {waitRender: true});
        await this.browser.clickInto(['data-lang-select_dropdown-menu', 'ru'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Смена языка интерфейса в таблице прилавков', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('ui-lang-select', {waitRender: true});
        await this.browser.clickInto(['ui-lang-select_dropdown-menu', 'en'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Скролл таблицы прилавков с подгрузкой', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        await this.browser.performScroll('groups-table__wrapper', {
            direction: 'down',
            beforeIterationDelay: () => this.browser.waitForTestIdSelectorNotInDom('groups-table__spinner'),
            afterIterationDelay: () => this.browser.waitUntilRendered()
        });
        await this.browser.assertImage('groups-table__wrapper');
    });

    it('Скролл таблицы прилавков со свернутым боковым меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'), {collapseSidebar: true});
        await this.browser.performScroll('groups-table__wrapper', {
            direction: 'down',
            beforeIterationDelay: () => this.browser.waitForTestIdSelectorNotInDom('groups-table__spinner'),
            afterIterationDelay: () => this.browser.waitUntilRendered()
        });
        await this.browser.assertImage('groups-table__wrapper');
    });

    it('Показать неактивные в таблице прилавков', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        await this.browser.clickInto(['action-bar', 'hide-inactive'], {waitRender: true});
        await this.browser.assertImage('groups-table__wrapper');
    });

    it('Поиск прилавка по коду', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        await this.browser.typeInto(['action-bar', 'search'], '1_28');
        await this.browser.waitForTestIdSelectorNotInDom('groups-table__spinner');
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['groups-table__wrapper', '\\tbody']);
    });

    it('Поиск прилавка по длинному названию. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'), {region: 'il'});
        await this.browser.typeInto(['action-bar', 'search'], 'Иной которое перед');
        await this.browser.waitForTestIdSelectorNotInDom('groups-table__spinner');
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['groups-table__wrapper', '\\tbody']);
    });

    it('Поиск прилавка по короткому названию - по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'), {
            queryParams: {search: 'Отвергает из равно'}
        });
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['groups-table__wrapper', '\\tbody']);
    });

    it('Поиск прилавка по описанию - по прямой ссылке. Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'), {
            region: 'fr',
            queryParams: {search: 'dolores repellat tempora'}
        });
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['groups-table__wrapper', '\\tbody']);
    });

    it('Ничего не найдено в таблице прилавков', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        await this.browser.typeInto(['action-bar', 'search'], 'not-found');
        await this.browser.waitForTestIdSelectorNotInDom('categories-table__spinner');
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('groups-table__wrapper');
    });

    it('Клик в прилавок в таблице прилавков', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        await this.browser.clickInto('group_row_group_code_1_1', {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.GROUP('\\d')));
    });

    it('Копирование по ховеру на код и название в таблице прилавков', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'), {patchStyles: {showCopyButtons: true}});
        await this.browser.clickInto([
            'group_row_group_code_1_1',
            'group_name_and_code',
            'text-with-copy-button_name',
            'button'
        ]);
        expect(await this.browser.clipboardReadText()).to.equal('Или зодчим');
        await this.browser.clickInto([
            'group_row_group_code_1_1',
            'group_name_and_code',
            'text-with-copy-button_code',
            'button'
        ]);
        expect(await this.browser.clipboardReadText()).to.equal('group_code_1_1');
    });

    it('Нельзя удалить прилавок через три точки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        const basePath = ['group_row_group_code_1_1', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.waitForTestIdSelectorAriaDisabled([...basePath, 'more-menu', 'delete']);
    });

    it('Отмена дублирования прилавка через три точки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        const basePath = ['group_row_group_code_1_3', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'duplicate'], {waitRender: true});
        await this.browser.assertImage('create-duplicate-modal', {removeShadows: true});
        await this.browser.clickInto(['create-duplicate-modal', 'create-duplicate-modal__cancel_button'], {
            waitRender: true
        });
        await this.browser.assertImage('base-layout');
    });

    it('Нельзя дублировать прилавок без названия. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'), {region: 'il'});
        const basePath = ['group_row_group_code_4_1', 'table-more-button'];
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

    it('Нельзя дублировать прилавок с существующим кодом', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'), {
            patchStyles: {enableNotifications: true}
        });
        const basePath = ['group_row_group_code_1_1', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'duplicate'], {waitRender: true});
        await this.browser.typeInto('code', 'group_code_1_1', {clear: true});
        await this.browser.clickInto(['create-duplicate-modal', 'create-duplicate-modal__ok_button'], {
            waitRender: true
        });
        await this.browser.waitForTestIdSelectorInDom('notification');
        await this.browser.assertImage('notification', {removeShadows: true});
    });

    it('Валидация кода прилавка при ее дублировании', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        const basePath = ['group_row_group_code_1_1', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'duplicate'], {waitRender: true});
        await this.browser.typeInto('code', 'bad::code', {clear: true});
        await this.browser.clickInto(['create-duplicate-modal', 'create-duplicate-modal__ok_button'], {
            waitRender: true
        });
        await this.browser.waitForTestIdSelectorInDom('create-duplicate-modal');
        await this.browser.assertImage('code_container');
    });

    it('Дублирование прилавка через три точки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        const basePath = ['group_row_group_code_1_3', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'duplicate'], {waitRender: true});
        await this.browser.clickInto(['create-duplicate-modal', 'create-duplicate-modal__ok_button'], {
            waitRender: true
        });
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Открытие прилавка через три точки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        const basePath = ['group_row_group_code_1_1', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'open'], {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.GROUP('\\d')));
    });

    it('Деактивировать прилавок через три точки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        await this.browser.clickInto(['action-bar', 'hide-inactive'], {waitRender: true});
        const basePath = ['group_row_group_code_1_1', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'deactivate'], {waitRender: true});
        await this.browser.assertImage('group_row_group_code_1_1');
    });

    it('Активировать прилавок через три точки. Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'), {region: 'fr'});
        await this.browser.clickInto(['action-bar', 'hide-inactive'], {waitRender: true});
        const basePath = ['group_row_group_code_3_5', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'activate'], {waitRender: true});
        await this.browser.assertImage('group_row_group_code_3_5');
    });

    it('Отмена деактивации прилавка через три точки, если он в двух сетках', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        const basePath = ['group_row_group_code_1_3', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'deactivate'], {waitRender: true});
        await this.browser.assertImage('edit-modal', {removeShadows: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__cancel_button'], {waitRender: true});
        await this.browser.assertImage('group_row_group_code_1_3');
    });

    it('Активация прилавка во всех сетках через три точки. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'), {region: 'il'});
        await this.browser.clickInto(['action-bar', 'hide-inactive'], {waitRender: true});
        const basePath = ['group_row_group_code_4_5', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'activate'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.assertImage('group_row_group_code_4_5');
    });

    it('Деактивация прилавка через три точки только в одной из сеток', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        const basePath = ['group_row_group_code_1_3', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'deactivate'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'update-all']);
        await this.browser.clickInto(['edit-modal', 'select-item_grid_code_1_2', 'checkbox'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.clickInto(['action-bar', 'hide-inactive'], {waitRender: true});
        await this.browser.typeInto(['action-bar', 'search'], 'group_code_1_3', {clear: true});
        await this.browser.waitForTestIdSelectorNotInDom('groups-table__spinner');
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['groups-table__wrapper', '\\tbody']);
    });

    it('Нельзя создать дубликат прилавка в сетке при деактивации через три точки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'), {patchStyles: {enableNotifications: true}});
        const basePath = ['group_row_group_code_1_3', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'deactivate'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'update-all']);
        await this.browser.clickInto(['edit-modal', 'select-item_grid_code_1_2', 'checkbox'], {waitRender: true});
        await this.browser.typeInto(['edit-modal', 'code'], 'group_code_1_3', {clear: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('notification');
        await this.browser.assertImage('notification', {removeShadows: true});
    });

    it('Нельзя активировать прилавок через три точки, если у него нет фото', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'), {patchStyles: {enableNotifications: true}});
        await this.browser.clickInto(['action-bar', 'hide-inactive'], {waitRender: true});
        const basePath = ['group_row_group_code_1_10', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'activate'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('notification');
        await this.browser.assertImage('notification', {removeShadows: true});
    });
});
