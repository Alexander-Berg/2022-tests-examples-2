import getEntityIdFromUrl from 'tests/e2e/helper/get-entity-id-from-url';
import {masterCategories} from 'tests/e2e/seed-db-map';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Удаление мастер-категории', function () {
    it('Удаление только что созданной неактивной МК', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.clickInto(['status', 'disabled_label']);
        await this.browser.typeInto('code', 'test_mc');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});
        const categoryUrl = await this.browser.getUrl();
        const categoryId = getEntityIdFromUrl(categoryUrl);

        await this.browser.clickInto(['header-panel', 'delete-button']);
        await this.browser.clickInto('confirmation-modal__ok-button', {waitNavigation: true, waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(categoryId));
        await this.browser.waitForTestIdSelectorInDom('entity-not-found');
    });

    it('Удаление только что созданной неактивной дочерней МК', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.clickInto('parent-category-modal__input', {waitRender: true});
        await this.browser.clickInto(['parent-category-modal', 'row_master_category_code_1_0']);
        await this.browser.clickInto(['parent-category-modal', 'parent-category-modal__ok-button'], {waitRender: true});
        await this.browser.clickInto(['status', 'disabled_label']);
        await this.browser.typeInto('code', 'test_child');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});
        const categoryUrl = await this.browser.getUrl();
        const categoryId = getEntityIdFromUrl(categoryUrl);

        await this.browser.clickInto(['header-panel', 'delete-button']);
        await this.browser.clickInto('confirmation-modal__ok-button', {waitNavigation: true, waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(categoryId));
        await this.browser.waitForTestIdSelectorInDom('entity-not-found');
    });

    it('Удаление родителя удаляет всех дочек', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.typeInto('code', 'test_parent');
        await this.browser.clickInto(['status', 'disabled_label']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});
        const categoryUrl = await this.browser.getUrl();
        const categoryId = getEntityIdFromUrl(categoryUrl);

        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.clickInto('parent-category-modal__input', {waitRender: true});
        await this.browser.clickInto(['hide-inactive']);
        await this.browser.clickInto(['parent-category-modal', 'row_test_parent']);
        await this.browser.clickInto(['parent-category-modal', 'parent-category-modal__ok-button'], {waitRender: true});
        await this.browser.clickInto(['status', 'disabled_label']);
        await this.browser.typeInto('code', 'test_child');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        const childCategoryUrl = await this.browser.getUrl();
        const childCategoryId = getEntityIdFromUrl(childCategoryUrl);

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(categoryId));
        await this.browser.clickInto(['header-panel', 'delete-button']);
        await this.browser.clickInto('confirmation-modal__ok-button', {waitNavigation: true, waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(categoryId));
        await this.browser.waitForTestIdSelectorInDom('entity-not-found');

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(childCategoryId));
        await this.browser.waitForTestIdSelectorInDom('entity-not-found');
    });

    it('После удаления можно создать МК с тем же кодом', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.clickInto(['status', 'disabled_label']);
        await this.browser.typeInto('code', 'test_mc');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});
        await this.browser.clickInto(['header-panel', 'delete-button']);
        await this.browser.clickInto('confirmation-modal__ok-button', {waitNavigation: true, waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.clickInto(['status', 'disabled_label']);
        await this.browser.typeInto('code', 'test_mc');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('В МК есть товары - удалить нельзя', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_1_3));
        await this.browser.assertImage('header-panel');
    });

    it('МК активна - удалить нельзя', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.typeInto('code', 'test_mc');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});
        await this.browser.assertImage('header-panel');
    });

    it('Активация МК, которую можно удалить - проверка, что после активации удалить нельзя', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.clickInto(['status', 'disabled_label']);
        await this.browser.typeInto('code', 'test_mc');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});
        await this.browser.waitForTestIdSelectorEnabled('delete-button');
        await this.browser.clickInto(['status', 'active_label']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.waitForTestIdSelectorDisabled('delete-button');
    });
});
