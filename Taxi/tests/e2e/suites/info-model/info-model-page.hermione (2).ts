import {infoModels, rootInfoModels} from 'tests/e2e/seed-db-map';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {USER_LOGIN} from 'service/seed-db/fixtures';

const translationName = 'Cool name';
const ROOT_INFO_MODEL_ID = rootInfoModels.ru.root;
const INFO_MODEL_ID = infoModels.ru.info_model_code_1_1;
const PRODUCT_ID = 10000115;

describe('Просмотр и редактирование инфомодели', function () {
    it('Заголовок страницы инфомодели в режиме просмотра', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(ROOT_INFO_MODEL_ID));
        await this.browser.assertImage('header-panel');
    });

    it('Просмотр инфомодели не доступен в другом регионе', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(ROOT_INFO_MODEL_ID));
        const path = await this.browser.getPath();
        await this.browser.openPage(path, {region: 'il'});
        await this.browser.assertImage('base-layout');
    });

    it('Клик в "Закрыть" возвращает к таблице инфомоделей', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(ROOT_INFO_MODEL_ID));
        await this.browser.clickInto('close-button', {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.INFOMODELS));
    });

    it('Поле код недоступно для редактирования', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(ROOT_INFO_MODEL_ID));
        await this.browser.waitForTestIdSelectorDisabled('code');
    });

    it('Режим просмотра инфомодели – общий вид', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(INFO_MODEL_ID));
        await this.browser.assertImage('base-layout');

        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.assertImage('info-model-tabs');
    });

    it('Добавить атрибут', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(INFO_MODEL_ID));

        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['attributes-search'], {waitRender: true});
        await this.browser.clickInto(['attribute-select-virtual-list', 'boolean_attribute_code_0_1']);
        await this.browser.clickInto('im-user_attributes-table', {
            waitRender: true
        });
        await this.browser.assertImage('im_attribute_row_boolean_attribute_code_0_1');
    });

    it('Удалить вновь добавленный атрибут', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(INFO_MODEL_ID));
        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['attributes-search'], {waitRender: true});
        await this.browser.clickInto(['attribute-select-virtual-list', 'image_attribute_code_1_1']);
        await this.browser.clickInto('im-user_attributes-table', {
            waitRender: true
        });
        await this.browser.assertImage('im_attribute_row_image_attribute_code_1_1');
        await this.browser.clickInto(['im_attribute_row_image_attribute_code_1_1', 'delete']);
        await this.browser.waitForTestIdSelectorNotInDom('im_attribute_row_image_attribute_code_1_1');
    });

    it('Изменить "Название"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(INFO_MODEL_ID));
        await this.browser.typeInto(['translations', 'name'], translationName, {clear: true});
        await this.browser.clickInto('submit-button');
        await this.browser.assertImage(['translations', 'name']);
    });

    it('Внесение изменений меняет шапку на режим редактирования', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(INFO_MODEL_ID));
        const input = await this.browser.findByTestId(['translations', 'name']);
        const initialValue = await input.getValue();

        await this.browser.typeInto(['translations', 'name'], translationName, {clear: true});
        await this.browser.assertImage('header-panel');
        await this.browser.typeInto(['translations', 'name'], initialValue, {clear: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['im_attribute_row_boolean_attribute_code_0_0', 'switch-important']);
        await this.browser.assertImage('header-panel');
        await this.browser.clickInto(['im_attribute_row_boolean_attribute_code_0_0', 'switch-important']);
    });

    it('Можно отменить внесенные изменения', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(INFO_MODEL_ID));

        await this.browser.typeInto(['translations', 'name'], 'Cool name');
        await this.browser.clickInto('cancel-button', {waitRender: true});
        await this.browser.clickInto('confirmation-modal__ok-button', {waitRender: true});
        await this.browser.assertImage(['translations', 'name']);
    });

    it('Поиск атрибута по коду в модале выбора атрибута', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(ROOT_INFO_MODEL_ID));
        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['attributes-search'], {waitRender: true});
        await this.browser.typeInto('attributes-search', 'string_attribute_code');
        await this.browser.waitUntilRendered();
        await this.browser.waitForTestIdSelectorNotInDom('boolean_attribute_code_0_0');
        await this.browser.waitForTestIdSelectorInDom('string_attribute_code_5_0');
        await this.browser.assertImage('attributes-search');
        await this.browser.assertImage('attribute-select-virtual-list', {removeShadows: true});
    });

    it('Поиск атрибута по названию в модале выбора атрибута', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(ROOT_INFO_MODEL_ID));
        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['attributes-search'], {waitRender: true});
        await this.browser.typeInto('attributes-search', 'истину');
        await this.browser.waitUntilRendered();
        await this.browser.waitForTestIdSelectorNotInDom('boolean_attribute_code_0_0');
        await this.browser.waitForTestIdSelectorInDom('select_attribute_code_4_0');
        await this.browser.assertImage('attributes-search');
        await this.browser.assertImage('attribute-select-virtual-list', {removeShadows: true});
    });

    it('Клик в автора открывает его стафф', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(INFO_MODEL_ID));
        await this.browser.clickInto('entity-header-info_author');

        const handles = await this.browser.getWindowHandles();
        expect(handles.length).to.equal(2);

        await this.browser.switchToWindow(handles[1]);
        expect(await this.browser.getUrl()).to.contain(
            encodeURIComponent(`https://staff.yandex-team.ru/${USER_LOGIN}`)
        );

        await this.browser.closeWindow();
        await this.browser.switchToWindow(handles[0]);
    });

    it('Поменять важность атрибутов в инфомодели', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(INFO_MODEL_ID));

        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['im_attribute_row_boolean_attribute_code_0_0', 'switch-important']);
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorAriaChecked([
            'im_attribute_row_boolean_attribute_code_0_0',
            'switch-important'
        ]);
        await this.browser.assertImage('im_attribute_row_boolean_attribute_code_0_0');
    });

    it('Модал "Отмена изменений"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(INFO_MODEL_ID));
        await this.browser.typeInto(['translations', 'name'], translationName, {clear: true});
        await this.browser.clickInto('cancel-button');
        await this.browser.waitForTestIdSelectorInDom('confirmation-modal');
        await this.browser.assertImage('confirmation-modal', {removeShadows: true});
        await this.browser.clickInto('confirmation-modal__ok-button', {waitRender: true, waitForClickable: true});
        await this.browser.assertImage(['translations', 'name']);
    });

    it('Информация об инфомодели содержит название, автора и дату создания', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(INFO_MODEL_ID));

        await this.browser.assertImage(['entity-header-info']);
    });

    it('Клик к количество товаров ИМ в ее карточке открывает таблицу товаров с этой ИМ', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_14));
        await this.browser.clickInto('products-count-link', {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.assertImage('filter-list');
        await this.browser.assertImage(['products-table', 'table-container', '\\tbody']);
    });

    // eslint-disable-next-line max-len
    it('Клик в количество заполненных товаров ИМ в ее карточке открывает таблицу активных заполненных товаров с этой ИМ', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_14));
        await this.browser.clickInto('filled-products-count-link', {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.assertImage('filter-list');
    });

    // eslint-disable-next-line max-len
    it('Клик в количество не заполненных товаров ИМ в ее карточке открывает таблицу активных незаполненных товаров с этой ИМ', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_14));
        await this.browser.clickInto('not-filled-products-count-link', {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.assertImage('filter-list');
    });

    it('Удалить атрибут из ИМ во Франции', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.fr.info_model_code_3_1), {region: 'fr'});

        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['im_attribute_row_multiselect_attribute_code_2_0', 'delete']);

        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorNotInDom('submit-button');

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(PRODUCT_ID), {region: 'fr'});

        await this.browser.assertImage('attribute_group_code_1', {removeShadows: true});
    });

    it('Удалить все атрибуты группы из ИМ в Великобритании', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.gb.info_model_code_2_1), {region: 'gb'});

        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});

        const attributesToDelete = [
            'multiselect_attribute_code_2_0',
            'image_attribute_code_1_1',
            'image_attribute_code_1_0',
            'boolean_attribute_code_0_1',
            'boolean_attribute_code_0_0'
        ];

        for (const attributeCode of attributesToDelete) {
            await this.browser.clickInto([`im_attribute_row_${attributeCode}`, 'delete']);
        }

        await this.browser.assertImage(['im-user_attributes-table', 'infomodel-groups-table', '\\tbody']);
    });
});
