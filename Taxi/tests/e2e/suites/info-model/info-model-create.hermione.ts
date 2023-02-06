import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Создание инфомодели', function () {
    it('Шапка страницы создания инфомодели', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL);
        await this.browser.assertImage('header-panel');
    });

    it('Дефолтное состояние формы создания ИМ (Россия, русский язык)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL, {region: 'ru', uiLang: 'ru', dataLang: 'ru'});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('info-model-tabs');
        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.assertImage('info-model-tabs');
    });

    it('Клик на кнопку "Создать инфомодель" открывает страницу создания инфомодели', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.clickInto('create-button', {waitNavigation: true, waitRender: true});
        await this.browser.assertImage();
    });

    it('Клик в "Отмена" возвращает к таблице инфомоделей', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL);
        await this.browser.clickInto('cancel-button', {waitNavigation: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.INFOMODELS));
    });

    it('Клик в "Отмена" после внесения изменений открывает модал "Отмена изменений"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL);
        await this.browser.typeInto('code', 'mycode');
        await this.browser.clickInto('cancel-button', {waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.CREATE_INFOMODEL));
        await this.browser.assertImage('confirmation-modal', {removeShadows: true});
    });

    it('Ввод валидного значения поля код', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL);
        await this.browser.typeInto('code', 'validcode');

        // На невалидный код получим то же самое, т. к. валидация срабатывает после клика на "Создать".
        // Но в будущем может изменим валидацию.
        await this.browser.assertImage('header-panel');
    });

    it('Ввод невалидного значения поля код', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL);
        await this.browser.typeInto('code', 'invalid code!');
        // Сейчас только при клике на "Создать", срабатывает валидация.
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.assertImage('infomodel-base_params', {removeShadows: true});
    });

    it('Создание инфомодели без атрибутов', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL);
        await this.browser.typeInto('code', 'test_info_model_code');

        await this.browser.clickInto('submit-button', {waitRender: true, waitNavigation: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.INFOMODEL('\\d')));
        await this.browser.assertImage('infomodel_params');

        await this.browser.clickInto('\\#rc-tabs-1-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.assertImage('im-user_attributes-table');
    });

    it('Клик в инпут поиска открывает окно выбора атрибутов', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL);
        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['attributes-search'], {waitRender: true});

        await this.browser.assertImage(['attribute-select-virtual-list'], {removeShadows: true});
    });

    it('Добавить и удалить атрибут (проверка влкадки "Пользовательские атрибуты")', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL);
        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['attributes-search'], {waitRender: true});
        await this.browser.clickInto(['attribute-select-virtual-list', 'boolean_attribute_code_0_0']);
        await this.browser.clickInto('im-user_attributes-table', {
            waitRender: true
        });
        await this.browser.assertImage('im-user_attributes-table');
        await this.browser.clickInto(['im_attribute_row_boolean_attribute_code_0_0', 'delete'], {waitRender: true});
        await this.browser.assertImage('im-user_attributes-table');
    });

    it('Создание инфомодели с атрибутами', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL);
        await this.browser.typeInto('code', 'test_info_model_code');

        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['attributes-search'], {waitRender: true});
        await this.browser.clickInto(['attribute-select-virtual-list', 'boolean_attribute_code_0_0']);
        await this.browser.clickInto(['attribute-select-virtual-list', 'image_attribute_code_1_0']);

        await this.browser.clickInto('submit-button', {waitRender: true, waitNavigation: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.INFOMODEL('\\d')));
        await this.browser.assertImage('infomodel_params');

        await this.browser.clickInto('\\#rc-tabs-1-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.assertImage('im-user_attributes-table');
    });

    it('Просмотр созданной инфомодели в таблице', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL);
        await this.browser.typeInto('code', 'test_info_model_code_666');
        await this.browser.clickInto('submit-button', {waitNavigation: true});

        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.typeInto(['action-bar', 'search'], 'test_info_model_code_666');

        await this.browser.waitForTestIdSelectorNotInDom('infomodels-table__spinner');
        await this.browser.waitUntilRendered();

        await this.browser.assertImage('infomodels-table');
    });

    it('Смена языка интерфейса на странице создания ИМ (Франция)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL, {region: 'fr', dataLang: 'fr', uiLang: 'fr'});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('ui-lang-select', {waitRender: true});
        await this.browser.clickInto(['ui-lang-select_dropdown-menu', 'ru'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Изменить язык интерфейса + проверить вид формы (английский язык)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL, {region: 'ru', dataLang: 'ru', uiLang: 'ru'});
        await this.browser.waitUntilRendered();
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('ui-lang-select', {waitRender: true});
        await this.browser.clickInto('en', {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('info-model-tabs');
        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.assertImage('info-model-tabs');
    });

    it('Изменить регион (Великобритания) – проверить блок "Наименования и описания"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL, {region: 'ru', dataLang: 'ru', uiLang: 'ru'});
        await this.browser.waitUntilRendered();
        await this.browser.clickInto('region-switcher', {waitRender: true});
        await this.browser.clickInto('GB', {waitNavigation: true, waitRender: true});
        await this.browser.assertImage(['infomodel-view', 'translations'], {removeShadows: true});
    });

    it('Изменить регион (Франция) – проверить блок "Наименования и описания"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL, {region: 'ru', dataLang: 'ru', uiLang: 'ru'});
        await this.browser.waitUntilRendered();
        await this.browser.clickInto('region-switcher', {waitRender: true});
        await this.browser.clickInto('FR', {waitNavigation: true, waitRender: true});
        await this.browser.assertImage(['infomodel-view', 'translations'], {removeShadows: true});
    });

    it('Изменить регион (Израиль) – проверить блок "Наименования и описания"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL, {region: 'ru', dataLang: 'ru', uiLang: 'ru'});
        await this.browser.waitUntilRendered();
        await this.browser.clickInto('region-switcher', {waitRender: true});
        await this.browser.clickInto('IL', {waitNavigation: true, waitRender: true});
        await this.browser.assertImage(['infomodel-view', 'translations'], {removeShadows: true});
    });
});
