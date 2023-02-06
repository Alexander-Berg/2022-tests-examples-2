import getEntityIdFromUrl from 'tests/e2e/helper/get-entity-id-from-url';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

const SYSTEM_ATTRIBUTE_ID = 1;
const MULTISELECT_ATTRIBUTE_ID = 10;

describe('Удаление атрибута', function () {
    it('Атрибут системный - удалить нельзя', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(SYSTEM_ATTRIBUTE_ID));
        await this.browser.waitForTestIdSelectorDisabled(['header-panel', 'delete-button']);
        await this.browser.assertImage('header-panel');
    });

    it('Атрибут привязан к инфомодели, но не заполнен в товаре - можно удалить', async function () {
        const infoModelId = 5;
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.typeInto('code', 'test_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});
        const attributeUrl = await this.browser.getUrl();
        const attributeId = getEntityIdFromUrl(attributeUrl);

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModelId));
        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['attributes-search'], {waitRender: true});
        await this.browser.typeInto('attributes-search', 'test_attribute_code', {clear: true});
        await this.browser.waitUntilRendered();
        await this.browser.clickInto(['attribute-select-virtual-list', 'test_attribute_code']);
        await this.browser.clickInto('im-user_attributes-table', {
            waitRender: true
        });
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributeId));
        await this.browser.clickInto('delete-button', {waitRender: true});
        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributeId));
        await this.browser.waitForTestIdSelectorInDom('entity-not-found');
    });

    it('Атрибут заполнен в товаре, в том числе в качестве фантомного - удалить нельзя', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(MULTISELECT_ATTRIBUTE_ID));
        await this.browser.assertImage('header-panel');
    });

    it('Удаление атрибута удовлетворяющего требованиям', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.typeInto('code', 'test_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});
        const attributeUrl = await this.browser.getUrl();
        const attributeId = getEntityIdFromUrl(attributeUrl);

        await this.browser.clickInto('delete-button', {waitRender: true});
        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributeId));
        await this.browser.waitForTestIdSelectorInDom('entity-not-found');
    });

    it('Проверка изменения состояния. Можно удалить -> Нельзя и наоборот', async function () {
        const productId = '10000002';
        const infoModelId = '19';
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type');
        await this.browser.clickInto(['attribute-type_dropdown-menu', 'number']);
        await this.browser.typeInto('code', 'test_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});
        await this.browser.waitForTestIdSelectorEnabled('delete-button');
        const attributeUrl = await this.browser.getUrl();
        const attributeId = getEntityIdFromUrl(attributeUrl);

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModelId));
        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['attributes-search'], {waitRender: true});
        await this.browser.typeInto('attributes-search', 'test_attribute_code', {clear: true});
        await this.browser.waitUntilRendered();
        await this.browser.clickInto(['attribute-select-virtual-list', 'test_attribute_code']);
        await this.browser.clickInto('im-user_attributes-table', {
            waitRender: true
        });
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(productId));
        await this.browser.typeInto('test_attribute_code', '123');
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributeId));
        await this.browser.waitForTestIdSelectorDisabled('delete-button');

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(productId));
        await this.browser.typeInto('test_attribute_code', '', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributeId));
        await this.browser.waitForTestIdSelectorEnabled('delete-button');
    });

    it('После удаления можно создать Атрибут с тем же кодом', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.typeInto('code', 'test_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});
        await this.browser.clickInto(['header-panel', 'delete-button']);
        await this.browser.clickInto('confirmation-modal__ok-button', {waitNavigation: true, waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.typeInto('code', 'test_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Удалить неизменный не заполненный в товаре атрибут', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.typeInto('code', 'test_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto('is-immutable');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});

        const attributeUrl = await this.browser.getUrl();
        const attributeId = getEntityIdFromUrl(attributeUrl);

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(5));
        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['attributes-search'], {waitRender: true});
        await this.browser.typeInto('attributes-search', 'test_attribute_code', {clear: true});
        await this.browser.waitUntilRendered();
        await this.browser.clickInto(['attribute-select-virtual-list', 'test_attribute_code']);
        await this.browser.clickInto('im-user_attributes-table', {
            waitRender: true
        });
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributeId));
        await this.browser.clickInto(['header-panel', 'delete-button']);
        await this.browser.clickInto('confirmation-modal__ok-button', {waitNavigation: true, waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.ATTRIBUTES));
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributeId));
        await this.browser.waitForTestIdSelectorInDom('entity-not-found');
    });

    it('Нельзя удалить неизменный атрибут, если он заполнен в товаре', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.typeInto('code', 'test_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto('is-immutable');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});

        const attributeUrl = await this.browser.getUrl();
        const attributeId = getEntityIdFromUrl(attributeUrl);

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(5));
        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['attributes-search'], {waitRender: true});
        await this.browser.typeInto('attributes-search', 'test_attribute_code', {clear: true});
        await this.browser.waitUntilRendered();
        await this.browser.clickInto(['attribute-select-virtual-list', 'test_attribute_code']);
        await this.browser.clickInto('im-user_attributes-table', {
            waitRender: true
        });
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000015));
        await this.browser.clickInto('test_attribute_code_on');
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributeId));
        await this.browser.waitForTestIdSelectorDisabled(['header-panel', 'delete-button']);
    });
});
