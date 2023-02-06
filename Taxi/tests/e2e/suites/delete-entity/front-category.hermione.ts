import getEntityIdFromUrl from 'tests/e2e/helper/get-entity-id-from-url';
import {frontCategories} from 'tests/e2e/seed-db-map';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Удаление фронт-категории', function () {
    it('Удаление только что созданной неактивной ФК', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.clickInto(['status', 'disabled_label']);
        await this.browser.typeInto('code', 'test_fc');
        await this.browser.typeInto(['translations', 'ru', 'name'], 'Super mega category name');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});
        const categoryUrl = await this.browser.getUrl();
        const categoryId = getEntityIdFromUrl(categoryUrl);

        await this.browser.clickInto(['header-panel', 'delete-button']);
        await this.browser.clickInto('confirmation-modal__ok-button', {waitNavigation: true, waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(categoryId));
        await this.browser.waitForTestIdSelectorInDom('entity-not-found');
    });

    it('Удаление только что созданной неактивной дочерней ФК', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.clickInto('parent-category-modal__input', {waitRender: true});
        await this.browser.clickInto(['parent-category-modal', 'row_front_category_code_1_0']);
        await this.browser.clickInto(['parent-category-modal', 'parent-category-modal__ok-button'], {waitRender: true});
        await this.browser.clickInto(['status', 'disabled_label']);
        await this.browser.typeInto('code', 'test_child');
        await this.browser.typeInto(['translations', 'ru', 'name'], 'Super mega category name');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});
        const categoryUrl = await this.browser.getUrl();
        const categoryId = getEntityIdFromUrl(categoryUrl);

        await this.browser.clickInto(['header-panel', 'delete-button']);
        await this.browser.clickInto('confirmation-modal__ok-button', {waitNavigation: true, waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(categoryId));
        await this.browser.waitForTestIdSelectorInDom('entity-not-found');
    });

    it('Удаление родителя удаляет всех дочек', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.typeInto('code', 'test_parent');
        await this.browser.typeInto(['translations', 'ru', 'name'], 'Super mega category name');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});
        const categoryUrl = await this.browser.getUrl();
        const categoryId = getEntityIdFromUrl(categoryUrl);

        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.clickInto('parent-category-modal__input', {waitRender: true});
        await this.browser.clickInto(['hide-inactive']);
        await this.browser.performScroll(['\\.ant-tree-list-holder']);
        await this.browser.clickInto(['parent-category-modal', 'row_test_parent']);
        await this.browser.clickInto(['parent-category-modal', 'parent-category-modal__ok-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_child');
        await this.browser.typeInto(['translations', 'ru', 'name'], 'Super mega child category name');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        const childCategoryUrl = await this.browser.getUrl();
        const childCategoryId = getEntityIdFromUrl(childCategoryUrl);

        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(categoryId));
        await this.browser.clickInto(['header-panel', 'delete-button']);
        await this.browser.clickInto('confirmation-modal__ok-button', {waitNavigation: true, waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(categoryId));
        await this.browser.waitForTestIdSelectorInDom('entity-not-found');

        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(childCategoryId));
        await this.browser.waitForTestIdSelectorInDom('entity-not-found');
    });

    it('После удаления можно создать ФК с тем же кодом', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.clickInto(['status', 'disabled_label']);
        await this.browser.typeInto('code', 'test_fc');
        await this.browser.typeInto(['translations', 'ru', 'name'], 'Super mega category name');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});
        await this.browser.clickInto(['header-panel', 'delete-button']);
        await this.browser.clickInto('confirmation-modal__ok-button', {waitNavigation: true, waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.clickInto(['status', 'disabled_label']);
        await this.browser.typeInto('code', 'test_fc');
        await this.browser.typeInto(['translations', 'ru', 'name'], 'Super mega category name');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('В ФК есть товары - удалить нельзя', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        await this.browser.assertImage('header-panel');
    });

    it('ФК активна - удалить нельзя', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.typeInto('code', 'test_root');
        await this.browser.typeInto(['translations', 'ru', 'name'], 'Super mega category name');
        await this.browser.clickInto(['status', 'active_label']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});
        await this.browser.assertImage('header-panel');
    });

    it('Активация ФК, которую можно удалить - проверка, что после активации удалить нельзя', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.typeInto('code', 'test_fc');
        await this.browser.typeInto(['translations', 'ru', 'name'], 'Super mega category name');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});
        await this.browser.waitForTestIdSelectorEnabled('delete-button');
        await this.browser.clickInto(['status', 'active_label']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.waitForTestIdSelectorDisabled(['header-panel', 'delete-button']);
    });
});
