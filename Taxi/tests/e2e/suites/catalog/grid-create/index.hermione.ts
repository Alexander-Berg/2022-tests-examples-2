import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Создание сеток в витрине', function () {
    it('Общий вид формы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorDisabled(['create-modal', 'create-modal__ok_button']);
        await this.browser.assertImage('create-modal', {removeShadows: true});
    });

    it('Закрытие формы создания сетки крестом', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('create-modal');

        await this.browser.clickInto(['create-modal', '\\.ant-modal-close'], {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom('create-modal');
    });

    it('Нельзя создать сетку с кодом, который уже существует', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'), {
            patchStyles: {enableNotifications: true}
        });
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'grid_code_1_1');
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('notification');
        await this.browser.assertImage('notification', {removeShadows: true});
    });

    it('Создать неактивную сетку с описанием', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_grid_code');
        await this.browser.clickInto(['status', 'disabled']);
        await this.browser.typeInto('description', 'test_grid_description');
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});

        await this.browser.assertImage('base-layout');
    });

    it('Создать активную сетку. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'), {region: 'il'});
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_grid_code');
        await this.browser.clickInto(['status', 'active']);
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});

        await this.browser.assertImage(['catalog-layout_info', 'status']);
    });

    it('Создание сетки с названием на разных языках. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'), {region: 'il'});
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_grid_code');
        await this.browser.clickInto(['translations', 'ru'], {waitRender: true});
        await this.browser.typeInto(['translations', 'long-title-ru'], 'test_grid_long_title_ru');
        await this.browser.clickInto(['translations', 'en'], {waitRender: true});
        await this.browser.typeInto(['translations', 'short-title-en'], 'test_grid_short_title_en');
        await this.browser.clickInto(['translations', 'he'], {waitRender: true});
        await this.browser.typeInto(['translations', 'long-title-he'], 'test_grid_long_title_he');
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});

        await this.browser.clickInto(['catalog-layout_info', 'translations', 'ru']);
        await this.browser.assertImage(['catalog-layout_info', 'translations']);
        await this.browser.clickInto(['catalog-layout_info', 'translations', 'en']);
        await this.browser.assertImage(['catalog-layout_info', 'translations']);
        await this.browser.clickInto(['catalog-layout_info', 'translations', 'he']);
        await this.browser.assertImage(['catalog-layout_info', 'translations']);
    });

    it('Создание сетки с валидным полем мета', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_grid_code');
        await this.browser.typeInto('meta', '{"number": 123, "string": "abc"}', {clear: true});
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});
        await this.browser.assertImage(['catalog-layout_info', 'meta']);
    });

    it('Создание сетки с невалидным полем мета', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});

        await this.browser.typeInto('code', 'test_grid_code');
        await this.browser.typeInto('meta', '{"number": 123]]]', {clear: true});
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('create-modal');
        await this.browser.assertImage('meta_container');
    });

    it('Смена языка интерфейса в форме создания сетки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'), {uiLang: 'en'});
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorDisabled(['create-modal', 'create-modal__ok_button']);
        await this.browser.assertImage('create-modal', {removeShadows: true});
    });

    it('Новые сетки не прорастают в другие регионы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_grid_code');
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('catalog-layout_info');

        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'), {region: 'fr'});
        await this.browser.typeInto('search', 'test_grid_code');
        await this.browser.waitForTestIdSelectorNotInDom('infinite-table_loader');
        await this.browser.waitForTestIdSelectorInDom('empty-placeholder');
    });

    it('Валидация кода при создании сетки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});

        await this.browser.typeInto('code', 'bad::code');
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('create-modal');
        await this.browser.assertImage('code_container');
    });
});
