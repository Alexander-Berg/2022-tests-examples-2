import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

const MULTISELECT_ATTRIBUTE_ID = 10;

describe('Удаление опции атрибута', function () {
    it('Опция используется в товаре - удалить нельзя', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(MULTISELECT_ATTRIBUTE_ID));
        await this.browser.assertImage('select-option-header-attribute_option_code_10_1');
    });

    it('Опция не используется в товарах - удаляем', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(MULTISELECT_ATTRIBUTE_ID));
        await this.browser.clickInto('select-option-delete-attribute_option_code_10_2', {waitRender: true});
        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button'], {waitRender: true});
        await this.browser.assertImage('select-option');
    });

    it('После удаления можно добавить опцию с тем же кодом', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(MULTISELECT_ATTRIBUTE_ID));
        await this.browser.clickInto('select-option-delete-attribute_option_code_10_2', {waitRender: true});
        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button'], {waitRender: true});
        await this.browser.clickInto('select-option-add');
        await this.browser.typeInto(['select-option-header', 'select-option-code'], 'attribute_option_code_10_2');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('select-option');
    });
});
