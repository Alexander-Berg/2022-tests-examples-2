import {attributeGroups, attributes, infoModels} from 'tests/e2e/seed-db-map';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

const ATTRIBUTE_GROUP_ID = attributeGroups.attribute_group_code_1;
const SECOND_ATTRIBUTE_GROUP_ID = attributeGroups.attribute_group_code_2;
const INFO_MODEL_ID = infoModels.ru.info_model_code_1_1;
const ATTRIBUTE_ID = attributes.boolean_attribute_code_0_0;
const PRODUCT_ID = 10000001;

describe('Просмотр и редактирование группы', function () {
    it('Общий вид карточки группы Великобритании', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUP(ATTRIBUTE_GROUP_ID), {region: 'gb', uiLang: 'en'});

        await this.browser.assertImage('base-layout');
    });

    it('Переход в группу во Франции по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUP(ATTRIBUTE_GROUP_ID), {region: 'fr', uiLang: 'fr'});

        await this.browser.assertImage('header');
    });

    it('Поле код нельзя редактировать', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUP(ATTRIBUTE_GROUP_ID));

        await this.browser.assertImage(['group-parameters', 'group-code_field']);
    });

    it('Добавить в группу атрибут другой группы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUP(SECOND_ATTRIBUTE_GROUP_ID));

        await this.browser.clickInto(['attributes_container', 'attributes-search']);
        await this.browser.clickInto(['attribute-select-virtual-list', 'boolean_attribute_code_0_0']);
        await this.browser.clickInto('group-parameters');
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.waitForTestIdSelectorInDom('confirmation-modal');
        await this.browser.assertImage(['confirmation-modal'], {removeShadows: true});

        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom('submit-button');

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(ATTRIBUTE_ID));

        await this.browser.assertImage(['attribute-base_params', 'group-parameter']);

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(INFO_MODEL_ID));
        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['infomodel-groups-table', 'im_attribute-group_row_attribute_group_code_2'], {
            waitRender: true
        });
        await this.browser.assertImage(['im-user_attributes-table', 'infomodel-attributes-table', '\\tbody']);
    });

    it('Удалить атрибут из группы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUP(ATTRIBUTE_GROUP_ID));

        await this.browser.clickInto(['attributes_container', 'ag_attribute_row_boolean_attribute_code_0_0', 'delete']);
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.assertImage(['attributes_container', 'group-attributes-table']);

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(ATTRIBUTE_ID));

        await this.browser.assertImage(['attribute-base_params', 'group-parameter']);
    });

    it('Поменять местами атрибуты группы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUP(ATTRIBUTE_GROUP_ID));

        await this.browser.dragAndDrop(
            ['attributes_container', 'ag_attribute_row_image_attribute_code_1_0'],
            ['attributes_container', 'ag_attribute_row_boolean_attribute_code_0_0'],
            {offset: 'bottom'}
        );
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom('submit-button');

        await this.browser.assertImage(['attributes_container', 'group-attributes-table']);

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(INFO_MODEL_ID));
        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});

        await this.browser.assertImage(['im-user_attributes-table', 'infomodel-attributes-table', '\\tbody']);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(PRODUCT_ID));

        await this.browser.assertImage('attribute_group_code_1', {removeShadows: true});
    });

    it('Отображение добавленного аттрибута в списке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUP(ATTRIBUTE_GROUP_ID));

        await this.browser.clickInto(['attributes_container', 'attributes-search']);

        await this.browser.assertImage(['attribute-select-virtual-list', 'boolean_attribute_code_0_0']);

        await this.browser.clickInto(['attribute-select-virtual-list', 'boolean_attribute_code_0_0']);

        await this.browser.assertImage(['attribute-select-virtual-list', 'boolean_attribute_code_0_0']);
    });

    it('Изменить название и описание группы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUP(ATTRIBUTE_GROUP_ID));

        await this.browser.typeInto(['translations', 'ru', 'name'], 'Меллон', {clear: true});
        await this.browser.typeInto(['translations', 'ru', 'description'], 'Молви друг и войдешь', {clear: true});

        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUPS);

        await this.browser.assertImage(['group-attributes-table', 'ag_attribute_row_attribute_group_code_1']);
    });
});
