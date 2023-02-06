import {categories} from 'tests/e2e/seed-db-map';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Таблица категорий в витрине', function () {
    it('Смена языка данных в таблице категорий. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'), {
            region: 'il',
            dataLang: 'he',
            uiLang: 'en'
        });
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('data-lang-select', {waitRender: true});
        await this.browser.clickInto(['data-lang-select_dropdown-menu', 'ru'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Смена языка интерфейса в таблице категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('ui-lang-select', {waitRender: true});
        await this.browser.clickInto(['ui-lang-select_dropdown-menu', 'en'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Скролл таблицы категорий с подгрузкой', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        await this.browser.performScroll('categories-table__wrapper', {
            direction: 'down',
            beforeIterationDelay: () => this.browser.waitForTestIdSelectorNotInDom('categories-table__spinner'),
            afterIterationDelay: () => this.browser.waitUntilRendered()
        });
        await this.browser.assertImage('categories-table__wrapper');
    });

    it('Скролл таблицы категорий со свернутым боковым меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'), {collapseSidebar: true});
        await this.browser.performScroll('categories-table__wrapper', {
            direction: 'down',
            beforeIterationDelay: () => this.browser.waitForTestIdSelectorNotInDom('categories-table__spinner'),
            afterIterationDelay: () => this.browser.waitUntilRendered()
        });
        await this.browser.assertImage('categories-table__wrapper');
    });

    it('Показать неактивные в таблице категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        await this.browser.clickInto(['action-bar', 'hide-inactive'], {waitRender: true});
        await this.browser.assertImage('categories-table__wrapper');
    });

    it('Поиск категории по коду', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        await this.browser.typeInto(['action-bar', 'search'], '1_28');
        await this.browser.waitForTestIdSelectorNotInDom('categories-table__spinner');
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['categories-table__wrapper', '\\tbody']);
    });

    it('Поиск категории по длинному названию. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'), {region: 'il'});
        await this.browser.typeInto(['action-bar', 'search'], 'Некое некоей некоей');
        await this.browser.waitForTestIdSelectorNotInDom('categories-table__spinner');
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['categories-table__wrapper', '\\tbody']);
    });

    it('Поиск категории по короткому названию - по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'), {
            queryParams: {search: 'Не приносят восхваляющих'}
        });
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['categories-table__wrapper', '\\tbody']);
    });

    it('Поиск категории по описанию - по прямой ссылке. Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'), {
            region: 'fr',
            queryParams: {search: 'Ullam sunt'}
        });
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['categories-table__wrapper', '\\tbody']);
    });

    it('Ничего не найдено в таблице категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        await this.browser.typeInto(['action-bar', 'search'], 'not-found');
        await this.browser.waitForTestIdSelectorNotInDom('categories-table__spinner');
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('categories-table__wrapper');
    });

    it('Клик в категорию в таблице категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        await this.browser.clickInto('category_row_category_code_1_1', {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.CATEGORY('\\d')));
    });

    it('Копирование по ховеру на код и название в таблице категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'), {patchStyles: {showCopyButtons: true}});
        await this.browser.clickInto([
            'category_row_category_code_1_1',
            'category_name_and_code',
            'text-with-copy-button_name',
            'button'
        ]);
        expect(await this.browser.clipboardReadText()).to.equal('Равно воспользоваться разумно');
        await this.browser.clickInto([
            'category_row_category_code_1_1',
            'category_name_and_code',
            'text-with-copy-button_code',
            'button'
        ]);
        expect(await this.browser.clipboardReadText()).to.equal('category_code_1_1');
    });

    it('Нельзя удалить категорию через три точки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        const basePath = ['category_row_category_code_1_1', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.waitForTestIdSelectorAriaDisabled([...basePath, 'more-menu', 'delete']);
    });

    it('Отмена дублирования категории через три точки', async function () {
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

    it('Нельзя дублировать категорию без названия. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'), {region: 'il'});
        const basePath = ['category_row_category_code_4_1', 'table-more-button'];
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

    it('Нельзя дублировать категорию с существующим кодом', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'), {
            patchStyles: {enableNotifications: true}
        });
        const basePath = ['category_row_category_code_1_1', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'duplicate'], {waitRender: true});
        await this.browser.typeInto('code', 'category_code_1_1', {clear: true});
        await this.browser.clickInto(['create-duplicate-modal', 'create-duplicate-modal__ok_button'], {
            waitRender: true
        });
        await this.browser.waitForTestIdSelectorInDom('notification');
        await this.browser.assertImage('notification', {removeShadows: true});
    });

    it('Валидация кода категории при ее дублировании', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        const basePath = ['category_row_category_code_1_1', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'duplicate'], {waitRender: true});
        await this.browser.typeInto('code', 'bad::code', {clear: true});
        await this.browser.clickInto(['create-duplicate-modal', 'create-duplicate-modal__ok_button'], {
            waitRender: true
        });
        await this.browser.waitForTestIdSelectorInDom('create-duplicate-modal');
        await this.browser.assertImage('code_container');
    });

    it('Дублирование категории через три точки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        const basePath = ['category_row_category_code_1_3', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'duplicate'], {waitRender: true});
        await this.browser.clickInto(['create-duplicate-modal', 'create-duplicate-modal__ok_button'], {
            waitRender: true
        });
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Открытие категории через три точки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        const basePath = ['category_row_category_code_1_1', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'open'], {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.CATEGORY('\\d')));
    });

    it('Деактивировать категорию через три точки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        await this.browser.clickInto(['action-bar', 'hide-inactive'], {waitRender: true});
        const basePath = ['category_row_category_code_1_1', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'deactivate'], {waitRender: true});
        await this.browser.assertImage('category_row_category_code_1_1');
    });

    it('Активировать категорию через три точки. Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'), {region: 'fr'});
        await this.browser.clickInto(['action-bar', 'hide-inactive'], {waitRender: true});
        const basePath = ['category_row_category_code_3_5', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'activate'], {waitRender: true});
        await this.browser.assertImage('category_row_category_code_3_5');
    });

    it('Отмена деактивации категории через три точки, если он в двух прилавках', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        const basePath = ['category_row_category_code_1_3', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'deactivate'], {waitRender: true});
        await this.browser.assertImage('edit-modal', {removeShadows: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__cancel_button'], {waitRender: true});
        await this.browser.assertImage('category_row_category_code_1_3');
    });

    it('Активация категории во всех прилавках через три точки. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'), {region: 'il'});
        await this.browser.clickInto(['action-bar', 'hide-inactive'], {waitRender: true});
        const basePath = ['category_row_category_code_4_5', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'activate'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.assertImage('category_row_category_code_4_5');
    });

    it('Деактивация категории через три точки только в одной из сеток', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        const basePath = ['category_row_category_code_1_3', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'deactivate'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'update-all']);
        await this.browser.clickInto(['edit-modal', 'select-item_group_code_1_2', 'checkbox'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.clickInto(['action-bar', 'hide-inactive'], {waitRender: true});
        await this.browser.typeInto(['action-bar', 'search'], 'category_code_1_3', {clear: true});
        await this.browser.waitForTestIdSelectorNotInDom('categories-table__spinner');
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['categories-table__wrapper', '\\tbody']);

        await this.browser.clickInto('category_row_category_code_1_3_copy', {waitNavigation: true, waitRender: true});
        await this.browser.clickInto('\\[id$="used-in-tab"]', {waitRender: true});
        await this.browser.assertImage('entity-links');

        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_3));
        await this.browser.clickInto('\\[id$="used-in-tab"]', {waitRender: true});
        await this.browser.assertImage('entity-links');
    });

    it('Нельзя создать дубликат категории на прилавке при деактивации через три точки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'), {
            patchStyles: {enableNotifications: true}
        });
        const basePath = ['category_row_category_code_1_3', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'deactivate'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'update-all']);
        await this.browser.clickInto(['edit-modal', 'select-item_group_code_1_2', 'checkbox'], {waitRender: true});
        await this.browser.typeInto(['edit-modal', 'code'], 'category_code_1_3', {clear: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('notification');
        await this.browser.assertImage('notification', {removeShadows: true});
    });

    it('Нельзя активировать категорию через три точки,если у нее нет фото', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'), {
            patchStyles: {enableNotifications: true}
        });
        await this.browser.clickInto(['action-bar', 'hide-inactive'], {waitRender: true});
        const basePath = ['category_row_category_code_1_10', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'activate'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('notification');
        await this.browser.assertImage('notification', {removeShadows: true});
    });
});
