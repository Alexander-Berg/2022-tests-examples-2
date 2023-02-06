import getEntityIdFromUrl from 'tests/e2e/helper/get-entity-id-from-url';
import {infoModels} from 'tests/e2e/seed-db-map';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

type CreateAttributeAndLinkToInfoModelParams = {
    code: string;
    infoModelId: number;
    isImportant?: boolean;
};

describe('История изменений инфомодели', function () {
    async function createAttributeAndLinkToInfoModel(
        ctx: Hermione.TestContext,
        {code, infoModelId, isImportant}: CreateAttributeAndLinkToInfoModelParams
    ) {
        await ctx.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await ctx.browser.typeInto('code', code);
        await ctx.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await ctx.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true, waitNavigation: true});
        const attributeUrl = await ctx.browser.getUrl();
        const attributeId = getEntityIdFromUrl(attributeUrl);

        await ctx.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModelId));
        await ctx.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await ctx.browser.clickInto(['attributes-search'], {waitRender: true});
        await selectAttribute(ctx, code);
        await ctx.browser.clickInto('im-user_attributes-table', {
            waitRender: true
        });
        if (isImportant) {
            await ctx.browser.clickInto(['infomodel-groups-table', 'im_attribute-group_row_undefined']);
            await ctx.browser.clickInto([`im_attribute_row_${code}`, 'switch-important']);
        }
        await ctx.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        return attributeId;
    }

    async function selectAttribute(ctx: Hermione.TestContext, code: string) {
        await ctx.browser.clickInto(['attributes-search'], {waitRender: true});

        await ctx.browser.typeInto('attributes-search', code, {clear: true});
        await ctx.browser.clickInto(['attribute-select-virtual-list', code]);
    }

    it('Запись о создании пустой инфомодели', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL);
        await this.browser.typeInto('code', 'test_info_model_code');
        await this.browser.clickInto('submit-button');
        await this.browser.clickInto('\\#rc-tabs-1-tab-history-of-changes-tab', {waitForClickable: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись о смене названия инфомодели', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_1));
        await this.browser.typeInto(['translations', 'ru', 'name'], 'New name', {clear: true});
        await this.browser.clickInto('submit-button');
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitForClickable: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись о удалении описания на английском у инфомодели. Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.fr.info_model_code_3_1), {region: 'fr'});
        await this.browser.typeInto(['translations', 'en', 'description'], '', {clear: true});
        await this.browser.clickInto('submit-button');
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitForClickable: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись о добавлении всех типов атрибутов в инфомодель', async function () {
        const allTypes = [
            'boolean_attribute_code_0_0',
            'image_attribute_code_1_0',
            'multiselect_attribute_code_2_0',
            'number_attribute_code_3_0',
            'select_attribute_code_4_0',
            'string_attribute_code_5_0',
            'text_attribute_code_6_0'
        ];
        const requiredAttributes = ['multiselect_attribute_code_2_0', 'boolean_attribute_code_0_0'];

        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL);
        await this.browser.typeInto('code', 'test_info_model_code');

        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['attributes-search'], {waitRender: true});
        for (const type of allTypes) {
            await selectAttribute(this, type);
        }
        await this.browser.clickInto('im-user_attributes-table', {
            waitRender: true
        });

        for (const requiredAttribute of requiredAttributes) {
            await this.browser.clickInto([`im_attribute_row_${requiredAttribute}`, 'switch-important'], {
                waitRender: true
            });
        }

        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto('\\#rc-tabs-1-tab-history-of-changes-tab', {waitForClickable: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись об изменении важности атрибута в инфомодели', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_1));

        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});

        const switchingAttributes = ['multiselect_attribute_code_2_0', 'image_attribute_code_1_0'];
        for (const switchingAttribute of switchingAttributes) {
            await this.browser.clickInto([`im_attribute_row_${switchingAttribute}`, 'switch-important'], {
                waitRender: true
            });
        }

        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitForClickable: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись о удалении атрибута из инфомодели', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_1));

        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['im_attribute_row_image_attribute_code_1_0', 'delete'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitForClickable: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись о добавлении атрибута в инфомомодель', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_1));

        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['attributes-search'], {waitRender: true});
        await this.browser.clickInto(['attribute-select-virtual-list', 'boolean_attribute_code_0_1']);
        await this.browser.clickInto('im-user_attributes-table', {
            waitRender: true
        });

        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitForClickable: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Поиск по истории инфомодели', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_1));

        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitForClickable: true});
        await this.browser.typeInto('history-of-changes_search', 'image');

        await this.browser.assertImage('query-state-spinner');
    });

    it('Удаленный из системы атрибут в истории ИМ', async function () {
        const attributeId = await createAttributeAndLinkToInfoModel(this, {
            code: 'test_code',
            infoModelId: infoModels.ru.info_model_code_1_1
        });

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributeId));
        await this.browser.clickInto(['header-panel', 'delete-button'], {waitRender: true});
        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_1));
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab');

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Удаленный из ИМ, а затем из системы атрибут', async function () {
        const attributeId = await createAttributeAndLinkToInfoModel(this, {
            code: 'test_code',
            infoModelId: infoModels.ru.info_model_code_1_1
        });

        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['infomodel-groups-table', 'im_attribute-group_row_undefined']);
        await this.browser.clickInto(['im_attribute_row_test_code', 'delete']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributeId));
        await this.browser.clickInto(['header-panel', 'delete-button'], {waitRender: true});
        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_1));
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab');

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Удаленный из системы обязательный атрибут', async function () {
        const attributeId = await createAttributeAndLinkToInfoModel(this, {
            code: 'test_code',
            infoModelId: infoModels.ru.info_model_code_1_1,
            isImportant: true
        });

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributeId));
        await this.browser.clickInto(['header-panel', 'delete-button'], {waitRender: true});
        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_1));
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab');

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Поиск по удаленным атрибутам в истории', async function () {
        const attributeId = await createAttributeAndLinkToInfoModel(this, {
            code: 'test_code',
            infoModelId: infoModels.ru.info_model_code_1_1,
            isImportant: true
        });

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributeId));
        await this.browser.clickInto(['header-panel', 'delete-button'], {waitRender: true});
        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_1));
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitRender: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.typeInto('history-of-changes_search', 'test_code');
        await this.browser.assertImage('history-of-changes_list', {stretch: true});
    });
});
