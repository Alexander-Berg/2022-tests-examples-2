import crypto from 'crypto';
import {attributes, infoModels, requiredAttributes, specialAttributes} from 'tests/e2e/seed-db-map';
import {addAttributeToInfomodelByCode} from 'tests/e2e/utils/add-attribute-to-infomodel-by-code';
import setAttributeConfirmationValue from 'tests/e2e/utils/confirm-attribute';
import {createAttribute} from 'tests/e2e/utils/create-attribute';
import createImageFile from 'tests/e2e/utils/create-image-file';
import getFixturePath from 'tests/e2e/utils/fixture';
import makeAttributeConfirmable from 'tests/e2e/utils/make-attribute-confirmable';
import makeDataTestIdSelector from 'tests/e2e/utils/make-data-test-id-selector';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {DbTable} from '@/src/entities/const';
import {AttributeType} from 'types/attribute';

import {createUnusedAttribute} from './util';

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
        await this.browser.clickInto('header-panel', {waitRender: true});
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

        const longNameElement = await this.browser.findByTestId('longName_ru');
        const longNameValue = await longNameElement.getValue();

        await this.browser.typeInto('longName_ru', longNameValue.split('').reverse().join(''), {clear: true});
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

        const longNameElement = await this.browser.findByTestId('longName_ru');
        const longNameValue = await longNameElement.getValue();

        await this.browser.typeInto('longName_ru', longNameValue.split('').reverse().join(''), {clear: true});
        await this.browser.clickInto('cancel-button');
        await this.browser.waitForTestIdSelectorInDom('confirmation-modal');
        await this.browser.assertImage('confirmation-modal', {removeShadows: true});
        await this.browser.clickInto('confirmation-modal__ok-button', {waitRender: true, waitForClickable: true});
        await this.browser.assertImage('longName_ru', {removeShadows: true});
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
        await this.browser.clickInto('longName_ru', {waitRender: true});
        await this.browser.assertImage('longName_ru');
        await this.browser.clickInto('default_panel', {waitRender: true});
        await this.browser.assertImage('longName_ru');
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

    it('Для подтверждаемого, но не подтвержденного атрибута не показывается тайтл подтверждения', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await makeAttributeConfirmable(this.browser, attributes.boolean_attribute_code_0_0);

        await this.browser.assertImage(['attribute_group_code_1', 'boolean_attribute_code_0_0-name-labels']);
    });

    it('Подтвержденный атрибут в товаре отмечен галочкой, при ховере появляется хинт со статусом', async function () {
        await makeAttributeConfirmable(this.browser, attributes.boolean_attribute_code_0_0);
        await setAttributeConfirmationValue({
            browser: this.browser,
            productIdentifier: 10000001,
            attributeId: attributes.boolean_attribute_code_0_0
        });

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.assertImage(['attribute_group_code_1', 'boolean_attribute_code_0_0-name-labels']);

        const tooltip = await this.browser.findByTestId([
            'attribute_group_code_1',
            'boolean_attribute_code_0_0-name-labels',
            'confirmed-icon'
        ]);
        await tooltip.moveTo();

        await this.browser.waitUntilRendered();

        await this.browser.assertImage('\\.ant-tooltip-inner', {removeShadows: true});
    });

    it('Нельзя изменить подтвержденный атрибут через UI', async function () {
        await makeAttributeConfirmable(this.browser, attributes.boolean_attribute_code_0_0);
        await setAttributeConfirmationValue({
            browser: this.browser,
            productIdentifier: 10000001,
            attributeId: attributes.boolean_attribute_code_0_0
        });

        await makeAttributeConfirmable(this.browser, attributes.image_attribute_code_1_1);
        await setAttributeConfirmationValue({
            browser: this.browser,
            productIdentifier: 10000001,
            attributeId: attributes.image_attribute_code_1_1
        });

        await makeAttributeConfirmable(this.browser, specialAttributes.image);
        await setAttributeConfirmationValue({
            browser: this.browser,
            productIdentifier: 10000001,
            attributeId: specialAttributes.image
        });

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.waitForTestIdSelectorNotInDom(['image-array', 'image-drag-0', 'delete-image']);
        await this.browser.waitForTestIdSelectorNotInDom(['image_attribute_code_1_1', 'image-drag-1', 'delete-image']);

        await this.browser.assertImage(['attribute_group_code_1', 'boolean_attribute_code_0_0']);
        await this.browser.assertImage(['attribute_group_code_1', 'image_attribute_code_1_1-array']);
        await this.browser.assertImage('image-array');
    });

    it('Можно изменить подтверждаемый, но не подтвержденный атрибут через UI', async function () {
        await makeAttributeConfirmable(this.browser, attributes.boolean_attribute_code_0_0);

        await makeAttributeConfirmable(this.browser, attributes.image_attribute_code_1_1);

        await makeAttributeConfirmable(this.browser, specialAttributes.image);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.clickInto(['image-array', 'image-drag-0', 'delete-image']);
        await this.browser.clickInto([
            'attribute_group_code_1',
            'image_attribute_code_1_1-array',
            'image-drag-1',
            'delete-image'
        ]);

        await this.browser.assertImage(['attribute_group_code_1', 'boolean_attribute_code_0_0']);
        await this.browser.assertImage(['attribute_group_code_1', 'image_attribute_code_1_1-array']);
        await this.browser.assertImage('image-array');
    });

    it('Нельзя снять подтверждение подтвержденного атрибута', async function () {
        await makeAttributeConfirmable(this.browser, requiredAttributes.markCount);
        await setAttributeConfirmationValue({
            browser: this.browser,
            productIdentifier: 10000001,
            attributeId: requiredAttributes.markCount
        });

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        const tooltip = await this.browser.findByTestId([
            'basic-attributes',
            'markCount-name-labels',
            'confirmed-icon'
        ]);
        await tooltip.moveTo();

        await this.browser.waitUntilRendered();

        await this.browser.waitForTestIdSelectorDisabled(['confirmation-tooltip', 'confirmation-button']);
    });

    it('Чекбокс Показать только подтверждаемые и процент подтвержденности отсутствуют', async function () {
        await makeAttributeConfirmable(this.browser, requiredAttributes.markCount);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.assertImage('product-info-bar', {ignoreElements: makeDataTestIdSelector('left-bar')});
    });

    it('Для локализуемого атрибута в товаре Франции показываем статус подтвержденной локали', async function () {
        await makeAttributeConfirmable(this.browser, requiredAttributes.shortNameLoc);
        await setAttributeConfirmationValue({
            browser: this.browser,
            productIdentifier: 10000101,
            attributeId: requiredAttributes.shortNameLoc,
            langId: 2
        });

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000101), {region: 'fr'});

        await this.browser.assertImage(['basic-attributes', 'shortNameLoc-container']);

        const tooltip = await this.browser.findByTestId([
            'basic-attributes',
            'shortNameLoc-name-labels',
            'not-confirmed-icon'
        ]);
        await tooltip.moveTo();

        await this.browser.waitUntilRendered();

        await this.browser.assertImage('\\.ant-tooltip-inner', {removeShadows: true});
    });

    it('Отсутствует алерт подтвержденности при наличии неподтвержденных подтверждаемых атрибутов', async function () {
        await makeAttributeConfirmable(this.browser, requiredAttributes.shortNameLoc);
        await makeAttributeConfirmable(this.browser, requiredAttributes.markCount);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.assertImage('product-tabs', {
            ignoreElements: [makeDataTestIdSelector('product-info-bar'), makeDataTestIdSelector('product_view')]
        });
    });

    it('МП: Неподтвержденный атрибут можно изменить на подтвержденный', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        await makeAttributeConfirmable(this.browser, requiredAttributes.markCount);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        const tooltip = await this.browser.findByTestId([
            'basic-attributes',
            'markCount-name-labels',
            'not-confirmed-icon'
        ]);
        await tooltip.moveTo();

        await this.browser.waitUntilRendered();

        await this.browser.clickInto(['confirmation-tooltip', 'confirmation-button']);

        await this.browser.assertImage(['basic-attributes', 'markCount-name-labels']);
    });

    it('МП: Подтвержденный атрибут можно изменить на неподтвержденный', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        await makeAttributeConfirmable(this.browser, requiredAttributes.markCount);
        await setAttributeConfirmationValue({
            browser: this.browser,
            productIdentifier: 10000001,
            attributeId: requiredAttributes.markCount
        });

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        const tooltip = await this.browser.findByTestId([
            'basic-attributes',
            'markCount-name-labels',
            'confirmed-icon'
        ]);
        await tooltip.moveTo();

        await this.browser.waitUntilRendered();

        await this.browser.clickInto(['confirmation-tooltip', 'confirmation-button']);

        await this.browser.assertImage(['basic-attributes', 'markCount-name-labels']);
    });

    it('МП: Пустой неподтвержденный атрибут нельзя подтвердить', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        await makeAttributeConfirmable(this.browser, requiredAttributes.shortNameLoc);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.typeInto('shortNameLoc_ru', '', {clear: true});

        const tooltip = await this.browser.findByTestId([
            'basic-attributes',
            'shortNameLoc-name-labels',
            'not-confirmed-icon'
        ]);
        await tooltip.moveTo();

        await this.browser.waitUntilRendered();

        await this.browser.assertImage('\\.ant-tooltip-inner', {removeShadows: true});
    });

    it('МП: При удалении значения у подтвержденного атрибута, он становится неподтвержденным', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        await makeAttributeConfirmable(this.browser, attributes.number_attribute_code_3_0);
        await setAttributeConfirmationValue({
            browser: this.browser,
            productIdentifier: 10000001,
            attributeId: attributes.number_attribute_code_3_0
        });

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.typeInto('number_attribute_code_3_0', '', {clear: true});

        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom('query-state-spinner-spinning');

        await this.browser.waitForTestIdSelectorInDom([
            'attribute_group_code_2',
            'number_attribute_code_3_0-name-labels',
            'not-confirmed-icon'
        ]);
    });

    it('МП: локализуемые атрибуты подтверждаются отдельно для каждой локали, Франция', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        await makeAttributeConfirmable(this.browser, requiredAttributes.shortNameLoc);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000101), {region: 'fr'});

        const tooltip = await this.browser.findByTestId([
            'basic-attributes',
            'shortNameLoc-name-labels',
            'not-confirmed-icon'
        ]);
        await tooltip.moveTo();

        await this.browser.clickInto(['confirmation-tooltip', 'shortNameLoc_en', 'confirmation-button']);

        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom('query-state-spinner-spinning');

        await this.browser.assertImage(['basic-attributes', 'shortNameLoc-name-labels']);
    });

    it('МП: множественные атрибуты подтверждаются сразу для всех значений', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        await makeAttributeConfirmable(this.browser, requiredAttributes.barcode);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        const tooltip = await this.browser.findByTestId([
            'basic-attributes',
            'barcode-name-labels',
            'not-confirmed-icon'
        ]);
        await tooltip.moveTo();

        await this.browser.clickInto(['confirmation-tooltip', 'confirmation-button']);

        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom('query-state-spinner-spinning');

        await this.browser.assertImage(['basic-attributes', 'barcode-name-labels']);
    });

    it('МП: В шапке товара отображаются данные подтвержденности, число и проценты', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        await makeAttributeConfirmable(this.browser, requiredAttributes.barcode);
        await makeAttributeConfirmable(this.browser, requiredAttributes.markCount);
        await setAttributeConfirmationValue({
            browser: this.browser,
            productIdentifier: 10000001,
            attributeId: requiredAttributes.barcode
        });

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.assertImage(['product-info-bar', 'right-bar', 'product-confirmation-fullness']);
    });

    it('МП: Чекбокс "Показать только подтверждаемые", если есть подтверждаемые атрибуты', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        await makeAttributeConfirmable(this.browser, requiredAttributes.barcode);
        await makeAttributeConfirmable(this.browser, attributes.boolean_attribute_code_0_0);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.assertImage(['product-info-bar', 'right-bar'], {
            ignoreElements: makeDataTestIdSelector('product-confirmation-fullness')
        });
    });

    it('МП: Чекбокс "Показать только подтверждаемые", если нет неподтверждаемых атрибуты', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.assertImage(['product-info-bar', 'right-bar'], {
            ignoreElements: makeDataTestIdSelector('product-confirmation-fullness')
        });
    });

    it('МП: Подтверждение всех атрибутов', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        await makeAttributeConfirmable(this.browser, requiredAttributes.barcode);
        await makeAttributeConfirmable(this.browser, requiredAttributes.markCount);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.assertImage('confirmation-alert');

        await this.browser.clickInto(['confirmation-alert', 'confirm-all']);

        await this.browser.assertImage(['basic-attributes', 'markCount-name-labels']);
        await this.browser.assertImage(['basic-attributes', 'barcode-name-labels']);
    });

    it('МП: Подтверждение всех атрибутов, если есть незаполенные атрибуты', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        await makeAttributeConfirmable(this.browser, requiredAttributes.barcode);
        await makeAttributeConfirmable(this.browser, attributes.multiselect_attribute_code_2_0);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        const button = await this.browser.findByTestId(['confirmation-alert', 'confirm-all']);
        await button.moveTo();

        await this.browser.assertImage('confirmation-alert');
    });

    it('МП: Подтверждаемые неиспользуемые атрибуты не влияют на подтвержденность в шапке', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        const attributeCode = 'boolean_attribute_code_0_0';
        await createUnusedAttribute(this.browser, {attributeCode, infoModelCode: 'info_model_code_1_14'});
        await makeAttributeConfirmable(this.browser, attributes[attributeCode]);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.assertImage(['product-info-bar', 'right-bar', 'product-confirmation-fullness']);
    });

    // eslint-disable-next-line max-len
    it('МП: Подтверждаемые неиспользуемые атрибуты не появляются по нажатию на чекбокс "показать только подтверждаемые"', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        const attributeCode = 'boolean_attribute_code_0_0';
        await createUnusedAttribute(this.browser, {attributeCode, infoModelCode: 'info_model_code_1_14'});
        await makeAttributeConfirmable(this.browser, attributes[attributeCode]);
        await makeAttributeConfirmable(this.browser, requiredAttributes.barcode);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.clickInto(['product-info-bar', 'right-bar', 'confirmation-checkbox']);

        await this.browser.assertImage('product_view');
    });

    // eslint-disable-next-line max-len
    it('МП: Неподтвержденные неиспользуемые атрибуты не подтверждаются по нажатии на кнопку "подтвердить все атрибуты"', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        const attributeCode = 'boolean_attribute_code_0_0';
        await createUnusedAttribute(this.browser, {attributeCode, infoModelCode: 'info_model_code_1_14'});
        await makeAttributeConfirmable(this.browser, attributes[attributeCode]);
        await makeAttributeConfirmable(this.browser, requiredAttributes.barcode);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.clickInto(['confirmation-alert', 'confirm-all']);

        await this.browser.assertImage('unused-attributes', {removeShadows: true});
    });

    // eslint-disable-next-line max-len
    it('МП: Подтвержденность неиспользуемых атрибутов можно менять через ui', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        const attributeCode = 'boolean_attribute_code_0_0';
        await createUnusedAttribute(this.browser, {attributeCode, infoModelCode: 'info_model_code_1_14'});
        await makeAttributeConfirmable(this.browser, attributes[attributeCode]);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.execute(() => window.scrollTo({top: 1024}));

        const tooltip = await this.browser.findByTestId([
            'unused-attributes',
            'boolean_attribute_code_0_0-name-labels',
            'not-confirmed-icon'
        ]);
        await tooltip.moveTo();

        await this.browser.clickInto(['confirmation-tooltip', 'confirmation-button']);

        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom('query-state-spinner-spinning');

        await this.browser.assertImage('unused-attributes', {removeShadows: true});
    });

    it('МП: Нет алерта подтвержденности, если нет подтверждаемых атрибутов', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.assertImage('product-tabs', {
            ignoreElements: [makeDataTestIdSelector('product-info-bar'), makeDataTestIdSelector('product_view')]
        });
    });

    it('Одиночный атрибут типа "Видео" в товаре имеет кнопку "Выбрать файл"', async function () {
        await createAttribute(this, {type: AttributeType.VIDEO});
        await addAttributeToInfomodelByCode(this, {code: 'test_video_attribute_code'});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.assertImage([
            'without-group',
            'test_video_attribute_code-container',
            'test_video_attribute_code'
        ]);
    });

    it('Клик в "Отмена" при загруженном в одиночный атрибут файле удаляет его', async function () {
        await createAttribute(this, {type: AttributeType.VIDEO});
        await addAttributeToInfomodelByCode(this, {code: 'test_video_attribute_code'});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.uploadFileInto(
            ['without-group', 'test_video_attribute_code-container', 'test_video_attribute_code', 'file-input'],
            getFixturePath('correct-video-sample.mp4')
        );
        await this.browser.waitForTestIdSelectorInDom(['header-panel', 'cancel-button']);

        await this.browser.clickInto(['header-panel', 'cancel-button']);
        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button']);

        await this.browser.assertImage(['without-group', 'test_video_attribute_code-container']);
    });

    it('Множественный атрибут типа "Видео" в товаре отображается с окном для загрузки', async function () {
        await createAttribute(this, {type: AttributeType.VIDEO, max: 2});
        await addAttributeToInfomodelByCode(this, {code: 'test_video_attribute_code'});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.assertImage(['without-group', 'test_video_attribute_code-array']);
    });

    it('Клик в "Отмена" при загруженном во множественный атрибут файле удаляет его', async function () {
        await createAttribute(this, {type: AttributeType.VIDEO, max: 2});
        await addAttributeToInfomodelByCode(this, {code: 'test_video_attribute_code'});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.uploadFileInto(
            ['without-group', 'test_video_attribute_code-array', 'file-input'],
            getFixturePath('correct-video-sample.mp4')
        );
        await this.browser.waitForTestIdSelectorInDom(['header-panel', 'cancel-button']);

        await this.browser.clickInto(['header-panel', 'cancel-button']);
        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button']);

        await this.browser.assertImage(['without-group', 'test_video_attribute_code-array']);
    });

    it('Загрузить два видео во множественный видео-атрибут товара', async function () {
        await createAttribute(this, {type: AttributeType.VIDEO, max: 2});
        await addAttributeToInfomodelByCode(this, {code: 'test_video_attribute_code'});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.uploadFileInto(
            ['without-group', 'test_video_attribute_code-array', 'file-input'],
            getFixturePath('correct-video-sample.mp4')
        );
        await this.browser.uploadFileInto(
            ['without-group', 'test_video_attribute_code-array', 'file-input'],
            getFixturePath('correct-video-sample.mp4')
        );

        await this.browser.waitUntilRendered();

        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.assertImage(['without-group', 'test_video_attribute_code-array']);
    });

    it('Загрузить видео в одиночный атрибут и удалить', async function () {
        await createAttribute(this, {type: AttributeType.VIDEO});
        await addAttributeToInfomodelByCode(this, {code: 'test_video_attribute_code'});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.uploadFileInto(
            ['without-group', 'test_video_attribute_code-container', 'test_video_attribute_code', 'file-input'],
            getFixturePath('correct-video-sample.mp4')
        );
        await this.browser.waitForTestIdSelectorInDom(['header-panel', 'cancel-button']);

        await this.browser.clickInto(['without-group', 'test_video_attribute_code-container', 'delete-image']);

        await this.browser.assertImage('header-panel', {removeShadows: true});
    });

    it('Нельзя загрузить файл неправильного формата, выбирая файл в одиночном атрибуте', async function () {
        await createAttribute(this, {type: AttributeType.VIDEO});
        await addAttributeToInfomodelByCode(this, {code: 'test_video_attribute_code'});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.uploadFileInto(
            ['without-group', 'test_video_attribute_code-container', 'test_video_attribute_code', 'file-input'],
            getFixturePath('sample.gif')
        );

        await this.browser.assertImage(['without-group', 'test_video_attribute_code-container']);
    });

    it('Нельзя загрузить файл неправильного формата, выбирая файл в множественном атрибуте', async function () {
        await createAttribute(this, {type: AttributeType.VIDEO, max: 2});
        await addAttributeToInfomodelByCode(this, {code: 'test_video_attribute_code'});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001), {patchStyles: {enableNotifications: true}});

        await this.browser.uploadFileInto(
            ['without-group', 'test_video_attribute_code-array', 'file-input'],
            getFixturePath('sample.jpeg')
        );

        await this.browser.performScroll('\\#root');

        const video = await this.browser.findByTestId([
            'without-group',
            'test_video_attribute_code-array',
            'image-drag-0'
        ]);
        await video.scrollIntoView();
        await video.moveTo();
        await this.browser.waitForTestIdSelectorVisible('\\.ant-tooltip-inner');

        await this.browser.assertImage('\\.ant-tooltip-inner', {removeShadows: true});
    });

    // eslint-disable-next-line max-len
    it('При загрузке видео меньшего разрешения показываем сообщение об ошибке в карточке товара и в правом нижнем углу экрана', async function () {
        await createAttribute(this, {type: AttributeType.VIDEO});
        await addAttributeToInfomodelByCode(this, {code: 'test_video_attribute_code'});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001), {patchStyles: {enableNotifications: true}});

        await this.browser.uploadFileInto(
            ['without-group', 'test_video_attribute_code-container', 'test_video_attribute_code', 'file-input'],
            getFixturePath('wrong-dismensions-video.mp4')
        );
        await this.browser.waitForTestIdSelectorInDom('notification');

        await this.browser.assertImage([
            'without-group',
            'test_video_attribute_code-container',
            'test_video_attribute_code'
        ]);
        await this.browser.assertImage('notification', {removeShadows: true});
    });

    it('Нельзя загрузить видео тяжелее установленного ограничения', async function () {
        await createAttribute(this, {type: AttributeType.VIDEO});
        await addAttributeToInfomodelByCode(this, {code: 'test_video_attribute_code'});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001), {patchStyles: {enableNotifications: true}});

        await this.browser.uploadFileInto(
            ['without-group', 'test_video_attribute_code-container', 'test_video_attribute_code', 'file-input'],
            getFixturePath('massive-video.mp4')
        );

        await this.browser.assertImage([
            'without-group',
            'test_video_attribute_code-container',
            'test_video_attribute_code'
        ]);
    });

    // eslint-disable-next-line max-len
    it('Превью видео одиночного атрибута в товаре Израиля, при ховере появляется иконка удаления файла', async function () {
        await createAttribute(this, {type: AttributeType.VIDEO});
        await addAttributeToInfomodelByCode(this, {
            code: 'test_video_attribute_code',
            infomodelId: infoModels.il.info_model_code_4_14,
            region: 'il'
        });

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000151), {region: 'il'});

        await this.browser.uploadFileInto(
            ['without-group', 'test_video_attribute_code-container', 'test_video_attribute_code', 'file-input'],
            getFixturePath('correct-video-sample.mp4')
        );
        await this.browser.waitForTestIdSelectorInDom(['header-panel', 'cancel-button']);

        const video = await this.browser.findByTestId([
            'without-group',
            'test_video_attribute_code-container',
            'delete-image'
        ]);
        await video.scrollIntoView();
        await video.moveTo();

        await this.browser.assertImage([
            'without-group',
            'test_video_attribute_code-container',
            'test_video_attribute_code'
        ]);
    });

    it('Видео удаляется из одиночного атрибута', async function () {
        await createAttribute(this, {type: AttributeType.VIDEO});
        await addAttributeToInfomodelByCode(this, {
            code: 'test_video_attribute_code'
        });

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.uploadFileInto(
            ['without-group', 'test_video_attribute_code-container', 'test_video_attribute_code', 'file-input'],
            getFixturePath('correct-video-sample.mp4')
        );
        await this.browser.waitForTestIdSelectorInDom(['header-panel', 'cancel-button']);

        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.clickInto(['without-group', 'test_video_attribute_code-container', 'delete-image']);
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.assertImage(['without-group', 'test_video_attribute_code-container']);
    });

    it('Превью видео множественного атрибута в товаре России', async function () {
        await createAttribute(this, {type: AttributeType.VIDEO, max: 1});
        await addAttributeToInfomodelByCode(this, {code: 'test_video_attribute_code'});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.uploadFileInto(
            ['without-group', 'test_video_attribute_code-array', 'file-input'],
            getFixturePath('correct-video-sample.mp4')
        );
        await this.browser.waitForTestIdSelectorInDom(['header-panel', 'cancel-button']);

        await this.browser.assertImage(['without-group', 'test_video_attribute_code-array']);
    });

    it('Ховер видео множественного атрибута и его удаление', async function () {
        await createAttribute(this, {type: AttributeType.VIDEO, max: 1});
        await addAttributeToInfomodelByCode(this, {code: 'test_video_attribute_code'});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.uploadFileInto(
            ['without-group', 'test_video_attribute_code-array', 'file-input'],
            getFixturePath('correct-video-sample.mp4')
        );
        await this.browser.waitForTestIdSelectorInDom(['header-panel', 'cancel-button']);

        await this.browser.clickInto('submit-button', {waitRender: true});

        const video = await this.browser.findByTestId([
            'without-group',
            'test_video_attribute_code-array',
            'image-drag-0'
        ]);
        await video.scrollIntoView();
        await video.moveTo();

        await this.browser.assertImage(['without-group', 'test_video_attribute_code-array', 'image-drag-0']);

        await this.browser.clickInto([
            'without-group',
            'test_video_attribute_code-array',
            'image-drag-0',
            'delete-image'
        ]);

        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.assertImage(['without-group', 'test_video_attribute_code-array']);
    });

    // eslint-disable-next-line max-len
    it('Клик в "Посмотреть" одиночного видео-атрибута открывает попап для просмотра видео, клик в "Х" в попапе закрывает просмотр', async function () {
        await createAttribute(this, {type: AttributeType.VIDEO});
        await addAttributeToInfomodelByCode(this, {
            code: 'test_video_attribute_code'
        });

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.uploadFileInto(
            ['without-group', 'test_video_attribute_code-container', 'test_video_attribute_code', 'file-input'],
            getFixturePath('correct-video-sample.mp4')
        );
        await this.browser.waitForTestIdSelectorInDom(['header-panel', 'cancel-button']);

        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.clickInto(
            ['without-group', 'test_video_attribute_code-container', 'test_video_attribute_code', 'show-media'],
            {waitRender: true}
        );

        await this.browser.assertImage('image-view-modal', {removeShadows: true});
        await this.browser.waitForTestIdSelectorReadyToPlayVideo(['image-view-modal', 'video']);

        await this.browser.clickInto(['image-view-modal', '\\.ant-modal-close']);

        await this.browser.waitForTestIdSelectorNotInDom('image-view-modal');
    });

    // eslint-disable-next-line max-len
    it('Клик в файл множественного видео-атрибута открывает попап для просмотра видео, клик в "Закрыть" в попапе закрывает просмотр', async function () {
        await createAttribute(this, {type: AttributeType.VIDEO, max: 1});
        await addAttributeToInfomodelByCode(this, {code: 'test_video_attribute_code'});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.uploadFileInto(
            ['without-group', 'test_video_attribute_code-array', 'file-input'],
            getFixturePath('correct-video-sample.mp4')
        );
        await this.browser.waitForTestIdSelectorInDom(['header-panel', 'cancel-button']);

        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.clickInto(['without-group', 'test_video_attribute_code-array', 'image-drag-0']);

        await this.browser.assertImage('image-view-modal', {removeShadows: true});
        await this.browser.waitForTestIdSelectorReadyToPlayVideo(['image-view-modal', 'video']);

        await this.browser.clickInto(['image-view-modal', '\\.ant-modal-close']);

        await this.browser.waitForTestIdSelectorNotInDom('image-view-modal');
    });

    // eslint-disable-next-line max-len
    it('По ховеру на загруженное видео множественного неизменяемого видео-атрибута не появляется иконки удаления файла', async function () {
        await createAttribute(this, {type: AttributeType.VIDEO, max: 1, isImmutable: true});
        await addAttributeToInfomodelByCode(this, {code: 'test_video_attribute_code'});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.uploadFileInto(
            ['without-group', 'test_video_attribute_code-array', 'file-input'],
            getFixturePath('correct-video-sample.mp4')
        );
        await this.browser.waitForTestIdSelectorInDom(['header-panel', 'cancel-button']);

        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom('query-state-spinner-spinning');

        const video = await this.browser.findByTestId([
            'without-group',
            'test_video_attribute_code-array',
            'image-drag-0'
        ]);
        await video.scrollIntoView();
        await video.moveTo();

        await this.browser.waitForTestIdSelectorDisabled([
            'without-group',
            'test_video_attribute_code-array',
            'file-input'
        ]);

        await this.browser.assertImage(['without-group', 'test_video_attribute_code-array', 'image-drag-0']);
    });

    // eslint-disable-next-line max-len
    it('По ховеру на подтвержденное изображение множественного изображения-атрибута не появляется иконки удаления файла', async function () {
        const {id: attributeId} = await createAttribute(this, {
            type: AttributeType.IMAGE,
            max: 1,
            isImmutable: true,
            isConfirmable: true
        });
        await addAttributeToInfomodelByCode(this, {code: 'test_image_attribute_code'});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));

        await this.browser.uploadFileInto(
            ['test_image_attribute_code-array', 'file-input'],
            getFixturePath('sample.jpeg')
        );

        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom('query-state-spinner-spinning');

        await setAttributeConfirmationValue({
            browser: this.browser,
            productIdentifier: 10000001,
            attributeId
        });

        await this.browser.refresh();

        const image = await this.browser.findByTestId([
            'without-group',
            'test_image_attribute_code-array',
            'image-drag-0'
        ]);
        await image.scrollIntoView();
        await image.moveTo();

        await this.browser.waitForTestIdSelectorDisabled([
            'without-group',
            'test_image_attribute_code-array',
            'file-input'
        ]);

        await this.browser.assertImage(['without-group', 'test_image_attribute_code-array', 'image-drag-0']);
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
