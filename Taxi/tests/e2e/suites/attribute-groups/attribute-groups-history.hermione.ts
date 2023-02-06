import {attributeGroups} from 'tests/e2e/seed-db-map';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

const ATTRIBUTE_GROUP_ID = attributeGroups.attribute_group_code_1;

describe('История группы', function () {
    it('История создания группы с атрибутами в Великобритании', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE_GROUP, {region: 'gb', uiLang: 'en'});

        await this.browser.typeInto(['group-parameters', 'group-code'], 'lion_heart');

        await this.browser.clickInto(['attributes_container', 'attributes-search']);
        await this.browser.performScroll('attribute-select-virtual-list', {direction: 'down'});
        await this.browser.clickInto(['attribute-select-virtual-list', 'text_attribute_code_6_2_loc']);
        await this.browser.clickInto(['attribute-select-virtual-list', 'image']);

        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage('history-of-changes_list');

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUPS, {region: 'ru', uiLang: 'ru'});
        await this.browser.assertImage(['group-attributes-table', 'ag_attribute_row_lion_heart']);
    });

    it('Запись о создании группы без атрибутов в России', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE_GROUP);

        await this.browser.typeInto(['group-parameters', 'group-code'], 'pushkin');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await this.browser.assertImage('history-of-changes_list');
    });

    it('Запись об изменении данных группы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUP(ATTRIBUTE_GROUP_ID));

        await this.browser.clickInto([
            'attributes_container',
            'ag_attribute_row_multiselect_attribute_code_2_0',
            'delete'
        ]);

        await this.browser.clickInto(['attributes_container', 'attributes-search']);
        await this.browser.performScroll('attribute-select-virtual-list', {direction: 'down'});
        await this.browser.clickInto(['attribute-select-virtual-list', 'text_attribute_code_6_2_loc']);
        await this.browser.clickInto(['group-parameters']);

        await this.browser.dragAndDrop(
            ['attributes_container', 'ag_attribute_row_image_attribute_code_1_1'],
            ['attributes_container', 'ag_attribute_row_boolean_attribute_code_0_0'],
            {offset: 'bottom'}
        );

        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);

        await this.browser.clickInto('\\#rc-tabs-0-tab-parameters-tab');
        await this.browser.typeInto(['translations', 'ru', 'name'], 'Меллон', {clear: true});
        await this.browser.typeInto(['translations', 'ru', 'description'], 'Молви друг и войдешь', {clear: true});

        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await this.browser.assertImage(['history-of-changes_list', 'list-item-3']);
    });
});
