import {categories, grids, groups} from 'tests/e2e/seed-db-map';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Витрина в режиме read only', function () {
    it('Нет кнопки создания сетки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'), {isReadonly: true});
        await this.browser.waitForTestIdSelectorNotInDom(['action-bar', 'create-button']);
        await this.browser.assertImage('action-bar');
    });

    it('Нет кнопки создания прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'), {isReadonly: true});
        await this.browser.waitForTestIdSelectorNotInDom(['action-bar', 'create-button']);
        await this.browser.assertImage('action-bar');
    });

    it('Нет кнопки создания категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'), {isReadonly: true});
        await this.browser.waitForTestIdSelectorNotInDom(['action-bar', 'create-button']);
        await this.browser.assertImage('action-bar');
    });

    it('В таблице сеток через три точки нельзя дублировать, деактивировать и удалить сетку', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('grids'), {isReadonly: true});
        const basePath = ['grid_row_grid_code_1_1', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.waitForTestIdSelectorAriaDisabled([...basePath, 'more-menu', 'duplicate']);
        await this.browser.waitForTestIdSelectorAriaDisabled([...basePath, 'more-menu', 'deactivate']);
        await this.browser.waitForTestIdSelectorAriaDisabled([...basePath, 'more-menu', 'delete']);
    });

    it('В таблице прилавков через три точки нельзя дублировать, деактивировать и удалить прилавок', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'), {isReadonly: true});
        const basePath = ['group_row_group_code_1_1', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.waitForTestIdSelectorAriaDisabled([...basePath, 'more-menu', 'duplicate']);
        await this.browser.waitForTestIdSelectorAriaDisabled([...basePath, 'more-menu', 'deactivate']);
        await this.browser.waitForTestIdSelectorAriaDisabled([...basePath, 'more-menu', 'delete']);
    });

    it('В таблице категорий через три точки нельзя дублировать, деактивировать и удалить категорию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'), {isReadonly: true});
        const basePath = ['category_row_category_code_1_1', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.waitForTestIdSelectorAriaDisabled([...basePath, 'more-menu', 'duplicate']);
        await this.browser.waitForTestIdSelectorAriaDisabled([...basePath, 'more-menu', 'deactivate']);
        await this.browser.waitForTestIdSelectorAriaDisabled([...basePath, 'more-menu', 'delete']);
    });

    it('На странице категории нельзя добавить подкатегории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1), {isReadonly: true});
        await this.browser.waitForTestIdSelectorNotVisible('add-front-category-button');
    });

    it('На странице категории нельзя поменять все свойства категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1), {isReadonly: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('На странице категории нельзя удалить подкатегорию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_3), {
            isReadonly: true,
            patchStyles: {showOptions: true}
        });
        await this.browser.waitForTestIdSelectorDisabled([
            'catalog-layout_roll',
            'front-category_front_category_code_5_3',
            'delete'
        ]);
    });

    it('На странице категории нельзя поменять порядок подкатегорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_3), {isReadonly: true});
        await this.browser.dragAndDrop(
            'front-category_front_category_code_5_3',
            'front-category_front_category_code_5_4',
            {
                offset: 'bottom'
            }
        );
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('catalog-layout_roll');
    });

    it('На странице прилавка нельзя добавить категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1), {isReadonly: true});
        await this.browser.waitForTestIdSelectorNotVisible('add-category-button');
    });

    it('На странице прилавка нельзя удалить категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1), {
            isReadonly: true,
            patchStyles: {showOptions: true}
        });
        const basePath = ['category_category_code_1_2', 'more'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.waitForTestIdSelectorAriaDisabled([...basePath, 'menu', 'delete']);
    });

    it('На странице прилавка нельзя поменять порядок категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1), {isReadonly: true});
        await this.browser.dragAndDrop('category_category_code_1_2', 'category_category_code_1_16', {
            offset: 'right'
        });
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('catalog-layout_roll');
    });

    it('На странице прилавка нельзя поменять изображение и его формат для категории на прилавке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1), {
            isReadonly: true,
            patchStyles: {showOptions: true}
        });
        const basePath = ['category_category_code_1_2', 'link-images'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.assertImage('edit-modal', {removeShadows: true});
    });

    it('На странице прилавка нельзя поменять мету для связи категории с прилавком', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1), {
            isReadonly: true,
            patchStyles: {showOptions: true}
        });
        const basePath = ['category_category_code_1_2', 'link-meta'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.assertImage('edit-modal', {removeShadows: true});
    });

    it('На странице прилавка нельзя поменять все свойства прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1), {isReadonly: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('На странице прилавка нельзя поменять свойства категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1), {isReadonly: true});
        await this.browser.clickInto('category_category_code_1_2', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('На странице прилавка нельзя изменить состав и порядок подкатегорий в категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1), {
            isReadonly: true,
            patchStyles: {showOptions: true}
        });
        await this.browser.clickInto('category_category_code_1_2', {waitRender: true});

        await this.browser.waitForTestIdSelectorNotVisible('add-front-category-button');
        await this.browser.waitForTestIdSelectorDisabled([
            'catalog-layout_roll',
            'front-category_front_category_code_5_1',
            'delete'
        ]);
        await this.browser.dragAndDrop(
            'front-category_front_category_code_5_1',
            'front-category_front_category_code_5_2',
            {
                offset: 'bottom'
            }
        );
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('catalog-layout_roll');
    });

    it('На странице сетки нельзя поменять все свойства сетки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {isReadonly: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('На странице сетки нельзя добавить прилавок', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {isReadonly: true});
        await this.browser.waitForTestIdSelectorNotVisible('add-group-button');
    });

    it('На странице сетки нельзя удалить прилавок', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            isReadonly: true,
            patchStyles: {showOptions: true}
        });
        await this.browser.clickInto(['group_group_code_1_2', 'more'], {waitRender: true});
        await this.browser.waitForTestIdSelectorAriaDisabled(['group_group_code_1_2', 'menu', 'delete']);
    });

    it('На странице сетки нельзя поменять порядок прилавков', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            isReadonly: true,
            patchStyles: {showOptions: true}
        });
        await this.browser.waitForTestIdSelectorDisabled(['group_group_code_1_2', 'down']);
    });

    it('На странице сетки нельзя поменять изображение прилавка на сетке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            isReadonly: true,
            patchStyles: {showOptions: true}
        });
        const basePath = ['group_group_code_1_2', 'link-image'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.assertImage([...basePath, 'menu'], {removeShadows: true});
    });

    it('На странице сетки нельзя поменять мету связи прилавка с сеткой', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            isReadonly: true,
            patchStyles: {showOptions: true}
        });
        const basePath = ['group_group_code_1_2', 'link-meta'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.assertImage('edit-modal', {removeShadows: true});
    });

    it('На странице сетки нельзя поменять свойства прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {isReadonly: true});
        await this.browser.clickInto('group_group_code_1_2', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('На странице сетки нельзя изменить набор категорий у прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            isReadonly: true,
            patchStyles: {showOptions: true}
        });
        await this.browser.clickInto('group_group_code_1_2', {waitRender: true});

        await this.browser.waitForTestIdSelectorNotVisible('add-category-button');
        const basePath = ['category_category_code_1_3', 'more'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.waitForTestIdSelectorAriaDisabled([...basePath, 'menu', 'delete']);
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.dragAndDrop('category_category_code_1_3', 'category_category_code_1_18', {
            offset: 'right'
        });
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('catalog-layout_roll');
    });

    it('На странице сетки нельзя поменять изображение и мету связи категории с прилавком', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            isReadonly: true,
            patchStyles: {showOptions: true}
        });
        await this.browser.clickInto('group_group_code_1_2', {waitRender: true});

        const basePath = ['category_category_code_1_3', 'link-images'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.assertImage('edit-modal', {removeShadows: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__cancel_button'], {waitRender: true});

        await this.browser.clickInto(['category_category_code_1_3', 'link-meta'], {waitRender: true});
        await this.browser.assertImage('edit-modal', {removeShadows: true});
    });

    it('На странице сетки нельзя поменять свойства категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {isReadonly: true});
        await this.browser.clickInto('group_group_code_1_2', {waitRender: true});
        await this.browser.clickInto('category_category_code_1_3', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('На странице сетки нельзя поменять набор подкатегорий у категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {isReadonly: true});
        await this.browser.clickInto('group_group_code_1_2', {waitRender: true});
        await this.browser.clickInto('category_category_code_1_3', {waitRender: true});

        await this.browser.waitForTestIdSelectorNotVisible('add-front-category-button');
        await this.browser.waitForTestIdSelectorDisabled([
            'catalog-layout_roll',
            'front-category_front_category_code_5_3',
            'delete'
        ]);
        await this.browser.dragAndDrop(
            'front-category_front_category_code_5_3',
            'front-category_front_category_code_5_4',
            {
                offset: 'bottom'
            }
        );
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('catalog-layout_roll');
    });
});
