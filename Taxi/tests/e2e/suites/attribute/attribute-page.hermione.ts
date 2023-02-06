import {attributeGroups, attributes, requiredAttributes} from 'tests/e2e/seed-db-map';
import setAttributeConfirmationValue from 'tests/e2e/utils/confirm-attribute';
import makeAttributeConfirmable from 'tests/e2e/utils/make-attribute-confirmable';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {DbTable} from '@/src/entities/const';
import {USER_LOGIN} from 'service/seed-db/fixtures';

describe('Просмотр и редактирование атрибута', function () {
    it('Заголовок страницы атрибута в режиме просмотра', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(requiredAttributes.barcode));
        await this.browser.assertImage('header-panel');
    });

    it('Блок с информацией об атрибуте', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(requiredAttributes.barcode));
        await this.browser.assertImage('entity-header-info');
        await this.browser.assertImage(['attribute-tabs', '\\.ant-tabs-nav']);
    });

    it('Просмотр атрибута доступен в другом регионе', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(requiredAttributes.barcode));
        const path = await this.browser.getPath();
        await this.browser.openPage(path, {region: 'il'});
        await this.browser.assertImage('header');
        await this.browser.assertImage('entity-header-info');
    });

    it('Клик в "Закрыть" возвращает к таблице атрибутов', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(requiredAttributes.barcode));
        await this.browser.clickInto('close-button', {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.ATTRIBUTES));
    });

    it('Основные параметры атрибута недоступны для редактирования', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(requiredAttributes.barcode));
        await this.browser.waitForTestIdSelectorDisabled('code');
        await this.browser.waitForTestIdSelectorDisabled('ticket-parameter');

        const typeSelect = await this.browser.findByTestId('attribute-type');
        const typeSelectInput = await typeSelect.$('input');
        await typeSelectInput.waitForEnabled({reverse: true});
    });

    it('"Наименования и описания" доступны для редактирования', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(requiredAttributes.barcode));

        const translations = await this.browser.findByTestId(['translations']);
        const fields = await translations.$$('input,textarea');

        expect(fields).lengthOf(8); // (name+description) * (ru+en+il+fr)
        for (const field of fields) {
            await field.waitForEnabled();
        }

        await this.browser.assertImage('translations');
    });

    it('Добавляется новая опция выпадающего списка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributes.multiselect_attribute_code_2_0));
        await this.browser.clickInto('select-option-add', {waitRender: true});
        await this.browser.assertImage('select-option');
    });

    it('Блок с опцией можно развернуть и свернуть', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributes.multiselect_attribute_code_2_0));

        // Expand then Collapse
        for (let i = 0; i < 2; i++) {
            await this.browser.clickInto('select-option-header-attribute_option_code_10_1', {waitRender: true});
            await this.browser.assertImage('select-option');
        }
    });

    it('Удаляется добавленная опция выпадающего списка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributes.multiselect_attribute_code_2_0));
        await this.browser.clickInto('select-option-add', {waitRender: true});
        await this.browser.clickInto(['select-option', 'select-option-header', 'select-option-delete'], {
            waitRender: true
        });
        await this.browser.assertImage('select-option');
    });

    it('Клик в автора атрибута открывает его стафф', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(requiredAttributes.barcode));
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

    it('Внести изменение в атрибут', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributes.boolean_attribute_code_0_0));

        const nameElement = await this.browser.findByTestId(['translations', 'ru', 'name']);
        const nameValue = await nameElement.getValue();

        await this.browser.typeInto(['translations', 'ru', 'name'], nameValue.split('').reverse().join(''), {
            clear: true
        });
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom('query-state-spinner-spinning');

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES);
        await this.browser.assertImage('attributes-table_row_boolean_attribute_code_0_0');
    });

    it('Добавить группу и изменить группу на другую', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributes.text_attribute_code_6_2_loc));

        await this.browser.clickInto(['attribute-base_params', 'group-parameter']);
        await this.browser.clickInto(['group-parameter_dropdown-menu', 'attribute_group_code_1']);
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorNotInDom('submit-button');

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUP(attributeGroups.attribute_group_code_1));

        await this.browser.assertImage(['attributes_container']);

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributes.text_attribute_code_6_2_loc));

        await this.browser.clickInto(['attribute-base_params', 'group-parameter']);
        await this.browser.clickInto(['group-parameter_dropdown-menu', 'attribute_group_code_2']);
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorNotInDom('submit-button');

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUP(attributeGroups.attribute_group_code_2));

        await this.browser.assertImage(['attributes_container']);
    });

    it('Убрать группу у атрибута', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributes.boolean_attribute_code_0_0));

        await this.browser.clickInto(['attribute-base_params', 'group-parameter']);
        await this.browser.clickInto(['group-parameter_dropdown-menu', 'without-group']);
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorNotInDom('submit-button');

        await this.browser.clickInto(['\\#rc-tabs-0-tab-history']);
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUP(attributeGroups.attribute_group_code_1));

        await this.browser.assertImage(['attributes_container']);
    });

    it('Окно выбора группы со скроллом', async function () {
        await this.browser.executeSql(
            `
            INSERT INTO ${DbTable.ATTRIBUTE_GROUP} (code, sort_order)
            VALUES
                ('how', 3),
                ('are', 4),
                ('you', 5);`
        );

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributes.boolean_attribute_code_0_0));
        await this.browser.clickInto(['attribute-base_params', 'group-parameter']);
        await this.browser.performScroll(['group-parameter_dropdown-menu', '\\.rc-virtual-list-holder'], {
            direction: 'down'
        });

        await this.browser.assertImage('group-parameter_dropdown-menu', {removeShadows: true});
    });

    // eslint-disable-next-line max-len
    it('При просмотре атрибута поле подтверждаемости задизейблено для подтверждаемых и неподтверждаемых атрибутов', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributes.boolean_attribute_code_0_0));

        await this.browser.waitForTestIdSelectorDisabled([
            'attribute-base_params',
            'is-confirmable_container',
            'is-confirmable'
        ]);

        await makeAttributeConfirmable(this.browser, attributes.boolean_attribute_code_0_0);

        await this.browser.refresh();

        await this.browser.waitForTestIdSelectorDisabled([
            'attribute-base_params',
            'is-confirmable_container',
            'is-confirmable'
        ]);
    });

    it('МП: "Необходимо подтверждать" доступно в форме  редактирования атрибута', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributes.boolean_attribute_code_0_0));

        await this.browser.waitForTestIdSelectorEnabled([
            'attribute-base_params',
            'is-confirmable_container',
            'is-confirmable'
        ]);
    });

    it('МП: Нельзя снять подтверждаемость при начилии подтвержденных в товарах', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        await makeAttributeConfirmable(this.browser, attributes.boolean_attribute_code_0_0);
        await setAttributeConfirmationValue({
            browser: this.browser,
            productIdentifier: 10000001,
            attributeId: attributes.boolean_attribute_code_0_0
        });

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributes.boolean_attribute_code_0_0));

        await this.browser.assertImage(['attribute-base_params', 'is-confirmable_container']);

        const checkbox = await this.browser.findByTestId([
            'attribute-base_params',
            'is-confirmable_container',
            'is-confirmable'
        ]);
        await checkbox.moveTo();

        await this.browser.waitUntilRendered();

        await this.browser.assertImage('\\.ant-tooltip-inner', {removeShadows: true});
    });
});
