import {categories, grids, groups} from 'tests/e2e/seed-db-map';
import createImageFile from 'tests/e2e/utils/create-image-file';
import getFixturePath from 'tests/e2e/utils/fixture';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Редактирование прилавка в витрине', function () {
    it('Общий вид прилавка без категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_8));
        await this.browser.waitForTestIdSelectorDisabled('code');
        await this.browser.assertImage('base-layout');
    });

    it('Общий вид прилавка с несколькими категориями. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.il.group_code_4_10), {region: 'il'});
        await this.browser.waitForTestIdSelectorDisabled('code');
        await this.browser.assertImage('base-layout');
    });

    it('Клик по категории в дереве категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        await this.browser.clickInto(['group-tree', 'row_category_code_1_2'], {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Общий вид модалки для выбора категорий для прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        await this.browser.clickInto('add-category-button', {waitRender: true});
        await this.browser.clickInto(['action-bar', 'hide-inactive'], {waitRender: true});
        await this.browser.typeInto(['action-bar', 'search'], '1_1', {clear: true});
        await this.browser.waitUntilRendered({minStableIterations: 10});
        await this.browser.assertImage('add-modal', {removeShadows: true});
    });

    it('Нельзя добавить уже добавленную на прилавок категорию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        await this.browser.clickInto('add-category-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorAriaDisabled(['add-modal', 'entity_category_code_1_2']);
        await this.browser.waitForTestIdSelectorDisabled(['add-modal', 'add-modal__ok_button']);
        await this.browser.assertImage('add-modal', {removeShadows: true});
    });

    it('Поиск в модалке выбора категории для прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        await this.browser.clickInto('add-category-button', {waitRender: true});
        await this.browser.typeInto(['action-bar', 'search'], '1_24', {clear: true});
        await this.browser.clickInto(['add-modal', 'entity_category_code_1_24']);
        await this.browser.clickInto(['add-modal', 'add-modal__ok_button'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Поиск среди неактивных категорий для прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        await this.browser.clickInto('add-category-button', {waitRender: true});
        await this.browser.clickInto(['action-bar', 'hide-inactive'], {waitRender: true});
        await this.browser.typeInto(['action-bar', 'search'], '0', {clear: true});
        await this.browser.clickInto(['add-modal', 'entity_category_code_1_10']);
        await this.browser.clickInto(['add-modal', 'entity_category_code_1_30']);
        await this.browser.clickInto(['add-modal', 'add-modal__ok_button'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Скролл с подгрузкой в модалке выбора категорий для прилавка. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.il.group_code_4_1), {region: 'il'});
        await this.browser.clickInto('add-category-button', {waitRender: true});
        await this.browser.performScroll(['add-modal', 'categories-container']);
        await this.browser.assertImage('add-modal', {removeShadows: true});
    });

    it('Отмена выбора категории для прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        await this.browser.clickInto('add-category-button', {waitRender: true});
        await this.browser.clickInto(['add-modal', 'entity_category_code_1_3']);
        await this.browser.assertImage('add-modal', {removeShadows: true});

        await this.browser.clickInto(['add-modal', 'add-modal__cancel_button'], {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Выбор картинки категории для прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        const category = await this.browser.findByTestId('category_category_code_1_16');
        await category.moveTo();
        await this.browser.assertImage('group_group_code_1_1');

        await this.browser.clickInto(['category_category_code_1_16', 'link-images'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'add-image'], {waitRender: true});
        await this.browser.assertImage(['edit-modal', 'add-image', 'menu'], {removeShadows: true});

        await this.browser.clickInto(['edit-modal', 'add-image', 'menu', 'image-img_1_16_2.png'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'image-with-formats_img_1_16_2.png', 'image-format-3'], {
            waitRender: true
        });
        await this.browser.assertImage('edit-modal', {removeShadows: true});

        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Отмена модалки выбора картинки категории для прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        const category = await this.browser.findByTestId('category_category_code_1_16');
        await category.moveTo();
        await this.browser.clickInto(['category_category_code_1_16', 'link-images'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'add-image'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'add-image', 'menu', 'image-img_1_16_2.png'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'image-with-formats_img_1_16_2.png', 'image-format-3'], {
            waitRender: true
        });
        await this.browser.clickInto(['edit-modal', 'image-with-formats_img_1_16_1.png', 'delete'], {
            waitRender: true
        });
        await this.browser.clickInto(['edit-modal', 'edit-modal__cancel_button'], {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('У двух картинок одной категории нельзя выбрать одинаковый формат', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        const category = await this.browser.findByTestId('category_category_code_1_16');
        await category.moveTo();
        await this.browser.clickInto(['category_category_code_1_16', 'link-images'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'add-image'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'add-image', 'menu', 'image-img_1_16_2.png'], {waitRender: true});
        await this.browser.waitForTestIdSelectorAriaDisabled([
            'edit-modal',
            'image-with-formats_img_1_16_2.png',
            'image-format-2'
        ]);
        await this.browser.assertImage('edit-modal', {removeShadows: true});
    });

    it('Замена картинки категории в прилавке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        const category = await this.browser.findByTestId('category_category_code_1_16');
        await category.moveTo();
        await this.browser.clickInto(['category_category_code_1_16', 'link-images'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'image-with-formats_img_1_16_1.png', 'delete'], {
            waitRender: true
        });
        await this.browser.clickInto(['edit-modal', 'add-image'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'add-image', 'menu', 'image-img_1_16_2.png'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'image-with-formats_img_1_16_2.png', 'image-format-3'], {
            waitRender: true
        });
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Отмена модалки изменения мета связи категории с прилавком', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        const category = await this.browser.findByTestId('category_category_code_1_16');
        await category.moveTo();
        await this.browser.clickInto(['category_category_code_1_16', 'link-meta'], {waitRender: true});
        await this.browser.typeInto(['edit-modal', 'meta'], '{"number": 123, "string": "abc"}', {clear: true});
        await this.browser.assertImage('edit-modal', {removeShadows: true});

        await this.browser.clickInto(['edit-modal', 'edit-modal__cancel_button'], {waitRender: true});
        await category.moveTo();
        await this.browser.assertImage('group_group_code_1_1');
    });

    it('Добавление валидной меты связи категории с прилавком', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        const category = await this.browser.findByTestId('category_category_code_1_16');
        await category.moveTo();
        await this.browser.clickInto(['category_category_code_1_16', 'link-meta'], {waitRender: true});
        await this.browser.typeInto(['edit-modal', 'meta'], '{"number": 123, "string": "abc"}', {clear: true});
        await this.browser.assertImage('edit-modal', {removeShadows: true});

        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await category.moveTo();
        await this.browser.assertImage('group_group_code_1_1');
    });

    it('Добавление невалидной меты связи категории с прилавком. Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.fr.group_code_3_1), {region: 'fr'});
        const category = await this.browser.findByTestId('category_category_code_3_16');
        await category.moveTo();
        await this.browser.clickInto(['category_category_code_3_16', 'link-meta'], {waitRender: true});
        await this.browser.typeInto(['edit-modal', 'meta'], '{"number": 123]]]', {clear: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.assertImage('edit-modal', {removeShadows: true});
    });

    it('Смена порядка категорий на прилавке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        await this.browser.dragAndDrop('category_category_code_1_2', 'category_category_code_1_16', {
            offset: 'right'
        });
        await this.browser.waitUntilRendered();
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Удалить категорию с прилавка через три точки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        const category = await this.browser.findByTestId('category_category_code_1_16');
        await category.moveTo();
        await this.browser.clickInto(['category_category_code_1_16', 'more'], {waitRender: true});
        await this.browser.assertImage(['category_category_code_1_16', 'more', 'menu'], {removeShadows: true});

        await this.browser.clickInto(['category_category_code_1_16', 'more', 'menu', 'delete'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Открытие категории через три точки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        const category = await this.browser.findByTestId('category_category_code_1_16');
        await category.moveTo();
        await this.browser.clickInto(['category_category_code_1_16', 'more'], {waitRender: true});

        await this.browser.clickInto(['category_category_code_1_16', 'more', 'open'], {
            waitNavigation: true,
            waitRender: true
        });
        expect(await this.browser.getUrl()).to.match(
            new RegExp(
                ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1) + `\\?category=${categories.ru.category_code_1_16}`
            )
        );
    });

    it('Клик в категорию на прилавке. Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.fr.group_code_3_1), {region: 'fr'});
        await this.browser.clickInto('category_category_code_3_2', {
            waitNavigation: true,
            waitRender: true
        });
        expect(await this.browser.getUrl()).to.match(
            new RegExp(ROUTES.CLIENT.GROUP(groups.fr.group_code_3_1) + `\\?category=${categories.fr.category_code_3_2}`)
        );
    });

    it('Нельзя сделать категорию активной без фото на прилавке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_17));
        await this.browser.clickInto('category_category_code_1_10', {
            waitNavigation: true,
            waitRender: true
        });
        expect(await this.browser.getUrl()).to.match(
            new RegExp(
                ROUTES.CLIENT.GROUP(groups.ru.group_code_1_17) + `\\?category=${categories.ru.category_code_1_10}`
            )
        );
        const basePath = ['status', 'active'];
        await this.browser.waitForTestIdSelectorDisabled(basePath);
        const activeButton = await this.browser.findByTestId(basePath);
        await activeButton.moveTo();
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Сделать категорию на прилавке неактивной, если категория в нескольких прилавках', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        await this.browser.clickInto('category_category_code_1_16', {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.clickInto(['status', 'disabled'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Смена названий категории на разных языках, только для одного из двух прилавков. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.il.group_code_4_1), {
            region: 'il',
            dataLang: 'en'
        });
        await this.browser.clickInto('category_category_code_4_1', {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.clickInto(['translations', 'en']);
        await this.browser.typeInto('long-title-en', 'test-long-title', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'update-all']);
        await this.browser.clickInto(['edit-modal', 'select-item_group_code_4_2', 'checkbox'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.il.group_code_4_1), {
            region: 'il',
            dataLang: 'en'
        });
        await this.browser.assertImage('base-layout');

        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.il.group_code_4_2), {
            region: 'il',
            dataLang: 'en'
        });
        await this.browser.assertImage('base-layout');
    });

    it('Нельзя удалить фото категории, которое выбрано у категории на прилавке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        await this.browser.clickInto('category_category_code_1_2', {
            waitNavigation: true,
            waitRender: true
        });
        const basePath = ['image-with-formats_img_1_2_1.png', 'delete'];
        await this.browser.waitForTestIdSelectorAriaDisabled(basePath);
        const deleteButton = await this.browser.findByTestId(basePath);
        await deleteButton.moveTo();
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('catalog-layout_info');

        await this.browser.clickInto(['image-reference-tooltip', `link_${groups.ru.group_code_1_1}`], {
            waitNavigation: true,
            waitRender: true
        });
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1)));
    });

    it('Нельзя удалить формат фото категории, который выбран у категории на прилавке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        await this.browser.clickInto('category_category_code_1_2', {
            waitNavigation: true,
            waitRender: true
        });
        const basePath = ['image-with-formats_img_1_2_1.png', 'image-format-2'];
        await this.browser.waitForTestIdSelectorAriaDisabled(basePath);
        const deleteButton = await this.browser.findByTestId(basePath);
        await deleteButton.moveTo();
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Смена фото и форматов для категории, которая есть в нескольких прилавках', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_2));
        await this.browser.clickInto('category_category_code_1_3', {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.clickInto(['image-with-formats_img_1_3_1.png', 'image-format-6'], {waitRender: true});
        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('img1.png'));
        await this.browser.waitForTestIdSelectorInDom('image-with-formats_img1.png');
        await this.browser.clickInto(['image-with-formats_img1.png', 'image-format-3'], {waitRender: true});
        await this.browser.clickInto(['image-with-formats_img1.png', 'image-format-4'], {waitRender: true});
        await this.browser.clickInto(['image-with-formats_img1.png', 'image-format-2'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Стрелка назад из редактирования конкретной категории на прилавке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        await this.browser.clickInto('category_category_code_1_2', {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.clickInto(['catalog-layout_roll', 'back'], {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.assertImage('base-layout');
    });

    it('Смена описания категории на прилавке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        await this.browser.clickInto('category_category_code_1_2', {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.typeInto('description', 'test-description', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Смена меты категории на прилавке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        await this.browser.clickInto('category_category_code_1_2', {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.typeInto('meta', '{"number": 123, "string": "abc"}', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Закрыть прилавок', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        await this.browser.clickInto('close-button', {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(
            new RegExp(ROUTES.CLIENT.CATALOG_TAB('groups').replace('?', '\\?'))
        );
        await this.browser.assertImage('base-layout');
    });

    it('Смена языка данных на странице прилавка. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.il.group_code_4_1), {region: 'il'});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('data-lang-select', {waitRender: true});
        await this.browser.clickInto(['data-lang-select_dropdown-menu', 'en'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Смена языка интерфейса на странице прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('ui-lang-select', {waitRender: true});
        await this.browser.clickInto(['ui-lang-select_dropdown-menu', 'en'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Нельзя сделать прилавок активным без фото', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_10));
        const basePath = ['status', 'active'];
        await this.browser.waitForTestIdSelectorDisabled(basePath);
        const activeButton = await this.browser.findByTestId(basePath);
        await activeButton.moveTo();
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Смена статуса прилавка, который есть только в одной сетке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        await this.browser.clickInto(['status', 'disabled']);
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Смена названия прилавка на разных языках, сразу на нескольких сетках', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.il.group_code_4_1), {
            region: 'il',
            dataLang: 'en'
        });
        await this.browser.clickInto(['translations', 'en']);
        await this.browser.typeInto('long-title-en', 'test-long-title-en', {clear: true});
        await this.browser.clickInto(['translations', 'he']);
        await this.browser.typeInto('long-title-he', 'test-long-title-he', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Смена фото прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        await this.browser.clickInto(['image_img_1_1_1.png', 'delete']);
        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('img1.png'));
        await this.browser.waitForTestIdSelectorInDom('image_img1.png');
        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('img2.png'));
        await this.browser.waitForTestIdSelectorInDom('image_img2.png');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Смена описания прилавка только на одной из двух сеток', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_3));
        await this.browser.typeInto('description', 'test-description', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'update-all']);
        await this.browser.clickInto(['edit-modal', 'select-item_grid_code_1_3', 'checkbox'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');

        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_3));
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Изменить мета на валидное. Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.fr.group_code_3_1), {region: 'fr'});
        await this.browser.performScroll('catalog-layout_info');
        await this.browser.typeInto('meta', '{"number": 123, "string": "abc"}', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Изменить мета на невалидное', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        await this.browser.performScroll('catalog-layout_info');
        await this.browser.typeInto('meta', '{"number": 123]]]', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Отмена изменений на прилавке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        await this.browser.clickInto(['status', 'disabled']);
        await this.browser.clickInto('cancel-button', {waitRender: true});
        await this.browser.assertImage('confirmation-modal', {removeShadows: true});

        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button'], {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Переключение на вкладку сеток данного прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_4));
        await this.browser.clickInto('\\[id$="used-in-tab"]', {waitRender: true});
        await this.browser.assertImage('entity-links');
    });

    it('Клик в одну из сеток, в которых есть данный прилавок', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_4));
        await this.browser.clickInto('\\[id$="used-in-tab"]', {waitRender: true});
        await this.browser.clickInto('entity-link_grid_code_1_6', {waitNavigation: true, waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Поиск по названию категории на странице прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_1));
        await this.browser.typeInto('search_input', 'раз', {clear: true});
        await this.browser.assertImage('group-tree');
    });

    it('Поиск по коду категории на странице прилавка. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.il.group_code_4_1), {region: 'il'});
        await this.browser.typeInto('search_input', 'de_4_1', {clear: true});
        await this.browser.assertImage('group-tree');
    });

    it('Нельзя удалить фото прилавка, которое выбрано для прилавка на сетке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_3));
        const basePath = ['image_img_1_3_1.png', 'delete'];
        await this.browser.waitForTestIdSelectorAriaDisabled(basePath);
        const deleteButton = await this.browser.findByTestId(basePath);
        await deleteButton.moveTo();
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('catalog-layout_info');

        await this.browser.clickInto(['image-reference-tooltip', `link_${grids.ru.grid_code_1_2}`], {
            waitNavigation: true,
            waitRender: true
        });
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.GRID(grids.ru.grid_code_1_2)));
    });

    it('Кликабельность картинок в прилавке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_3));
        await this.browser.clickInto(['image_img_1_3_1.png', 'thumbnail'], {waitRender: true});
        await this.browser.assertImage('image-view-modal', {removeShadows: true});
        await this.browser.clickInto(['image-view-modal', '\\.ant-modal-close'], {waitRender: true});
        await this.browser.waitForTestIdSelectorNotVisible('image-view-modal');
    });

    it('Не загружается фотография 799х800 для прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_3));
        await this.browser.uploadFileInto(['images-upload', 'file-input'], getFixturePath('img-799x800.png'));
        await this.browser.assertImage('images_container');
    });

    it('Не загружается фотография 800х799 для прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_3));
        await this.browser.uploadFileInto(['images-upload', 'file-input'], getFixturePath('img-800x799.png'));
        await this.browser.assertImage('images_container');
    });

    it('Загружается фотография 800х800 для прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_3));
        await this.browser.uploadFileInto(['images-upload', 'file-input'], getFixturePath('img-800x800.png'));
        await this.browser.waitForTestIdSelectorInDom('image_img-800x800.png');
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('images_container');
    });
});
