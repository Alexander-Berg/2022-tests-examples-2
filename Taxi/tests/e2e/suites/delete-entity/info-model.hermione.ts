import getEntityIdFromUrl from 'tests/e2e/helper/get-entity-id-from-url';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

const INFO_MODEL_ID = 5;

describe('Удаление инфомодели', function () {
    it('Удаление инфомодели, не привязанной к МК', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL);
        await this.browser.typeInto('code', 'test_im');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});
        const infoModelUrl = await this.browser.getUrl();
        const infoModelId = getEntityIdFromUrl(infoModelUrl);
        await this.browser.clickInto(['header-panel', 'delete-button']);
        await this.browser.clickInto('confirmation-modal__ok-button', {waitNavigation: true, waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModelId));
        await this.browser.waitForTestIdSelectorInDom('entity-not-found');
    });

    it('Инфомодель привязана к МК - удалить нельзя', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(INFO_MODEL_ID));
        await this.browser.waitForTestIdSelectorDisabled(['header-panel', 'delete-button']);
        await this.browser.assertImage('header-panel');
    });

    it('Проверка изменения состояния. Можно удалить -> Нельзя и наоборот', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL);
        await this.browser.typeInto('code', 'test_im');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});
        await this.browser.waitForTestIdSelectorEnabled(['header-panel', 'delete-button']);
        await this.browser.assertImage('header-panel');

        const infoModelUrl = await this.browser.getUrl();
        const infoModelId = getEntityIdFromUrl(infoModelUrl);

        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.typeInto('code', 'test_mc');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});
        await this.browser.clickInto('info-model-select');
        await this.browser.clickInto(['info-model-select_dropdown-menu', 'im_node_compatible_test_im']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        const categoryUrl = await this.browser.getUrl();
        const categoryId = getEntityIdFromUrl(categoryUrl);

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModelId));
        await this.browser.assertImage('header-panel');

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(categoryId));
        await this.browser.clickInto('info-model-select');
        await this.browser.clickInto(['info-model-select_dropdown-menu', 'im_node_compatible_root']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModelId));
        await this.browser.assertImage('header-panel');
    });

    it('После удаления можно создать ИМ с тем же кодом', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL);
        await this.browser.typeInto('code', 'test_im');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});
        await this.browser.clickInto(['header-panel', 'delete-button']);
        await this.browser.clickInto('confirmation-modal__ok-button', {waitNavigation: true, waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL);
        await this.browser.typeInto('code', 'test_im');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});
        await this.browser.assertImage('base-layout');
    });
});
