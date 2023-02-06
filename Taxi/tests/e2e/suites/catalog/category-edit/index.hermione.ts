import {categories, frontCategories, groups} from 'tests/e2e/seed-db-map';
import createImageFile from 'tests/e2e/utils/create-image-file';
import getFixturePath from 'tests/e2e/utils/fixture';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Редактирование категории в витрине', function () {
    it('Общий вид страницы категории с фото без подкатегорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_4));
        await this.browser.waitForTestIdSelectorDisabled('code');
        await this.browser.assertImage('base-layout');
    });

    it('Общий вид страницы категории без фото с подкатегориями. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.il.category_code_4_10), {region: 'il'});
        await this.browser.waitForTestIdSelectorDisabled('code');
        await this.browser.assertImage('base-layout');
    });

    it('Добавление подкатегории в категорию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1));
        await this.browser.clickInto('add-front-category-button', {waitRender: true});
        await this.browser.assertImage('add-modal', {removeShadows: true});

        await this.browser.clickInto(['row_front_category_code_1_2', '\\.ant-tree-switcher'], {waitRender: true});
        await this.browser.clickInto('row_front_category_code_7_0', {waitRender: true});
        await this.browser.clickInto('row_front_category_code_7_1', {waitRender: true});
        await this.browser.clickInto(['add-modal', 'add-modal__ok_button'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Нельзя добавить уже добавленную подкатегорию в категорию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1));
        await this.browser.clickInto('add-front-category-button', {waitRender: true});
        await this.browser.clickInto(['row_front_category_code_1_0', '\\.ant-tree-switcher'], {waitRender: true});
        await this.browser.waitForTestIdSelectorNotClickable('row_front_category_code_5_0');
        await this.browser.waitForTestIdSelectorDisabled(['add-modal', 'add-modal__ok_button']);
        await this.browser.assertImage('add-modal', {removeShadows: true});
    });

    it('Поиск по дереву подкатегорий при добавлении подкатегории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1));
        await this.browser.clickInto('add-front-category-button', {waitRender: true});
        await this.browser.typeInto(['add-modal', 'search_input'], 'всю');
        await this.browser.assertImage('add-modal', {removeShadows: true});
    });

    it('Скролл дерева подкатегорий при выборе подкатегории. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.il.category_code_4_1), {region: 'il'});
        await this.browser.clickInto('add-front-category-button', {waitRender: true});
        await this.browser.performScroll(['add-modal', '\\.ant-tree-list-holder']);
        await this.browser.assertImage('add-modal', {removeShadows: true});
    });

    it('Отмена выбора подкатегории для категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1));
        await this.browser.clickInto('add-front-category-button', {waitRender: true});
        await this.browser.clickInto(['row_front_category_code_1_2', '\\.ant-tree-switcher'], {waitRender: true});
        await this.browser.clickInto('row_front_category_code_7_0', {waitRender: true});
        await this.browser.clickInto('row_front_category_code_7_1', {waitRender: true});
        await this.browser.clickInto(['add-modal', 'add-modal__cancel_button'], {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Развернуть-свернуть информацию о подкатегории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1));
        await this.browser.clickInto(['front-category_front_category_code_5_0', 'expand'], {waitRender: true});
        await this.browser.assertImage('front-category_front_category_code_5_0');

        await this.browser.clickInto(['front-category_front_category_code_5_0', 'expand'], {waitRender: true});
        await this.browser.assertImage('front-category_front_category_code_5_0');
    });

    it('Ховер на подкатегорию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1));
        const frontCategory = await this.browser.findByTestId('front-category_front_category_code_5_0');
        await frontCategory.moveTo();
        await this.browser.assertImage('front-category_front_category_code_5_0');
    });

    it('Копирование кода подкатегории по ховеру в центральном столбце', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1));
        const codeWithCopy = await this.browser.findByTestId([
            'front-category_front_category_code_5_0',
            'code-with-copy'
        ]);
        await codeWithCopy.moveTo();
        await this.browser.clickInto(['front-category_front_category_code_5_0', 'code-with-copy', 'button']);
        expect(await this.browser.clipboardReadText()).to.equal('front_category_code_5_0');
    });

    it('Ссылка на родительскую категорию. Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.fr.category_code_3_1), {
            region: 'fr'
        });
        await this.browser.clickInto(['front-category_front_category_code_45_0', 'expand'], {waitRender: true});
        await this.browser.clickInto(['front-category_front_category_code_45_0', 'parent-category-link'], {
            waitNavigation: true,
            waitRender: true
        });
        expect(await this.browser.getUrl()).to.match(
            new RegExp(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.fr.front_category_code_3_0))
        );
    });

    it('Ссылка на подкатегорию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1));
        await this.browser.clickInto(['front-category_front_category_code_5_0', 'expand'], {waitRender: true});
        await this.browser.clickInto(['front-category_front_category_code_5_0', 'category-link'], {
            waitNavigation: true,
            waitRender: true
        });
        expect(await this.browser.getUrl()).to.match(
            new RegExp(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_5_0))
        );
    });

    it('Ссылка на товары в подкатегории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1));
        await this.browser.clickInto(['front-category_front_category_code_5_0', 'expand'], {waitRender: true});
        await this.browser.clickInto(['front-category_front_category_code_5_0', 'products-count-link'], {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.assertImage('filter-list');
    });

    it('Смена порядка подкатегорий в категории, которая есть в нескольких прилавках', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_3));
        await this.browser.dragAndDrop(
            'front-category_front_category_code_5_3',
            'front-category_front_category_code_5_4',
            {
                offset: 'bottom'
            }
        );
        await this.browser.waitUntilRendered();
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('edit-modal', {removeShadows: true});

        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Наличие меню за тремя точками в подкатегориях', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1));
        const frontCategory = await this.browser.findByTestId('front-category_front_category_code_5_0');
        await frontCategory.moveTo();
        await this.browser.assertImage('front-category_front_category_code_5_0');

        const basePath = ['front-category_front_category_code_5_0', 'more'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.assertImage([...basePath, 'menu'], {removeShadows: true});
    });

    it('Ссылка на родительскую категорию в меню трех точек', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1), {
            patchStyles: {showOptions: true}
        });
        const basePath = ['front-category_front_category_code_5_0', 'more'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'menu', 'open-parent-category'], {
            waitNavigation: true,
            waitRender: true
        });
        expect(await this.browser.getUrl()).to.match(
            new RegExp(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0))
        );
    });

    it('Ссылка на подкатегорию в меню трех точек', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1), {
            patchStyles: {showOptions: true}
        });
        const basePath = ['front-category_front_category_code_5_0', 'more'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'menu', 'open-category'], {
            waitNavigation: true,
            waitRender: true
        });
        expect(await this.browser.getUrl()).to.match(
            new RegExp(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_5_0))
        );
    });

    it('Ссылка на товары в подкатегории в меню трех точек', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1), {
            patchStyles: {showOptions: true}
        });
        const basePath = ['front-category_front_category_code_5_0', 'more'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'menu', 'open-products'], {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.assertImage('filter-list');
    });

    it('Удалить подкатегорию из категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_2), {
            patchStyles: {showOptions: true}
        });
        await this.browser.clickInto(['front-category_front_category_code_5_1', 'delete'], {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Модалка при отмене внесения изменений. Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.fr.category_code_3_1), {
            region: 'fr'
        });
        await this.browser.clickInto(['status', 'disabled']);
        await this.browser.clickInto('cancel-button', {waitRender: true});
        await this.browser.assertImage('confirmation-modal', {removeShadows: true});
    });

    it('Смена статуса категории в одном из нескольких прилавков', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_3));
        await this.browser.clickInto(['status', 'disabled']);
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'update-all']);
        await this.browser.clickInto(['edit-modal', 'select-item_group_code_1_2', 'checkbox'], {waitRender: true});
        await this.browser.clickInto(['edit-modal', 'edit-modal__ok_button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_2));
        await this.browser.clickInto('category_category_code_1_3', {waitRender: true});
        await this.browser.assertImage('base-layout');

        await this.browser.openPage(ROUTES.CLIENT.GROUP(groups.ru.group_code_1_3));
        await this.browser.clickInto('category_category_code_1_3_copy', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Нельзя сделать категорию активной, если у нее нет фото', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_10));
        const basePath = ['status', 'active'];
        await this.browser.waitForTestIdSelectorDisabled(basePath);
        const activeButton = await this.browser.findByTestId(basePath);
        await activeButton.moveTo();
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Смена диплинк и валидация диплинк на странице категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1));
        await this.browser.typeInto('deeplink', 'диплинк_русскими_буквами', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');

        await this.browser.typeInto('deeplink', 'test-deep-link-for-category-code-1-1', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Стереть длинное название категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1));
        await this.browser.typeInto('long-title-ru', '', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Смена названия на одном из языков', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.il.category_code_4_3), {
            region: 'il',
            dataLang: 'en'
        });
        await this.browser.clickInto(['translations', 'en']);
        await this.browser.typeInto('long-title-en', 'test-long-title', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Загрузка нескольких фото', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_10));
        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('img1.png'));
        await this.browser.waitForTestIdSelectorInDom('image-with-formats_img1.png');
        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('img2.png'));
        await this.browser.waitForTestIdSelectorInDom('image-with-formats_img2.png');
        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('img3.png'));
        await this.browser.waitForTestIdSelectorInDom('image-with-formats_img3.png');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Загрузка одного фото в категорию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_10));
        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('img1.png'));
        await this.browser.waitForTestIdSelectorInDom('image-with-formats_img1.png');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
        await this.browser.assertImage('header-panel');
    });

    it('Удалить одно фото с категории с несколькими фото', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1));
        await this.browser.clickInto(['image-with-formats_img_1_1_1.png', 'delete']);
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Удаление всех фото с активной категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1));
        await this.browser.clickInto(['image-with-formats_img_1_1_1.png', 'delete']);
        await this.browser.clickInto(['image-with-formats_img_1_1_2.png', 'delete']);
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Загрузка неразрешенного формата фото', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1));
        await this.browser.uploadFileInto(['images-upload', 'file-input'], getFixturePath('sample.gif'));
        await this.browser.assertImage('images-upload');
        await this.browser.assertImage('header-panel');
    });

    it('Загрузка большого фото и смена формата на нормальном фото', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_10));
        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('img1.png'));
        await this.browser.waitForTestIdSelectorInDom('image-with-formats_img1.png');
        await this.browser.clickInto(['image-with-formats_img1.png', 'image-format-4']);
        await this.browser.clickInto(['image-with-formats_img1.png', 'image-format-6']);
        await this.browser.clickInto(['image-with-formats_img1.png', 'image-format-2']);
        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('img2.png', 2400));
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Изменить описание категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_6));
        await this.browser.typeInto('description', 'test-description', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Изменить мета на невалидное', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1));
        await this.browser.performScroll('catalog-layout_info');
        await this.browser.typeInto('meta', '{"number": 123]]]', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Изменить мета на валидное', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1));
        await this.browser.performScroll('catalog-layout_info');
        await this.browser.typeInto('meta', '{"number": 123, "string": "abc"}', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Закрыть категорию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1));
        await this.browser.clickInto('close-button', {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(
            new RegExp(ROUTES.CLIENT.CATALOG_TAB('categories').replace('?', '\\?'))
        );
        await this.browser.assertImage('base-layout');
    });

    it('Поиск подкатегорий по коду на странице категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_3));
        await this.browser.typeInto('search_input', 'de_5_4', {clear: true});
        await this.browser.assertImage('category-tree');
    });

    it('Поиск подкатегорий по названию на странице категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_3));
        await this.browser.typeInto('search_input', 'всю', {clear: true});
        await this.browser.assertImage('category-tree');
    });

    it('Смена языка интерфейса на странице категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1));
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('ui-lang-select', {waitRender: true});
        await this.browser.clickInto(['ui-lang-select_dropdown-menu', 'en'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Смена языка данных на странице категории. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.il.category_code_4_3), {region: 'il'});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('data-lang-select', {waitRender: true});
        await this.browser.clickInto(['data-lang-select_dropdown-menu', 'en'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Переключение на вкладку с прилавками, если их нет у данной категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_1));
        await this.browser.clickInto('\\[id$="used-in-tab"]', {waitRender: true});
        await this.browser.assertImage('entity-links');
    });

    it('Нельзя удалить фото категории, которое выбрано у категории на прилавке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_3));
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
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_3));
        const basePath = ['image-with-formats_img_1_3_1.png', 'image-format-2'];
        await this.browser.waitForTestIdSelectorAriaDisabled(basePath);
        const deleteButton = await this.browser.findByTestId(basePath);
        await deleteButton.moveTo();
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('catalog-layout_info');
    });

    it('Кликабельность картинок в категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_3));
        await this.browser.clickInto(['image-with-formats_img_1_3_1.png', 'thumbnail'], {waitRender: true});
        await this.browser.assertImage('image-view-modal', {removeShadows: true});
        await this.browser.clickInto(['image-view-modal', 'image-view-modal__close-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorNotVisible('image-view-modal');
    });

    it('Не загружается фотография 399х400 для категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_3));
        await this.browser.uploadFileInto(['images-upload', 'file-input'], getFixturePath('img-399x400.png'));
        await this.browser.assertImage('images_container');
    });

    it('Не загружается фотография 400х399 для категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_3));
        await this.browser.uploadFileInto(['images-upload', 'file-input'], getFixturePath('img-400x399.png'));
        await this.browser.assertImage('images_container');
    });

    it('Загружается фотография 400х400 для категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATEGORY(categories.ru.category_code_1_3));
        await this.browser.uploadFileInto(['images-upload', 'file-input'], getFixturePath('img-400x400.png'));
        await this.browser.waitForTestIdSelectorInDom('image-with-formats_img-400x400.png');
        await this.browser.assertImage('images_container');
    });
});
