import {attributes, infoModels} from 'tests/e2e/seed-db-map';
import makeDataTestIdSelector from 'tests/e2e/utils/make-data-test-id-selector';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

const INFO_MODEL_ID = infoModels.ru.info_model_code_1_1;
const PRODUCT_ID = 10000001;
const ATTRIBUTE_ID = attributes.multiselect_attribute_code_2_0;

describe('Таблица групп атрибутов', function () {
    it('Общий вид таблицы групп', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUPS);

        await this.browser.assertImage('base-layout');
    });

    it('Переход по прямой ссылке на страницу групп Франции', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUPS, {region: 'fr', uiLang: 'fr'});

        await this.browser.assertImage('header');
    });

    it('Поиск группы по названию и по коду в Великобритании', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUPS, {region: 'gb'});

        await this.browser.typeInto(['action-bar', 'search'], 'facer');
        await this.browser.waitForTestIdSelectorNotInDom('ag_attribute_row_attribute_group_code_1');
        await this.browser.assertImage('group-attributes-table');

        await this.browser.typeInto(['action-bar', 'search'], 'group_code_2', {clear: true});
        await this.browser.waitForTestIdSelectorNotInDom('ag_attribute_row_attribute_group_code_1');
        await this.browser.assertImage('group-attributes-table');
    });

    it('Поиск группы по названию и по коду атрибута во Франции', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUPS, {region: 'fr', uiLang: 'fr'});

        await this.browser.typeInto(['action-bar', 'search'], 'image_attribute');
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('group-attributes-table');

        await this.browser.typeInto(['action-bar', 'search'], 'Consequatur', {clear: true});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('group-attributes-table');
    });

    it('Изменить язык интерфейса на странице групп', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUPS, {noCookies: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('ui-lang-select', {waitRender: true});
        await this.browser.clickInto('fr', {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout', {
            ignoreElements: makeDataTestIdSelector(['attribute_group-table__container', '\\.ant-table-tbody'])
        });
    });

    it('Переместить группу', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUPS);

        await this.browser.dragAndDrop(
            'ag_attribute_row_attribute_group_code_1',
            'ag_attribute_row_attribute_group_code_3',
            {
                offset: 'bottom'
            }
        );

        await this.browser.assertImage(['group-attributes-table'], {ignoreElements: '.ant-table-thead'});

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(INFO_MODEL_ID));
        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.assertImage(['im-user_attributes-table', 'infomodel-groups-table', '\\tbody']);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(PRODUCT_ID));
        await this.browser.assertImage('product_view', {
            ignoreElements: [
                makeDataTestIdSelector('basic-attributes'),
                makeDataTestIdSelector('product-image'),
                makeDataTestIdSelector('group-content')
            ],
            compositeImage: true
        });
    });

    it('Клик в "Создать группу атрибутов" открывает страницу создания группы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUPS);

        await this.browser.clickInto('create-button');

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.CREATE_ATTRIBUTE_GROUP));
    });

    it('Клик в строку таблицы открывает страницу этой группы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUPS);

        await this.browser.clickInto(['group-attributes-table', 'ag_attribute_row_attribute_group_code_1']);

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.ATTRIBUTE_GROUP('1')));
    });

    it('Удалить группу через контекстное меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUPS);

        await this.browser.clickInto([
            'group-attributes-table',
            'ag_attribute_row_attribute_group_code_1',
            'table-more-button'
        ]);
        await this.browser.clickInto([
            'group-attributes-table',
            'ag_attribute_row_attribute_group_code_1',
            'delete-group'
        ]);
        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom('ag_attribute_row_attribute_group_code_1');

        await this.browser.assertImage(['group-attributes-table'], {ignoreElements: '.ant-table-thead'});

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(ATTRIBUTE_ID));

        await this.browser.assertImage(['attribute-base_params', 'group-parameter_container']);

        await this.browser.clickInto(['\\#rc-tabs-0-tab-history']);
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Изменить регион на странице групп', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUPS);

        await this.browser.clickInto('region-switcher', {waitRender: true});
        await this.browser.clickInto('FR', {waitNavigation: true, waitRender: true});

        await this.browser.assertImage('group-attributes-table');
    });
});
