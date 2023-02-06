import {categories, frontCategories, grids, groups} from 'tests/e2e/seed-db-map';
import createImageFile from 'tests/e2e/utils/create-image-file';
import getFixturePath from 'tests/e2e/utils/fixture';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Редактирование сетки в витрине', function () {
    it('Общий вид пустой сетки, поле "Код" недоступно для редактирования', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_4));
        await this.browser.waitForTestIdSelectorDisabled('code');
        await this.browser.assertImage('base-layout');
    });

    it('Отмена выбора категории для прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_4));
        await this.browser.clickInto('add-group-button', {waitRender: true});
        await this.browser.clickInto(['add-modal', 'entity_group_code_1_7']);
        await this.browser.assertImage('add-modal', {removeShadows: true});

        await this.browser.clickInto(['add-modal', 'add-modal__cancel_button'], {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Поиск по названию прилавка в модале добавления прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_4));
        await this.browser.clickInto('add-group-button', {waitRender: true});
        await this.browser.typeInto(['action-bar', 'search'], 'прост', {clear: true});
        await this.browser.waitUntilRendered({minStableIterations: 10});
        await this.browser.assertImage('add-modal', {removeShadows: true});
    });

    it('Ховер на прилавок в модале добавления прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_4));
        await this.browser.clickInto('add-group-button', {waitRender: true});
        const group = await this.browser.findByTestId('entity_group_code_1_3');
        await group.moveTo();
        await this.browser.assertImage('add-modal', {removeShadows: true});
    });

    it('Выбрать несколько прилавков в модале добавления прилавков и добавить', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_4));
        await this.browser.clickInto('add-group-button', {waitRender: true});
        await this.browser.clickInto(['add-modal', 'entity_group_code_1_2']);
        await this.browser.clickInto(['add-modal', 'entity_group_code_1_3']);
        await this.browser.clickInto(['add-modal', 'add-modal__ok_button'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Нельзя добавить уже добавленный прилавок', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1));
        await this.browser.clickInto('add-group-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorAriaDisabled(['add-modal', 'entity_group_code_1_2']);
        await this.browser.waitForTestIdSelectorDisabled(['add-modal', 'add-modal__ok_button']);
        await this.browser.assertImage('add-modal', {removeShadows: true});
    });

    it('Изменить описание сетки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_4));
        await this.browser.typeInto('description', 'test-description', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Смена языка интерфейса на странице сетки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1));
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('ui-lang-select', {waitRender: true});
        await this.browser.clickInto(['ui-lang-select_dropdown-menu', 'en'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Поиск прилавка сетки по названию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1));
        await this.browser.typeInto('search_input', 'нико', {clear: true});
        await this.browser.assertImage('grid-tree');
    });

    it('Поиск категории прилавка сетки по названию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1));
        await this.browser.typeInto('search_input', 'потом', {clear: true});
        await this.browser.assertImage('grid-tree');
    });

    it('Развернуть дерево прилавков и категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1));
        await this.browser.clickInto(['row_group_code_1_2', '\\.ant-tree-switcher'], {waitRender: true});
        await this.browser.clickInto(['row_category_code_1_3', '\\.ant-tree-switcher'], {waitRender: true});
        await this.browser.assertImage('grid-tree');
    });

    it('Клик в прилавок подсвечивает его название голубым и открывает его просмотр в сетке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1));
        await this.browser.clickInto('row_group_code_1_2', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    // eslint-disable-next-line max-len
    it('Клик в категорию подсвечивает ее название голубым, открывает в сетке ее карточку и список всех категорий прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1));
        await this.browser.clickInto(['row_group_code_1_2', '\\.ant-tree-switcher'], {waitRender: true});
        await this.browser.clickInto('row_category_code_1_3', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Клик в "назад" из просмотра прилавка возвращает к просмотру сетки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2}
        });
        await this.browser.assertImage('base-layout');

        await this.browser.clickInto(['catalog-layout_roll', 'back'], {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.assertImage('base-layout');
    });

    it('Клик в "назад" из просмотра категории возвращает к просмотру прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2, category: categories.ru.category_code_1_3}
        });
        await this.browser.assertImage('base-layout');
        await this.browser.clickInto(['catalog-layout_roll', 'back'], {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.assertImage('base-layout');
    });

    it('Добавить новый прилавок в начало', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1));
        await this.browser.clickInto('add-group-button', {waitRender: true});
        await this.browser.clickInto(['add-modal', 'entity_group_code_1_3']);
        await this.browser.clickInto(['add-modal', 'add-modal__ok_button'], {waitRender: true});
        await this.browser.assertImage('catalog-layout_roll');
    });

    it('Добавить новый прилавок в середину', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1));
        await this.browser.clickInto('\\[data-testid=add-group-button]:nth-child(2n) ', {waitRender: true});
        await this.browser.clickInto(['add-modal', 'entity_group_code_1_3']);
        await this.browser.clickInto(['add-modal', 'add-modal__ok_button'], {waitRender: true});
        await this.browser.assertImage('catalog-layout_roll');
    });

    it('Сдвинуть прилавок вниз в списке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            patchStyles: {showOptions: true}
        });
        await this.browser.clickInto(['group_group_code_1_2', 'down'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Добавить валидное значение мета прилавку', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1));
        const group = await this.browser.findByTestId('group_group_code_1_2');
        await group.moveTo();
        await this.browser.clickInto(['group_group_code_1_2', 'link-meta'], {waitRender: true});
        await this.browser.typeInto(['edit-modal', 'meta'], '{"number": 123, "string": "abc"}', {clear: true});
        await this.browser.assertImage('edit-modal', {removeShadows: true});

        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await group.moveTo();
        await this.browser.assertImage('catalog-layout_roll');
    });

    it('Ввод невалидного значения мета', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1));
        const group = await this.browser.findByTestId('group_group_code_1_2');
        await group.moveTo();
        await this.browser.clickInto(['group_group_code_1_2', 'link-meta'], {waitRender: true});
        await this.browser.typeInto(['edit-modal', 'meta'], '{"number": 123]]]', {clear: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.assertImage('edit-modal', {removeShadows: true});
    });

    it('Клик в "Отмена" закрывает окно изменения мета информации', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1));
        const group = await this.browser.findByTestId('group_group_code_1_2');
        await group.moveTo();
        await this.browser.clickInto(['group_group_code_1_2', 'link-meta'], {waitRender: true});
        await this.browser.typeInto(['edit-modal', 'meta'], '{"number": 123, "string": "abc"}', {clear: true});
        await this.browser.assertImage('edit-modal', {removeShadows: true});

        await this.browser.clickInto(['edit-modal', 'edit-modal__cancel_button'], {waitRender: true});
        await group.moveTo();
        await this.browser.assertImage('catalog-layout_roll');
    });

    it('Изменить изображение прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1));
        const group = await this.browser.findByTestId('group_group_code_1_2');
        await group.moveTo();
        const basePath = ['group_group_code_1_2', 'link-image'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.assertImage([...basePath, 'menu'], {removeShadows: true});

        await this.browser.clickInto([...basePath, 'menu', 'image_img_1_2_3.png'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Открыть прилавок через контекстное меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1));
        const group = await this.browser.findByTestId('group_group_code_1_2');
        await group.moveTo();
        const basePath = ['group_group_code_1_2', 'more'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'open'], {
            waitNavigation: true,
            waitRender: true
        });
        expect(await this.browser.getUrl()).to.match(
            new RegExp(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1) + `\\?group=${groups.ru.group_code_1_2}`)
        );
    });

    it('Удалить прилавок из сетки через контекстное меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1));
        const group = await this.browser.findByTestId('group_group_code_1_2');
        await group.moveTo();
        const basePath = ['group_group_code_1_2', 'more'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'delete'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Открытие затененного прилавка по клику', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1));
        await this.browser.clickInto('group_group_code_1_16', {waitRender: true});
        await this.browser.assertImage('catalog-layout_roll');

        await this.browser.clickInto('group_group_code_1_2', {waitRender: true});
        await this.browser.assertImage('catalog-layout_roll');
    });

    it('Добавить категорию для прилавка во всех сетках', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_5), {
            queryParams: {group: groups.ru.group_code_1_19}
        });
        await this.browser.clickInto('add-category-button', {waitRender: true});
        await this.browser.clickInto(['add-modal', 'entity_category_code_1_3']);
        await this.browser.clickInto(['add-modal', 'add-modal__ok_button'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.clickInto(['row_group_code_1_19', '\\.ant-tree-switcher'], {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Клик в категорию открывает ее для просмотра в нашей сетке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2}
        });
        await this.browser.clickInto('category_category_code_1_3', {
            waitNavigation: true,
            waitRender: true
        });
        expect(await this.browser.getUrl()).to.match(
            new RegExp(
                ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1) +
                    `\\?group=${groups.ru.group_code_1_2}` +
                    `&category=${categories.ru.category_code_1_3}`
            )
        );
    });

    it('Открыть категорию через контекстное меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2}
        });
        const category = await this.browser.findByTestId('category_category_code_1_3');
        await category.moveTo();
        await this.browser.clickInto(['category_category_code_1_3', 'more'], {waitRender: true});
        await this.browser.clickInto(['category_category_code_1_3', 'more', 'open'], {
            waitNavigation: true,
            waitRender: true
        });
        expect(await this.browser.getUrl()).to.match(
            new RegExp(
                ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1) +
                    `\\?group=${groups.ru.group_code_1_2}` +
                    `&category=${categories.ru.category_code_1_3}`
            )
        );
    });

    it('Удалить категорию из прилавка через контекстное меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2}
        });
        const category = await this.browser.findByTestId('category_category_code_1_3');
        await category.moveTo();
        await this.browser.clickInto(['category_category_code_1_3', 'more'], {waitRender: true});
        await this.browser.clickInto(['category_category_code_1_3', 'more', 'delete'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto(['row_group_code_1_2', '\\.ant-tree-switcher'], {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Поменять местами категории в прилавке перетаскиванием', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2}
        });
        await this.browser.dragAndDrop('category_category_code_1_3', 'category_category_code_1_18', {
            offset: 'right'
        });
        await this.browser.waitUntilRendered();
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto(['row_group_code_1_2', '\\.ant-tree-switcher'], {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Добавить валидное мета категории в прилавке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2}
        });
        const category = await this.browser.findByTestId('category_category_code_1_18');
        await category.moveTo();
        await this.browser.clickInto(['category_category_code_1_18', 'link-meta'], {waitRender: true});
        await this.browser.typeInto(['edit-modal', 'meta'], '{"number": 123, "string": "abc"}', {clear: true});
        await this.browser.assertImage('edit-modal', {removeShadows: true});

        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await category.moveTo();
        await this.browser.assertImage('group_group_code_1_2');
    });

    it('Добавить невалидное мета категории в прилавке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2}
        });
        const category = await this.browser.findByTestId('category_category_code_1_18');
        await category.moveTo();
        await this.browser.clickInto(['category_category_code_1_18', 'link-meta'], {waitRender: true});
        await this.browser.typeInto(['edit-modal', 'meta'], '{"number": 123]]]', {clear: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.assertImage('edit-modal', {removeShadows: true});
    });

    it('Добавить изображение и формат категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2}
        });
        const category = await this.browser.findByTestId('category_category_code_1_18');
        await category.moveTo();
        await this.browser.clickInto(['category_category_code_1_18', 'link-images'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'add-image'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'add-image', 'menu', 'image-img_1_18_2.png'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'image-with-formats_img_1_18_2.png', 'image-format-3'], {
            waitRender: true
        });
        await this.browser.clickInto(['edit-modal', 'image-with-formats_img_1_18_1.png', 'image-format-4'], {
            waitRender: true
        });
        await this.browser.assertImage('edit-modal', {removeShadows: true});

        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('group_group_code_1_2');
    });

    it('Нельзя добавить изображение без формата', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2}
        });
        const category = await this.browser.findByTestId('category_category_code_1_18');
        await category.moveTo();
        await this.browser.clickInto(['category_category_code_1_18', 'link-images'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'image-with-formats_img_1_18_1.png', 'image-format-2'], {
            waitRender: true
        });
        await this.browser.waitForTestIdSelectorDisabled(['edit-modal', 'edit-modal__ok_button']);
        await this.browser.assertImage('edit-modal', {removeShadows: true});
    });

    // eslint-disable-next-line max-len
    it('Клик в прилавок в средней колонке открывает его информацию в правой колонке с полем "Код" недоступным для редактирования', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1));
        await this.browser.clickInto('group_group_code_1_16', {waitRender: true});
        await this.browser.waitForTestIdSelectorDisabled('code');
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Изменить статус прилавка в одной сетке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_16}
        });
        await this.browser.clickInto(['status', 'disabled']);
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'update-all']);
        await this.browser.clickInto(['edit-modal', 'select-item_grid_code_1_1', 'checkbox'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'select-item_grid_code_1_30', 'checkbox'], {waitRender: true});
        await this.browser.assertImage('edit-modal', {removeShadows: true});

        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');

        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_16}
        });
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Изменить длинное и короткое название для всех сеток', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_16}
        });
        await this.browser.typeInto('short-title-ru', 'test-short-title', {clear: true});
        await this.browser.typeInto('long-title-ru', 'test-long-title', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('При создании копии после изменений код проверяется на уникальность', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_16},
            patchStyles: {enableNotifications: true}
        });
        await this.browser.clickInto(['status', 'disabled']);
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'update-all']);
        await this.browser.clickInto(['edit-modal', 'select-item_grid_code_1_1', 'checkbox'], {waitRender: true});
        await this.browser.typeInto(['edit-modal', 'code'], 'group_code_1_16', {clear: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('notification');
        await this.browser.assertImage('notification', {removeShadows: true});
    });

    it('Ввод невалидного кода при сохранении изменений прилавка в одной сетке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_16}
        });
        await this.browser.clickInto(['status', 'disabled']);
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'update-all']);
        await this.browser.clickInto(['edit-modal', 'select-item_grid_code_1_1', 'checkbox'], {waitRender: true});
        await this.browser.typeInto(['edit-modal', 'code'], 'invalid::code', {clear: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.assertImage('edit-modal', {removeShadows: true});
    });

    it('Добавить изображение прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2}
        });
        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('abc.png'));
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');

        await this.browser.clickInto(['catalog-layout_roll', 'back'], {
            waitNavigation: true,
            waitRender: true
        });
        const group = await this.browser.findByTestId('group_group_code_1_2');
        await group.moveTo();
        const basePath = ['group_group_code_1_2', 'link-image'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'menu', 'image_abc.png'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('grid-tree');
    });

    it('Изменить описание прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2}
        });
        await this.browser.typeInto('description', 'test-description', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');

        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        await this.browser.assertImage('group_row_group_code_1_2');
    });

    it('Изменить мета прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2}
        });
        await this.browser.performScroll('catalog-layout_info');
        await this.browser.typeInto('meta', '{"number": 123, "string": "abc"}', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');

        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_2));
        await this.browser.performScroll('catalog-layout_info');
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Нельзя изменить фото прилавка, если оно используется на сетке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2}
        });
        const basePath = ['image_img_1_2_1.png', 'delete'];
        await this.browser.waitForTestIdSelectorAriaDisabled(basePath);
        const deleteButton = await this.browser.findByTestId(basePath);
        await deleteButton.moveTo();
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('catalog-layout_info');

        await this.browser.clickInto(['image-reference-tooltip', `link_${grids.ru.grid_code_1_1}`], {
            waitNavigation: true,
            waitRender: true
        });
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1)));
    });

    it('Добавить подкатегорию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2, category: categories.ru.category_code_1_18}
        });
        await this.browser.clickInto('add-front-category-button', {waitRender: true});
        await this.browser.clickInto(['row_front_category_code_1_0', '\\.ant-tree-switcher'], {waitRender: true});
        await this.browser.clickInto('row_front_category_code_5_0', {waitRender: true});
        await this.browser.clickInto('row_front_category_code_5_1', {waitRender: true});
        await this.browser.clickInto(['add-modal', 'add-modal__ok_button'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto(['row_category_code_1_18', '\\.ant-tree-switcher'], {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Удалить подкатегорию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2, category: categories.ru.category_code_1_18}
        });
        const frontCategory = await this.browser.findByTestId('front-category_front_category_code_10_0');
        await frontCategory.moveTo();
        await this.browser.clickInto(['front-category_front_category_code_10_0', 'delete'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto(['row_category_code_1_18', '\\.ant-tree-switcher'], {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Клик в три точки открывает контекстное меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2, category: categories.ru.category_code_1_18}
        });
        const frontCategory = await this.browser.findByTestId('front-category_front_category_code_10_0');
        await frontCategory.moveTo();
        const basePath = ['front-category_front_category_code_10_0', 'more'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.assertImage([...basePath, 'menu'], {removeShadows: true});
    });

    it('Открыть родительскую категорию кликом на нее', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2, category: categories.ru.category_code_1_18}
        });
        await this.browser.clickInto(['front-category_front_category_code_10_0', 'expand'], {waitRender: true});
        await this.browser.clickInto(['front-category_front_category_code_10_0', 'parent-category-link'], {
            waitNavigation: true,
            waitRender: true
        });
        expect(await this.browser.getUrl()).to.match(
            new RegExp(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_5))
        );
    });

    it('Открыть саму категорию через контекстное меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2, category: categories.ru.category_code_1_18}
        });
        const frontCategory = await this.browser.findByTestId('front-category_front_category_code_10_0');
        await frontCategory.moveTo();
        const basePath = ['front-category_front_category_code_10_0', 'more'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'menu', 'open-category'], {
            waitNavigation: true,
            waitRender: true
        });
        expect(await this.browser.getUrl()).to.match(
            new RegExp(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_10_0))
        );
    });

    it('Открыть список товаров категории через контекстное меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2, category: categories.ru.category_code_1_18}
        });
        const frontCategory = await this.browser.findByTestId('front-category_front_category_code_10_0');
        await frontCategory.moveTo();
        const basePath = ['front-category_front_category_code_10_0', 'more'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'menu', 'open-products'], {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.assertImage('filter-list');
    });

    it('Изменить статус категории в одном прилавке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2, category: categories.ru.category_code_1_18}
        });
        await this.browser.clickInto(['status', 'disabled']);
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Изменить длинное и короткое название категории во всех прилавках, Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.fr.grid_code_3_1), {
            queryParams: {group: groups.fr.group_code_3_2, category: categories.fr.category_code_3_3},
            region: 'fr'
        });
        await this.browser.clickInto(['translations', 'en']);
        await this.browser.typeInto('short-title-en', 'test-short-title', {clear: true});
        await this.browser.typeInto('long-title-en', 'test-long-title', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('edit-modal', {removeShadows: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Изменить deeplink для всех прилавков', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2, category: categories.ru.category_code_1_3}
        });
        await this.browser.typeInto('deeplink', 'test-deep-link-abc', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Добавить изображение категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2, category: categories.ru.category_code_1_18}
        });
        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('abc.png'));
        await this.browser.waitForTestIdSelectorInDom('image-with-formats_abc.png');
        await this.browser.clickInto(['image-with-formats_abc.png', 'image-format-4']);
        await this.browser.clickInto(['image-with-formats_abc.png', 'image-format-6']);
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');

        await this.browser.clickInto(['catalog-layout_roll', 'back'], {
            waitNavigation: true,
            waitRender: true
        });
        const category = await this.browser.findByTestId('category_category_code_1_18');
        await category.moveTo();
        await this.browser.clickInto(['category_category_code_1_18', 'link-images'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'image-with-formats_img_1_18_1.png', 'delete'], {
            waitRender: true
        });
        await this.browser.clickInto(['edit-modal', 'add-image'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'add-image', 'menu', 'image-abc.png'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'image-with-formats_abc.png', 'image-format-2'], {
            waitRender: true
        });
        await this.browser.clickInto(['edit-modal', 'image-with-formats_abc.png', 'image-format-4'], {
            waitRender: true
        });
        await this.browser.clickInto(['edit-modal', 'image-with-formats_abc.png', 'image-format-6'], {
            waitRender: true
        });
        await this.browser.assertImage('edit-modal', {removeShadows: true});

        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto(['row_group_code_1_2', '\\.ant-tree-switcher'], {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Нельзя выбрать изображение без формата', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2, category: categories.ru.category_code_1_18}
        });
        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('abc.png'));
        await this.browser.waitForTestIdSelectorInDom('image-with-formats_abc.png');
        await this.browser.clickInto(['image-with-formats_abc.png', 'image-format-2']);
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Нельзя загрузить файл другого расширения', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2, category: categories.ru.category_code_1_18}
        });
        await this.browser.uploadFileInto(['images-upload', 'file-input'], getFixturePath('sample.gif'));
        await this.browser.assertImage('images-upload');
        await this.browser.assertImage('header-panel');
    });

    it('Изменить описание и мета категории в одном прилавке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2, category: categories.ru.category_code_1_18}
        });
        await this.browser.performScroll('catalog-layout_info');
        await this.browser.typeInto('description', 'test-description', {clear: true});
        await this.browser.typeInto('meta', '{"number": 123, "string": "abc"}', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Ввод невалидного мета категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2, category: categories.ru.category_code_1_18}
        });
        await this.browser.performScroll('catalog-layout_info');
        await this.browser.typeInto('meta', '{"number": 123]]]', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Перейти в таб про привязанные прилавки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_21));
        await this.browser.clickInto(['status', 'disabled'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_17), {
            queryParams: {group: groups.ru.group_code_1_23, category: categories.ru.category_code_1_12}
        });
        await this.browser.clickInto('\\[id$="used-in-tab"]', {waitRender: true});
        await this.browser.assertImage('entity-links');
    });

    it('Клик в привязанный прилавок открывает этот прилавок', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2, category: categories.ru.category_code_1_3}
        });
        await this.browser.clickInto('\\[id$="used-in-tab"]', {waitRender: true});
        await this.browser.clickInto('entity-link_group_code_1_3', {waitNavigation: true, waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Клик в привязанную сетку открывает эту сетку', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2, category: categories.ru.category_code_1_3}
        });
        await this.browser.clickInto('\\[id$="used-in-tab"]', {waitRender: true});
        await this.browser.clickInto('entity-link_grid_code_1_2', {waitNavigation: true, waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Нельзя удалить фото категории, которое выбрано у категории на прилавке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2, category: categories.ru.category_code_1_3}
        });
        const basePath = ['image-with-formats_img_1_3_1.png', 'delete'];
        await this.browser.waitForTestIdSelectorAriaDisabled(basePath);
        const deleteButton = await this.browser.findByTestId(basePath);
        await deleteButton.moveTo();
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('catalog-layout_info');
        await this.browser.clickInto(['image-reference-tooltip', `link_${groups.ru.group_code_1_2}`], {
            waitNavigation: true,
            waitRender: true
        });
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_2)));
    });

    it('Нельзя удалить формат фото категории, который выбран у категории на прилавке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_1), {
            queryParams: {group: groups.ru.group_code_1_2, category: categories.ru.category_code_1_3}
        });
        const basePath = ['image-with-formats_img_1_3_1.png', 'image-format-2'];
        await this.browser.waitForTestIdSelectorAriaDisabled(basePath);
        const deleteButton = await this.browser.findByTestId(basePath);
        await deleteButton.moveTo();
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('catalog-layout_info');
    });
});
