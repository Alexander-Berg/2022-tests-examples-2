import {attributeGroups, infoModels} from 'tests/e2e/seed-db-map';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

const ATTRIBUTE_GROUP_ID = attributeGroups.attribute_group_code_1;
const INFO_MODEL_ID = infoModels.ru.info_model_code_1_1;
const PRODUCT_ID = 10000001;

describe('Удаление группы', function () {
    it('Удалить группу через карточку группы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUP(ATTRIBUTE_GROUP_ID));

        await this.browser.clickInto(['header', 'delete-button'], {waitRender: true});

        await this.browser.assertImage('confirmation-modal', {removeShadows: true});

        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button'], {waitNavigation: true});

        await this.browser.clickInto('region-switcher', {waitRender: true});
        await this.browser.clickInto('FR', {waitNavigation: true, waitRender: true});

        await this.browser.assertImage('group-attributes-table');
    });

    it('Удалить группу и проверить атрибуты в товаре', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUP(ATTRIBUTE_GROUP_ID));

        await this.browser.clickInto(['header', 'delete-button'], {waitRender: true});
        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button'], {waitNavigation: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(PRODUCT_ID));

        await this.browser.assertImage('without-group', {removeShadows: true});
    });

    it('Удалить группу и проверить атрибуты в ИМ', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE_GROUP(ATTRIBUTE_GROUP_ID));

        await this.browser.clickInto(['header', 'delete-button'], {waitRender: true});
        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button'], {waitNavigation: true});

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(INFO_MODEL_ID));

        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['infomodel-groups-table', 'im_attribute-group_row_undefined'], {
            waitRender: true
        });
        await this.browser.assertImage(['im-user_attributes-table', 'infomodel-attributes-table', '\\tbody']);
    });
});
