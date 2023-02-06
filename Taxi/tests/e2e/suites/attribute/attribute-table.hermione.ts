import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {USER_LOGIN} from 'service/seed-db/fixtures';

describe('Таблица атрибутов', function () {
    it('Страница атрибутов – общий вид', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES);
        await this.browser.assertImage();
    });

    it('Шапка страницы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES);
        await this.browser.assertImage('header-panel');
    });

    it('Шапка таблицы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES);
        await this.browser.assertImage(['attributes-table_table', '\\thead']);
    });

    it('Экшн-бар содержит поле поиска и активную кнопку "Создать атрибут"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES);
        await this.browser.assertImage('action-bar');
    });

    it('Клик на "Создать атрибут" открывает страницу создания атрибута', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES);
        await this.browser.clickInto('create-button');
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.CREATE_ATTRIBUTE));
    });

    it('Клик в строку таблицы открывает страницу атрибута', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES);
        await this.browser.clickInto('^attributes-table_row', {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.ATTRIBUTE('\\d')));
    });

    it('Клик в автора в таблице атрибутов открывает его стафф', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES);
        await this.browser.clickInto('author-link');
        const handles = await this.browser.getWindowHandles();
        expect(handles.length).to.equal(2);

        await this.browser.switchToWindow(handles[1]);
        expect(await this.browser.getUrl()).to.contain(
            encodeURIComponent(`https://staff.yandex-team.ru/${USER_LOGIN}`)
        );

        await this.browser.closeWindow();
        await this.browser.switchToWindow(handles[0]);
    });

    it('Скролл таблицы атрибутов при развернутом меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES);

        await this.browser.performScroll('attribute-table_container', {
            direction: 'down',
            beforeIterationDelay: () => this.browser.waitForTestIdSelectorNotInDom('attribute_table__spinner'),
            afterIterationDelay: () => this.browser.waitUntilRendered()
        });

        await this.browser.assertImage('attribute-table_container');
    });

    it('Скролл таблицы атрибутов при свернутом меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES, {collapseSidebar: true});

        await this.browser.performScroll('attribute-table_container', {
            direction: 'down',
            beforeIterationDelay: () => this.browser.waitForTestIdSelectorNotInDom('attribute_table__spinner'),
            afterIterationDelay: () => this.browser.waitUntilRendered()
        });

        await this.browser.assertImage('attribute-table_container');
    });

    it('Поиск атрибута по названию (Россия)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES, {region: 'ru', queryParams: {search: 'штрих'}});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['attributes-table_table', '\\tbody']);
    });

    it('Поиск атрибута по коду (Франция)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES, {
            region: 'fr',
            queryParams: {search: 'boolean_attribute_code'}
        });
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['attributes-table_table', '\\tbody']);
    });

    it('Можно найти атрибут по английскому названию при французском языке данных', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES, {region: 'fr', dataLang: 'fr', uiLang: 'ru'});
        await this.browser.typeInto(['action-bar', 'search'], 'Quis qui repudiandae');

        await this.browser.waitForTestIdSelectorNotInDom('attribute_table__spinner');
        await this.browser.waitUntilRendered();

        await this.browser.assertImage('attributes-table_table');
    });

    it('Можно найти атрибут по названию на иврите при английском языке данных', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES, {region: 'il', dataLang: 'en', uiLang: 'ru'});
        await this.browser.typeInto(['action-bar', 'search'], 'كثير العربى ومؤقتاً');

        await this.browser.waitForTestIdSelectorNotInDom('attribute_table__spinner');
        await this.browser.waitUntilRendered();

        await this.browser.assertImage('attributes-table_table');
    });

    it('Смена языка интерфейса (Франция)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES, {region: 'fr', dataLang: 'fr', uiLang: 'fr'});
        await this.browser.waitUntilRendered();
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('ui-lang-select', {waitRender: true});
        await this.browser.clickInto('en', {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Смена языка данных (Франция)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES, {region: 'fr', dataLang: 'fr', uiLang: 'fr'});
        await this.browser.waitUntilRendered();
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('data-lang-select', {waitRender: true});
        await this.browser.clickInto(['data-lang-select_dropdown-menu', 'en'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Свернуть и развернуть меню на странице Атрибутов Израиля', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES, {region: 'il'});
        await this.browser.clickInto('sidebar-switcher', {waitRender: true});
        await this.browser.clickInto('sidebar-switcher', {waitRender: true});
        await this.browser.assertImage();
    });
});
