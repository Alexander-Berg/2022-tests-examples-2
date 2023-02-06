import crypto from 'crypto';
import createImageFile from 'tests/e2e/utils/create-image-file';
import getFixturePath from 'tests/e2e/utils/fixture';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {DbTable} from '@/src/entities/const';

describe('Просмотр и редактирование товара', function () {
    it('Заголовок страницы товара в режиме просмотра', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.assertImage('header-panel');
    });

    it('Просмотр товара не доступен в другом регионе', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        const path = await this.browser.getPath();
        await this.browser.openPage(path, {region: 'il'});
        await this.browser.assertImage();
    });

    it('Клик в "Закрыть" возвращает к таблице товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.clickInto('close-button', {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.PRODUCTS));
    });

    it('Клик в категорию товара открывает список товаров этой категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.clickInto('product-breadcrumb', {waitNavigation: true, waitRender: true});
        await this.browser.assertImage('filter-list');
    });

    it('Клик в ИМ открывает страницу этой ИМ', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.clickInto('infomodel-link', {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.INFOMODEL('\\d')));
    });

    it('Удалить изображение товара (Израиль)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000151), {region: 'il'});

        await this.browser.clickInto(['product-image', 'delete-image']);
        await this.browser.waitForTestIdSelectorInDom(['product-image', 'file-input']);
    });

    it('Добавить изображение товара (Россия)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.clickInto(['product-image', 'delete-image']);

        await this.browser.uploadFileInto(['product-image', 'file-input'], createImageFile('product_image.png'));
        await this.browser.waitForTestIdSelectorInDom(['product-image', 'thumbnail'], {timeout: 30_000});
    });

    it('Скачать изображение товара (Франция)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000101), {region: 'fr'});

        await this.browser.clickInto(['product-image', 'download-image'], {waitRender: true});
        const file = await this.browser.getDownloadedFile('product_attribute_code_101_23_0.png', {purge: true});
        const hash = crypto.createHash('md5').update(file);
        expect(hash.digest('hex')).to.matchSnapshot(this);
    });

    it('Переключить таб на фронт-категории товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001), {clearLocalStorage: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Поиск по ФК товара России', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001), {clearLocalStorage: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true});
        await this.browser.typeInto('search', 'только');
        await this.browser.assertImage(['tree-table', 'list-holder']);
    });

    it('Развернуть дерево ФК товара Франции', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000101), {
            region: 'fr',
            clearLocalStorage: true,
            localStorageItems: buildLocalStorageValue({
                isAllExpanded: false,
                isAllCollapsed: true,
                isAllSelected: false,
                isAllActive: false
            })
        });

        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true, waitForClickable: true});
        await this.browser.clickInto(['product_fc_row_front_category_code_3_0', 'expand_icon'], {
            waitRender: true,
            waitForClickable: true
        });
        await this.browser.assertImage(['tree-table', 'list-holder']);
    });

    it('Удалить и добавить ФК товару Великобритании', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000051), {
            region: 'gb',
            clearLocalStorage: true,
            localStorageItems: buildLocalStorageValue({
                isAllExpanded: true,
                isAllCollapsed: false,
                isAllSelected: false
            })
        });

        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true});
        await this.browser.clickInto('product_fc_row_front_category_code_25_0', {waitRender: true});
        await this.browser.clickInto('product_fc_row_front_category_code_25_3');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage(['tree-table', 'list-holder']);
    });

    it('Показать неактивные ФК', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001), {
            clearLocalStorage: true,
            localStorageItems: buildLocalStorageValue({
                isAllSelected: false,
                isAllCollapsed: false,
                isAllExpanded: true
            })
        });

        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true, waitForClickable: true});
        await this.browser.clickInto('show-inactive', {waitRender: true, waitForClickable: true});
        await this.browser.assertImage(['tree-table', 'list-holder']);
    });

    it('Показать назначенные ФК', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001), {
            clearLocalStorage: true,
            localStorageItems: buildLocalStorageValue({
                isAllCollapsed: false,
                isAllExpanded: true,
                isAllSelected: false,
                isAllActive: false
            })
        });

        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true});
        await this.browser.clickInto('show-assigned', {waitRender: true});
        await this.browser.assertImage(['tree-table', 'list-holder']);
    });

    it('Развернуть все категории в товаре', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001), {
            clearLocalStorage: true,
            localStorageItems: buildLocalStorageValue({
                isAllCollapsed: false,
                isAllExpanded: true,
                isAllActive: false,
                isAllSelected: false
            })
        });

        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true});
        await this.browser.clickInto('expand-all', {waitRender: true});
        await this.browser.assertImage(['tree-table', 'list-holder']);
    });

    it('Свернуть все категории в товаре', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001), {
            clearLocalStorage: true,
            localStorageItems: buildLocalStorageValue({
                isAllCollapsed: false,
                isAllExpanded: true,
                isAllActive: false,
                isAllSelected: false
            })
        });

        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true, waitForClickable: true});
        await this.browser.clickInto('collapse-all', {waitRender: true, waitForClickable: true});
        await this.browser.assertImage(['tree-table', 'list-holder']);
    });

    it('Добавить два изображения в множественный атрибут на товаре', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.uploadFileInto(['product-image', 'file-input'], createImageFile('product_image_1.png'));
        await this.browser.uploadFileInto(['product-image', 'file-input'], createImageFile('product_image_2.png'));
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom('query-state-spinner-spinning');
        await this.browser.assertImage('product-image');
    });

    it('Удалить одно из изображений из множественного атрибута на товаре', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.clickInto(['image_attribute_code_1_1-array', 'image-drag-2', 'delete-image']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('image_attribute_code_1_1-array');
        await this.browser.assertImage('image_attribute_code_1_1-array');
    });

    it('Поменять порядок и выбрать другое главное изображение на товаре', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.uploadFileInto(['product-image', 'file-input'], createImageFile('product_image_1.png'));
        await this.browser.uploadFileInto(['product-image', 'file-input'], createImageFile('product_image_2.png'));
        await this.browser.waitUntilRendered({minStableIterations: 5});
        await this.browser.dragAndDrop(['image-array', 'image-drag-2'], ['image-array', 'image-drag-0']);
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorNotInDom('submit-button');
        await this.browser.waitForTestIdSelectorInDom(['product-image', 'thumbnail', 'image']);
        await this.browser.assertImage('product-image');
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.assertImage('^products-table-row');
    });

    it('Добавление большого файла для множественных изображений', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.uploadFileInto(['product-image', 'file-input'], createImageFile('product_image_valid.png'));
        await this.browser.uploadFileInto(
            ['product-image', 'file-input'],
            createImageFile('product_image_big.png', 2400)
        );
        await this.browser.assertImage('product-image');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom('query-state-spinner-spinning');
        await this.browser.assertImage('product-image');
    });

    it('Внести изменение в товар', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        const longNameElement = await this.browser.findByTestId('longNameLoc_ru');
        const longNameValue = await longNameElement.getValue();

        await this.browser.typeInto('longNameLoc_ru', longNameValue.split('').reverse().join(''), {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.assertImage('^products-table-row');
    });

    it('Деактивировать товар', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.clickInto(['status', 'disabled_label']);
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.assertImage('^products-table-row');
    });

    it('Отменить внесенное изменение товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        const longNameElement = await this.browser.findByTestId('longNameLoc_ru');
        const longNameValue = await longNameElement.getValue();

        await this.browser.typeInto('longNameLoc_ru', longNameValue.split('').reverse().join(''), {clear: true});
        await this.browser.clickInto('cancel-button');
        await this.browser.waitForTestIdSelectorInDom('confirmation-modal');
        await this.browser.assertImage('confirmation-modal', {removeShadows: true});
        await this.browser.clickInto('confirmation-modal__ok-button', {waitRender: true, waitForClickable: true});
        await this.browser.assertImage('longNameLoc_ru', {removeShadows: true});
    });

    it('Клик в "Добавить штрихкод" создает новое окно для ввода штрихкода', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.clickInto('add_new_barcode', {waitRender: true});
        await this.browser.assertImage('basic-attributes', {removeShadows: true});
    });

    it('Поля shortName, markCount и markCountUnit доступны для редактирования, Великобритания', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000051), {region: 'gb'});
        await this.browser.typeInto('shortNameLoc_en', 'new short name', {clear: true});
        await this.browser.assertImage('shortNameLoc_en');
        await this.browser.typeInto('markCount', '12345', {clear: true});
        await this.browser.assertImage('markCount');
        await this.browser.typeInto('markCountUnit', 'new mark count unit', {clear: true});
        await this.browser.assertImage('markCountUnit');
    });

    it('Клик в поле системного атрибута и потеря фокуса', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.clickInto('longNameLoc_ru', {waitRender: true});
        await this.browser.assertImage('longNameLoc_ru');
        await this.browser.clickInto('default_panel', {waitRender: true});
        await this.browser.assertImage('longNameLoc_ru');
    });

    it('Изменить на false пустой атрибут через интерфейс', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.clickInto('boolean_attribute_code_0_1_off');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom('submit-button');
        await this.browser.assertImage('boolean_attribute_code_0_1');
    });

    it('Изменить на true пустой атрибут через интерфейс', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.clickInto('boolean_attribute_code_0_1_on');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom('query-state-spinner-spinning');
        await this.browser.assertImage('boolean_attribute_code_0_1');
    });

    it('Очистить false-атрибут через интерфейс', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.clickInto('boolean_attribute_code_0_0_unset');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('boolean_attribute_code_0_0');
    });

    it('Очистить true-атрибут через интерфейс', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));
        await this.browser.clickInto('boolean_attribute_code_0_0_unset');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('boolean_attribute_code_0_0');
    });

    it('Название товара и информация о товаре в entity header', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.assertImage('entity-header-info');
        await this.browser.assertImage(['product-tabs', '\\.ant-tabs-nav']);
    });

    it('Неизменный атрибут типа "текстовая строка" можно задать через UI', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000002));

        await this.browser.typeInto('string_attribute_code_5_2_loc_ru', 'some_text');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('string_attribute_code_5_2_loc_ru');
    });

    it('Неизменный атрибут нельзя изменить через UI', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000008));
        await this.browser.waitForTestIdSelectorDisabled('string_attribute_code_5_2_loc_ru');
        await this.browser.assertImage(['attribute_group_code_3', 'input_wrapper-string_attribute_code_5_2_loc']);
    });

    it('Загрузить через интерфейс главное фото со сторонами меньше 800', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.clickInto(['image-array', 'image-drag-0', 'delete-image'], {waitRender: true});

        await this.browser.uploadFileInto(
            ['product-image', 'file-input'],
            createImageFile('product_image_invalid.png', 250)
        );
        await this.browser.assertImage('product-image');
    });

    it('Загрузить через интерфейс главное фото с одной стороной меньше 800', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.clickInto(['image-array', 'image-drag-0', 'delete-image'], {waitRender: true});

        await this.browser.uploadFileInto(['product-image', 'file-input'], getFixturePath('600x800-image.jpeg'));
        await this.browser.assertImage('product-image');
    });

    it('Тип номенклатуры товара в России нельзя очистить через UI', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        const element = await this.browser.findByTestId('nomenclatureType');
        await element.moveTo();

        await this.browser.assertImage('nomenclatureType');
    });

    it('В главное фото нельзя добавить .gif файл', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.clickInto(['image-array', 'image-drag-0', 'delete-image'], {waitRender: true});

        await this.browser.uploadFileInto(['product-image', 'file-input'], getFixturePath('sample.gif'));
        await this.browser.assertImage('product-image');
    });

    it('Можно добавить все допустимые форматы в множественный атрибут-изображение', async function () {
        await this.browser.executeSql(
            `
            UPDATE ${DbTable.ATTRIBUTE}
            SET properties = jsonb_set(properties , '{allowedImageExtensions}', '["jpeg", "jpg", "png", "gif"]')
            WHERE code = 'image';
            `
        );

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.clickInto(['image-array', 'image-drag-0', 'delete-image'], {waitRender: true});

        await this.browser.uploadFileInto(['product-image', 'file-input'], getFixturePath('sample.jpeg'));
        await this.browser.uploadFileInto(['product-image', 'file-input'], getFixturePath('sample.jpg'));
        await this.browser.uploadFileInto(['product-image', 'file-input'], createImageFile('sample.png'));
        await this.browser.uploadFileInto(['product-image', 'file-input'], getFixturePath('sample.gif'));

        await this.browser.waitUntilRendered({minStableIterations: 5});
        await this.browser.assertImage('product-image');
    });

    it('Нельзя добавить недопустимые форматы изображений', async function () {
        await this.browser.executeSql(
            `
            UPDATE ${DbTable.ATTRIBUTE}
            SET properties = jsonb_set(properties , '{allowedImageExtensions}', '["jpeg", "jpg"]')
            WHERE code = 'image_attribute_code_1_0';
            `
        );

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.clickInto(['image_attribute_code_1_0', 'delete-image']);

        await this.browser.uploadFileInto(['image_attribute_code_1_0', 'file-input'], createImageFile('sample.png'));
        await this.browser.assertImage('image_attribute_code_1_0');

        await this.browser.uploadFileInto(['image_attribute_code_1_0', 'file-input'], getFixturePath('sample.gif'));
        await this.browser.assertImage('image_attribute_code_1_0');

        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom('submit-button');
        await this.browser.assertImage('image_attribute_code_1_0');
    });

    it('Просмотр .gif изображений на товаре', async function () {
        await this.browser.executeSql(
            `
            UPDATE ${DbTable.ATTRIBUTE}
            SET properties = jsonb_set(properties , '{allowedImageExtensions}', '["gif"]')
            WHERE code = 'image_attribute_code_1_0';
            `
        );

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000005));

        await this.browser.clickInto(['image_attribute_code_1_0', 'delete-image']);

        await this.browser.uploadFileInto(['image_attribute_code_1_0', 'file-input'], getFixturePath('sample.gif'));

        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.clickInto(['image_attribute_code_1_0', 'thumbnail'], {waitRender: true});
        await this.browser.assertImage('image-view-modal', {removeShadows: true});
    });

    it('Найти значение атрибута типа множественный список в карточке товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.typeInto(['multiselect_attribute_code_2_1', '\\input'], 'Об');
        await this.browser.waitUntilRendered();

        await this.browser.assertImage('multiselect_attribute_code_2_1', {removeShadows: true});
        await this.browser.assertImage('multiselect_attribute_code_2_1_dropdown-menu', {removeShadows: true});
    });

    it('Найти и выбрать значение атрибута типа выпадающий список в карточке товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.typeInto(['multiselect_attribute_code_2_1', '\\input'], 'Об');
        await this.browser.waitUntilRendered();

        await this.browser.clickInto('attribute_option_code_11_3', {waitRender: true});

        await this.browser.assertImage('multiselect_attribute_code_2_1', {removeShadows: true});
        await this.browser.assertImage('multiselect_attribute_code_2_1_dropdown-menu', {removeShadows: true});
    });

    it('Подсказка об обязательном аттрибуте', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        const tooltip = await this.browser.findByTestId([
            'attribute_group_code_2',
            'multiselect_attribute_code_2_1-container',
            'require-icon'
        ]);
        await tooltip.moveTo();

        await this.browser.assertImage(['attribute_group_code_2', 'multiselect_attribute_code_2_1-container']);
    });
});

type Search = {
    rawValue?: string;
    normalizedValue?: string;
};

type ExpandedState = {
    isAllCollapsed: boolean;
    isAllExpanded: boolean;
};

type FrontCategoryProductListStorageValue = {
    isAllSelected: boolean;
    isAllActive: boolean;
    search: Search;
} & ExpandedState;

function buildLocalStorageValue(values: Partial<FrontCategoryProductListStorageValue>) {
    return {
        frontCategoryProductList: {
            isAllSelected: true,
            isAllActive: true,
            isAllCollapsed: true,
            isAllExpanded: false,
            search: {},
            ...values
        }
    };
}
