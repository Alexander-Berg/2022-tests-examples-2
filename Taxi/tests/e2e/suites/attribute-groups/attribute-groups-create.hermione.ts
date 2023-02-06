import {attributes} from 'tests/e2e/seed-db-map';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

const ATTRIBUTE_ID = attributes.multiselect_attribute_code_2_0;

describe('Создание группы атрибутов', function () {
    it('Переход на страницу создания группы по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE_GROUP);

        await this.browser.assertImage('base-layout');
    });

    it('Общий вид формы создания в России и Франции', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE_GROUP);

        await this.browser.assertImage('base-layout-content');

        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE_GROUP, {region: 'fr'});

        await this.browser.assertImage('base-layout-content');
    });

    it('Смена языка интерфейса на странице создания группы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE_GROUP);

        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('ui-lang-select', {waitRender: true});
        await this.browser.clickInto(['ui-lang-select_dropdown-menu', 'fr'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Шапка страницы до заполнения поля код', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE_GROUP);

        await this.browser.assertImage('header-panel');
    });

    it('Ввести невалидное значение в поле Код', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE_GROUP);

        await this.browser.typeInto(['group-parameters', 'group-code'], '420');
        await this.browser.clickInto('submit-button');

        await this.browser.assertImage('group-code_container');
    });

    it('Создать пустую группу с описанием в Британской империи', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE_GROUP);

        await this.browser.typeInto(['group-parameters', 'group-code'], 'light_of_heaven');
        await this.browser.typeInto(['translations', 'en', 'description'], 'can u see the light?');
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUPS, {region: 'gb', dataLang: 'en'});

        await this.browser.assertImage(['group-attributes-table', 'ag_attribute_row_light_of_heaven']);

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(ATTRIBUTE_ID));
        await this.browser.clickInto(['attribute-base_params', 'group-parameter']);
        await this.browser.assertImage('group-parameter_dropdown-menu', {removeShadows: true});
    });

    it('Валидация уникальности кода группы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE_GROUP, {patchStyles: {enableNotifications: true}});

        await this.browser.typeInto(['group-parameters', 'group-code'], 'attribute_group_code_1');
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.waitForTestIdSelectorInDom('notification');
        await this.browser.assertImage('notification', {removeShadows: true});
    });

    it('Поиск атрибута по коду и названию при создании группы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE_GROUP);

        await this.browser.clickInto(['attributes_container', 'attributes-search']);
        await this.browser.typeInto(['attributes_container', 'attributes-search'], 'image');
        await this.browser.waitUntilRendered();

        await this.browser.assertImage(['attributes_container', 'attributes-search']);
        await this.browser.assertImage('attribute-select-virtual-list', {removeShadows: true});

        await this.browser.typeInto(['attributes_container', 'attributes-search'], 'Фото товара', {clear: true});
        await this.browser.waitUntilRendered();

        await this.browser.assertImage(['attributes_container', 'attributes-search']);
        await this.browser.assertImage('attribute-select-virtual-list', {removeShadows: true});
    });

    it('Скролл списка атрибутов при добавлении в группу', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE_GROUP);

        await this.browser.clickInto(['attributes_container', 'attributes-search']);
        await this.browser.performScroll('attribute-select-virtual-list', {direction: 'down'});

        await this.browser.assertImage('attribute-select-virtual-list', {removeShadows: true});
    });

    it('В группу нельзя добавить системный атрибут', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE_GROUP);

        await this.browser.clickInto(['attributes_container', 'attributes-search']);
        await this.browser.typeInto(['attributes_container', 'attributes-search'], 'barcode');
        await this.browser.waitForTestIdSelectorInDom('attribute-select_empty');

        await this.browser.assertImage('attribute-select_empty', {removeShadows: true});
    });
});
