import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {DbTable} from '@/src/entities/const';

import {chooseMasterCategory, createUnusedAttribute} from './util';

describe('Страница товаров', function () {
    it('Заголовок шапки страницы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        const defaultHeaderElement = await this.browser.findByTestId('default_panel');
        const innerText = await defaultHeaderElement.getText();
        expect(innerText).to.equal('Товары');
    });

    it('Общий вид таблицы товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('products-table');
    });

    it('Клик в строку таблицы открывает страницу товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto('^products-table-row', {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.PRODUCT('\\d')));
    });

    it('Настройка отображения столбцов', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCTS + '?columnIds=longNameLoc%2Cbarcode%2Cid%2Cstatus%2Cmaster_category'
        );
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('products-table');
    });

    it('Некорректный запрос (отсутствуют столбцы) показывает "не найдено"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS + '?columnIds=BLA_BLA_BLA');
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('base-layout');
    });

    it('Сtrl+клик в строку таблицы продуктов открывает страницу товара в новом табе', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto('^products-table-row', {button: 'middle', y: 10});

        const handles = await this.browser.getWindowHandles();
        expect(handles.length).to.equal(2);

        await this.browser.switchToWindow(handles[1]);
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.PRODUCT('\\d')));

        await this.browser.closeWindow();
        await this.browser.switchToWindow(handles[0]);
    });

    it('Скролл таблицы товаров при развернутом меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);

        await this.browser.performScroll(['products-table', 'table-container'], {
            direction: 'down',
            beforeIterationDelay: () => this.browser.waitForTestIdSelectorNotInDom('products_table__spinner'),
            afterIterationDelay: () => this.browser.waitUntilRendered()
        });

        await this.browser.assertImage('products-table');
        await this.browser.assertImage(['action-bar', 'pagination-info']);
    });

    it('Скролл таблицы товаров при свернутом меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {collapseSidebar: true});

        await this.browser.performScroll(['products-table', 'table-container'], {
            direction: 'down',
            beforeIterationDelay: () => this.browser.waitForTestIdSelectorNotInDom('products_table__spinner'),
            afterIterationDelay: () => this.browser.waitUntilRendered()
        });

        await this.browser.assertImage('products-table');
        await this.browser.assertImage(['action-bar', 'pagination-info']);
    });

    it('Перейти к странице создания товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto('create-button', {waitRender: true});
        await this.browser.clickInto(['action-bar', 'create-real'], {waitRender: true});

        await chooseMasterCategory(this.browser);
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true, waitNavigation: true});

        expect(await this.browser.getPath()).to.match(new RegExp(ROUTES.CLIENT.PRODUCTS_CREATE));
    });

    it('Фильтрация товаров по мастер-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'master_category'], {waitRender: true});

        await this.browser.clickInto(['category-picker', 'master_category_code_1_0', '\\[class*=switcher]'], {
            waitRender: true
        });
        await this.browser.clickInto(['category-picker', 'master_category_code_5_0', '\\[class*=switcher]'], {
            waitRender: true
        });

        await this.browser.clickInto(['category-picker', 'master_category_code_25_1', 'title'], {
            waitRender: true
        });
        await this.browser.clickInto('filter-item-master-category', {waitRender: true});

        await this.browser.assertImage(['products-table', '\\tbody']);
        await this.browser.assertImage('filter-list');
    });

    it('Фильтрация товаров по фронт-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'front_category'], {waitRender: true});

        await this.browser.clickInto(['category-picker', 'front_category_code_1_0', '\\[class*=switcher]'], {
            waitRender: true
        });

        await this.browser.clickInto(['category-picker', 'front_category_code_5_0', 'title'], {
            waitRender: true
        });
        await this.browser.clickInto('filter-item-front-category', {waitRender: true});

        await this.browser.assertImage(['products-table', '\\tbody']);
        await this.browser.assertImage('filter-list');
    });

    it('Фильтрация товаров по мастер-категории и фронт-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'master_category'], {waitRender: true});

        await this.browser.clickInto(['category-picker', 'master_category_code_1_0', '\\[class*=switcher]'], {
            waitRender: true
        });
        await this.browser.clickInto(['category-picker', 'master_category_code_5_0', '\\[class*=switcher]'], {
            waitRender: true
        });

        await this.browser.clickInto(['category-picker', 'master_category_code_25_0', 'title'], {
            waitRender: true
        });
        await this.browser.clickInto('filter-item-master-category', {waitRender: true});

        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'front_category'], {waitRender: true});

        await this.browser.clickInto(['category-picker', 'front_category_code_1_0', '\\[class*=switcher]'], {
            waitRender: true
        });

        await this.browser.clickInto(['category-picker', 'front_category_code_5_0', 'title'], {
            waitRender: true
        });
        await this.browser.clickInto('filter-item-front-category', {waitRender: true});

        await this.browser.assertImage(['products-table', '\\tbody']);
        await this.browser.assertImage('filter-list');
    });

    it('Поиск товара по фрагменту названия (Россия)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'ru', queryParams: {search: 'тор'}});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Поиск товара по первым цифрам id (Израиль)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'il', queryParams: {search: '1000015'}});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['products-table', '\\tbody']);
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'il', queryParams: {search: '151'}});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Поиск товара по первым цифрам баркода (Франция)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'fr', queryParams: {search: '9646074'}});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Поиск товара по первым цифрам второго баркода (Россия)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'fr', queryParams: {search: '4750961'}});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Поиск товара по названию среди отфильтрованных товаров (Великобритания)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'gb',
            queryParams: {search: 'sin', 'filters[barcode][rule]': 'contain', 'filters[barcode][values]': '666'}
        });
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Поиск МК по названию в модале "Создать товар"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto('create-button', {waitRender: true});
        await this.browser.clickInto(['action-bar', 'create-real'], {waitRender: true});
        await this.browser.clickInto(['hide-inactive']);
        await this.browser.typeInto(['parent-category-modal__tree-list', 'search_input'], 'стремящегося');
        await this.browser.assertImage('parent-category-modal__tree-list');
    });

    it('Параметры таблицы по умолчанию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);

        await this.browser.assertImage('filter-list');
        await this.browser.assertImage('action-bar');
    });

    it('Фильтрация товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto('add-filter');
        await this.browser.typeInto(['filters-menu', 'search'], 'nameloc');
        await this.browser.clickInto('longNameLoc');
        const SEARCH_WORD = 'а';
        await this.browser.typeInto('input_list_for_longNameLoc_0', SEARCH_WORD);

        await this.browser.assertImage('filter-item-string');
        const {search} = new URL(await this.browser.getUrl());
        expect(decodeURI(search)).to.equal('?filters[longNameLoc][rule]=contain&filters[longNameLoc][values]=а');
    });

    it('Добавление условия поиска товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto('add-filter');
        await this.browser.typeInto(['filters-menu', 'search'], 'nameloc');
        await this.browser.clickInto('longNameLoc');
        const SEARCH_WORD = 'а';
        await this.browser.typeInto('input_list_for_longNameLoc_0', SEARCH_WORD);
        await this.browser.clickInto('add-filter');

        await this.browser.assertImage('action-bar');
    });

    it('Клик в "Добавить условие" открывает окно выбора фильтров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto('add-filter');

        await this.browser.assertImage('filters-menu', {removeShadows: true});
    });

    it('Клик в "Сбросить" сбрасывает фильтры', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto('add-filter');
        await this.browser.typeInto('search', 'nameloc');
        await this.browser.clickInto('longNameLoc');
        const SEARCH_WORD = 'а';
        await this.browser.typeInto('input_list_for_longNameLoc_0', SEARCH_WORD);
        await this.browser.clickInto('add-filter');

        await this.browser.clickInto('clear-filters');

        await this.browser.assertImage('filter-list');
        await this.browser.assertImage('action-bar');
    });

    it('Клик в "Настройка таблицы" открывает окно настройки таблицы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto('settings-icon');

        await this.browser.assertImage('columns-menu', {removeShadows: true});
    });

    it('Выбрать МК-родителя в России', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'master_category'], {waitRender: true});
        await this.browser.clickInto(['hide-inactive']);

        await this.browser.clickInto(['category-picker', 'master_category_code_1_0'], {
            waitRender: true
        });
        await this.browser.clickInto(['category-picker', 'master_category_code_1_0', '\\[class*=switcher]'], {
            waitRender: true
        });
        await this.browser.clickInto(['category-picker', 'master_category_code_5_0', '\\[class*=switcher]'], {
            waitRender: true
        });
        await this.browser.assertImage('category-picker');
        await this.browser.assertImage('filter-item-master-category');
    });

    it('Исключить из выбора одну из МК-потомков в Великобритании', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'gb'});
        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'master_category'], {waitRender: true});
        await this.browser.clickInto(['hide-inactive']);

        await this.browser.clickInto(['category-picker', 'master_category_code_2_0'], {
            waitRender: true
        });
        await this.browser.clickInto(['category-picker', 'master_category_code_2_0', '\\[class*=switcher]'], {
            waitRender: true
        });
        await this.browser.clickInto(['category-picker', 'master_category_code_10_0', '\\[class*=switcher]'], {
            waitRender: true
        });
        await this.browser.clickInto(['category-picker', 'master_category_code_35_0'], {waitRender: true});
        await this.browser.assertImage('category-picker');
        await this.browser.assertImage('filter-item-master-category');
    });

    it('Выбрать ФК-родителя во Франции', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'fr'});
        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'front_category'], {waitRender: true});
        await this.browser.clickInto(['hide-inactive']);

        await this.browser.clickInto(['category-picker', 'front_category_code_3_0'], {
            waitRender: true
        });
        await this.browser.clickInto(['category-picker', 'front_category_code_3_0', '\\[class*=switcher]'], {
            waitRender: true
        });
        await this.browser.assertImage('category-picker');
        await this.browser.assertImage('filter-item-front-category');
    });

    it('Исключить из выбора одну из ФК-потомков в Израиле', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'il'});
        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'front_category'], {waitRender: true});
        await this.browser.clickInto(['hide-inactive']);

        await this.browser.clickInto(['category-picker', 'front_category_code_4_0'], {
            waitRender: true
        });
        await this.browser.clickInto(['category-picker', 'front_category_code_4_0', '\\[class*=switcher]'], {
            waitRender: true
        });
        await this.browser.clickInto(['category-picker', 'front_category_code_65_0'], {
            waitRender: true
        });
        await this.browser.assertImage('category-picker');
        await this.browser.assertImage('filter-item-front-category');
    });

    it('Выбрать одну МК-потомка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'master_category'], {waitRender: true});

        await this.browser.clickInto(['category-picker', 'master_category_code_1_0', '\\[class*=switcher]'], {
            waitRender: true
        });
        await this.browser.clickInto(['category-picker', 'master_category_code_5_0', '\\[class*=switcher]'], {
            waitRender: true
        });
        await this.browser.clickInto(['category-picker', 'master_category_code_25_0'], {waitRender: true});
        await this.browser.assertImage('category-picker');
        await this.browser.assertImage('filter-item-master-category');
    });

    it('Отображение множественных изображений в таблице товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto('table-settings-button');
        await this.browser.clickInto(['list', 'image_attribute_code_1_1'], {waitRender: true});
        await this.browser.clickInto('table-settings-button');
        await this.browser.assertImage('^products-table-row');
    });

    it('Смена языка данных на странице товаров (Франция)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'fr', dataLang: 'fr', uiLang: 'fr'});
        await this.browser.waitUntilRendered();
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('data-lang-select', {waitRender: true});
        await this.browser.clickInto(['data-lang-select_dropdown-menu', 'en'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Фильтр товаров по наличию заполненных неиспользуемых атрибутов', async function () {
        await createUnusedAttribute(this.browser);
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'unused'], {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Ставший используемым атрибут не попадает в фильтр по неиспользуемым', async function () {
        await createUnusedAttribute(this.browser);
        const infoModelId = 5;
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModelId));
        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['attributes-search'], {waitRender: true});
        await this.browser.clickInto(['attribute-select-virtual-list', 'image_attribute_code_1_0']);
        await this.browser.clickInto('im-user_attributes-table', {
            waitRender: true
        });
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'unused'], {waitRender: true});
        await this.browser.assertImage('products-table');
    });

    it('Фильтр по неиспользуемым атрибутам открывается по прямой ссылке. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'il',
            queryParams: {filters: {unused: {rule: 'not-null'}}}
        });
        await this.browser.assertImage('filter-list');
    });

    it('Фильтр по неиспользуемым атрибутам закрывается по крестику', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {filters: {unused: {rule: 'not-null'}}}
        });
        await this.browser.clickInto(['filter-list', 'filter-item-unused', 'delete'], {waitRender: true});
        await this.browser.assertImage('filter-list');
    });

    it('Фильтр по неиспользуемым атрибутам с фильтром по имени товара. Франция', async function () {
        const attributeCode = 'text_attribute_code_6_2_loc';
        await createUnusedAttribute(this.browser, {
            region: 'fr',
            infoModelCode: 'info_model_code_3_1',
            attributeCode
        });
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'fr'});
        await this.browser.typeInto(['filter-list', 'search'], 'Repellendus non');

        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'unused'], {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Фильтр по конкретному неиспользуемому атрибуту', async function () {
        const attributeCode = 'text_attribute_code_6_2_loc';
        await createUnusedAttribute(this.browser, {
            region: 'fr',
            infoModelCode: 'info_model_code_3_1',
            attributeCode
        });

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'fr'
        });
        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});
        await this.browser.typeInto(['filters-menu', 'search'], attributeCode);
        await this.browser.clickInto(['filters-menu', attributeCode], {waitForClickable: true, waitRender: true});

        await this.browser.clickInto(['filter-list', 'select']);
        await this.browser.clickInto(['select_dropdown-menu', 'unused']);
        await this.browser.clickInto('header-panel');
        await this.browser.assertImage('base-layout');
    });

    // eslint-disable-next-line max-len
    it('Фильтр по конкретному неиспользуемому атрибуту открывается по прямой ссылке. Великобритания', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'gb',
            queryParams: {filters: {boolean_attribute_code_0_1: {rule: 'unused'}}}
        });
        await this.browser.assertImage('filter-list');
    });

    it('Фильтр по конкретному неиспользуемому атрибуту закрывается по крестику. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'il',
            queryParams: {filters: {boolean_attribute_code_0_0: {rule: 'not-null'}}}
        });
        await this.browser.clickInto(['filter-list', 'filter-item-boolean', 'delete'], {waitRender: true});
        await this.browser.assertImage('filter-list');
    });

    it('Фильтр по false-атрибуту', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {columnIds: ['image', 'longNameLoc', 'boolean_attribute_code_0_0'].join()}
        });
        await this.browser.clickInto('add-filter', {waitRender: true});
        await this.browser.clickInto('boolean_attribute_code_0_0', {waitRender: true});
        await this.browser.clickInto(['boolean-picker', 'false']);

        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Фильтр по true-атрибуту', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {columnIds: ['image', 'longNameLoc', 'boolean_attribute_code_0_0'].join()}
        });
        await this.browser.clickInto('add-filter', {waitRender: true});
        await this.browser.clickInto('boolean_attribute_code_0_0', {waitRender: true});
        await this.browser.clickInto(['boolean-picker', 'true']);

        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Фильтр по пустому атрибуту', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {columnIds: ['image', 'longNameLoc', 'boolean_attribute_code_0_0'].join()}
        });
        await this.browser.clickInto('add-filter', {waitRender: true});
        await this.browser.clickInto('boolean_attribute_code_0_0', {waitRender: true});
        await this.browser.clickInto(['boolean-picker', 'null']);

        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Отображение в таблице пустого атрибута', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.clickInto('boolean_attribute_code_0_0_unset');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {search: '10000001', columnIds: ['image', 'longNameLoc', 'boolean_attribute_code_0_0'].join()}
        });
        await this.browser.assertImage('products-table');
    });

    it('Клик в "Создать товар" открывает окно выбора МК товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);

        await this.browser.clickInto('create-button', {waitRender: true});
        await this.browser.clickInto(['action-bar', 'create-real'], {waitRender: true});
        await this.browser.assertImage('parent-category-modal', {removeShadows: true});
    });

    it('Клик в "Отмена" в окне "Создать товара" закрывает его', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);

        await this.browser.clickInto('create-button', {waitRender: true});
        await this.browser.clickInto(['action-bar', 'create-real'], {waitRender: true});
        await this.browser.clickInto('parent-category-modal__cancel-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorNotVisible('parent_category_modal');
    });

    it('Сложный поиск', async function () {
        const baseId = 10000011;
        const values = new Array(40)
            .fill(baseId)
            .map((value, i) => value + i)
            .join();
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {filters: {id: {rule: 'equal', values}}}
        });
        await this.browser.typeInto(['filter-list', 'search'], 'бы', {blur: true});
        await this.browser.assertImage('base-layout-content');
    });

    it('Фильтр товаров по id и введенным цифрам', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {filters: {id: {rule: 'equal', values: [10000001, 10000002, 10000003].join()}}}
        });
        await this.browser.typeInto(['filter-list', 'search'], '10000003', {blur: true});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('В фильтрации по МК товара отображается статус неактивных категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);

        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'master_category'], {waitRender: true});
        await this.browser.clickInto('hide-inactive');

        await this.browser.assertImage('master_category_code_1_3');
    });

    it('В фильтрации по ФК товара отображается статус неактивных категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);

        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'front_category'], {waitRender: true});
        await this.browser.clickInto('hide-inactive');

        await this.browser.performScroll(['\\.ant-tree-list-holder']);

        await this.browser.assertImage('front_category_code_1_18');
    });

    it('В выборе МК при создании товара отображется статус неактивных категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);

        await this.browser.clickInto('create-button', {waitRender: true});
        await this.browser.clickInto(['action-bar', 'create-real'], {waitRender: true});
        await this.browser.clickInto('hide-inactive');

        await this.browser.assertImage('row_master_category_code_1_4');
    });

    it('Показ неактивных категорий в фильтрации МК товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);

        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'master_category'], {waitRender: true});

        await this.browser.assertImage('category-picker');

        await this.browser.clickInto(['category-picker', 'hide-inactive'], {waitRender: true});

        await this.browser.assertImage('category-picker');
    });

    it('Показ неактивных категорий в фильтрации ФК товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);

        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'front_category'], {waitRender: true});

        await this.browser.performScroll(['\\.ant-tree-list-holder']);
        await this.browser.assertImage('category-picker');

        await this.browser.clickInto(['category-picker', 'hide-inactive'], {waitRender: true});

        await this.browser.performScroll(['\\.ant-tree-list-holder']);
        await this.browser.assertImage('category-picker');
    });

    it('Показ неактивных МК при создании товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);

        await this.browser.clickInto('create-button', {waitRender: true});
        await this.browser.clickInto(['action-bar', 'create-real'], {waitRender: true});

        await this.browser.assertImage('parent-category-modal__tree-list');

        await this.browser.clickInto(['parent-category-modal', 'hide-inactive'], {waitRender: true});

        await this.browser.assertImage('parent-category-modal__tree-list');
    });

    it('Отображение типа номенклатуры в таблице', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {columnIds: ['image', 'longNameLoc', 'nomenclatureType'].join()}
        });

        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Фильтр по типу номенклатуры', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                filters: {nomenclatureType: {values: 'product'}},
                columnIds: ['image', 'longNameLoc', 'nomenclatureType'].join()
            }
        });

        await this.browser.assertImage(['products-table', '\\tbody']);

        await this.browser.clickInto('filter-item-select', {waitRender: true});
        await this.browser.clickInto(['select_option_nomenclatureType', 'product']);
        await this.browser.clickInto(['select_option_nomenclatureType', 'sample'], {waitRender: true});
        await this.browser.clickInto('filter-item-select');

        await this.browser.assertImage(['products-table', '\\tbody']);

        await this.browser.clickInto('filter-item-select', {waitRender: true});
        await this.browser.clickInto(['select_option_nomenclatureType', 'sample']);
        await this.browser.clickInto(['select_option_nomenclatureType', 'consumable'], {waitRender: true});
        await this.browser.clickInto('filter-item-select');

        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Общая локализация в настройках таблицы товаров России', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                columnIds: ['longNameLoc', 'barcode', 'info_model'].join()
            }
        });
        await this.browser.clickInto('table-settings-button');
        await this.browser.clickInto('localization');
        await this.browser.assertImage('columns-menu', {removeShadows: true});

        await this.browser.clickInto('table-settings-button');

        await this.browser.assertImage(['table-container', '\\thead']);
        await this.browser.assertImage('products-table-row_10000001');
    });

    it('Общая локализация и локализация (страна) в настройках таблицы товаров Франции', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'fr',
            queryParams: {
                columnIds: ['longNameLoc', 'barcode', 'info_model'].join()
            }
        });
        await this.browser.clickInto('table-settings-button');
        await this.browser.clickInto('localization_fr');

        await this.browser.assertImage('columns-menu', {removeShadows: true});
    });

    it('Локализация (страна) по французскому языку в таблице товаров Франции', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'fr'});
        await this.browser.clickInto('table-settings-button');
        await this.browser.clickInto('updated_at');
        await this.browser.clickInto('localization_fr');
        await this.browser.clickInto('table-settings-button');

        await this.browser.assertImage(['table-container', '\\thead']);
        await this.browser.assertImage('products-table-row_10000101');
    });

    it('Локализация (страна) по двум языкам в таблице товаров Израиля', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'il',
            queryParams: {
                columnIds: ['longNameLoc', 'barcode', 'info_model', 'localization_he', 'localization_en'].join()
            }
        });

        await this.browser.assertImage(['table-container', '\\thead']);
        await this.browser.assertImage('products-table-row_10000151');
    });

    it('Фильтры таблицы товаров Франции', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'fr'});

        await this.browser.clickInto('add-filter');
        await this.browser.assertImage('filters-menu', {removeShadows: true});
    });

    it('Фильтрация по общей наполненности товаров Великобритании (равно)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'gb',
            queryParams: {
                filters: {
                    localization: {
                        values: '0',
                        rule: 'equal'
                    }
                },
                columnIds: ['image', 'longNameLoc', 'localization'].join()
            }
        });

        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Фильтрация по общей наполненности товаров Франции (не равно)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'fr',
            queryParams: {columnIds: ['image', 'longNameLoc', 'localization'].join()}
        });

        await this.browser.clickInto('add-filter');
        await this.browser.clickInto(['filters-menu', 'localization']);
        await this.browser.clickInto(['filter-list', 'select']);
        await this.browser.clickInto(['select_dropdown-menu', 'not-equal']);
        await this.browser.typeInto(['filter-list', 'input_list_for_localization_0'], '100');
        await this.browser.clickInto(['filter-list', 'filter-item-progress']);

        await this.browser.waitUntilRendered();

        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Фильтрация по общей наполненности товаров Израиля (диапазон)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'il',
            queryParams: {
                filters: {
                    localization: {
                        values: [0, 50].join(),
                        rule: 'range'
                    }
                },
                columnIds: ['image', 'longNameLoc', 'localization'].join()
            }
        });

        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Фильтрация по наполненности для локали иврит товаров Израиля (равно)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'il',
            queryParams: {
                filters: {
                    localization_he: {
                        values: '0',
                        rule: 'equal'
                    }
                },
                columnIds: ['image', 'longNameLoc', 'localization_he'].join()
            }
        });

        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Фильтрация по наполненности для английской локали товаров Израиля (не равно)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'il',
            queryParams: {
                filters: {
                    localization_en: {
                        values: '100',
                        rule: 'not-equal'
                    }
                },
                columnIds: ['image', 'longNameLoc', 'localization_en'].join()
            }
        });

        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Фильтрация по наполненности для французской локали товаров Франции (диапазон)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'fr',
            queryParams: {
                columnIds: ['image', 'longNameLoc', 'localization_fr'].join()
            }
        });

        await this.browser.clickInto('add-filter');
        await this.browser.clickInto(['filters-menu', 'localization_fr']);
        await this.browser.clickInto(['filter-list', 'select']);
        await this.browser.clickInto(['select_dropdown-menu', 'range']);
        await this.browser.typeInto(['filter-list', 'min'], '25');
        await this.browser.typeInto(['filter-list', 'max'], '75');

        await this.browser.waitUntilRendered();

        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Фильтр по кол-ву элементов в массиве для string', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                filters: {string_attribute_code_5_1: {rule: 'array-length', values: ',3'}},
                columnIds: ['image', 'longNameLoc', 'string_attribute_code_5_1'].join()
            }
        });

        await this.browser.assertImage(['products-table', '\\tbody']);

        await this.browser.clickInto('filter-item-string', {waitRender: true});
        await this.browser.typeInto(['string-number-picker-interval', 'min'], '2');
        await this.browser.waitUntilRendered();

        await this.browser.assertImage(['products-table', '\\tbody']);
        await this.browser.assertImage('filter-item-string');
    });

    it('Фильтр по кол-ву элементов в массиве для text', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                filters: {text_attribute_code_6_1: {rule: 'array-length', values: ',3'}},
                columnIds: ['image', 'longNameLoc', 'text_attribute_code_6_1'].join()
            }
        });

        await this.browser.assertImage(['products-table', '\\tbody']);

        await this.browser.clickInto('filter-item-string', {waitRender: true});
        await this.browser.typeInto(['string-number-picker-interval', 'min'], '2');
        await this.browser.waitUntilRendered();

        await this.browser.assertImage(['products-table', '\\tbody']);
        await this.browser.assertImage('filter-item-string');
    });

    it('Фильтр по кол-ву элементов в массиве для image', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                filters: {image_attribute_code_1_1: {rule: 'array-length', values: '2,'}},
                columnIds: ['image', 'longNameLoc', 'image_attribute_code_1_1'].join()
            }
        });

        await this.browser.assertImage(['products-table', '\\tbody']);
        await this.browser.assertImage('filter-item-image');
    });

    it('Отображение выпадашки действий в фильтре массива image', async function () {
        const attributeCode = 'image_attribute_code_1_1';

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});

        await this.browser.typeInto(['filters-menu', 'search'], attributeCode);
        await this.browser.clickInto(['filters-menu', attributeCode], {waitForClickable: true, waitRender: true});
        await this.browser.assertImage(['string-number-picker'], {removeShadows: true});

        await this.browser.clickInto(['string-number-picker', 'select'], {waitForClickable: true, waitRender: true});
        await this.browser.assertImage(['select_dropdown-menu'], {removeShadows: true});

        await this.browser.clickInto(['select_dropdown-menu', 'array-length'], {
            waitForClickable: true,
            waitRender: true
        });
        await this.browser.assertImage(['string-number-picker'], {removeShadows: true});
    });

    it('Отображение выпадашки действий в фильтре image', async function () {
        const attributeCode = 'image_attribute_code_1_0';

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto(['action-bar', 'add-filter'], {waitRender: true});

        await this.browser.typeInto(['filters-menu', 'search'], attributeCode);
        await this.browser.clickInto(['filters-menu', attributeCode], {waitForClickable: true, waitRender: true});

        await this.browser.assertImage('select-option-picker', {removeShadows: true});
    });

    it('Фильтр товаров по пустому и обязательному атрибуту (обязательный и не заполнен)', async function () {
        const attributeCode = 'image_attribute_code_1_0';
        const productIdentifier = 10000035;
        const columnIds = ['image', 'longNameLoc', 'info_model', attributeCode].join();

        // Делаем скриншот с проверяемым товаром, что он есть
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                filters: {id: {rule: 'equal', values: productIdentifier}},
                columnIds
            }
        });

        await this.browser.assertImage(['products-table', '\\tbody']);

        // Удаляем значение обязательного атрибута в инфо модели - 100% гарантия, что нет значения
        await this.browser.executeSql(
            `
            DELETE FROM ${DbTable.PRODUCT_ATTRIBUTE_VALUE}
            WHERE id IN (
                SELECT pav.id FROM ${DbTable.PRODUCT_ATTRIBUTE_VALUE} pav
                INNER JOIN ${DbTable.ATTRIBUTE} attr ON attr.id = pav.attribute_id
                INNER JOIN ${DbTable.PRODUCT} p ON p.id = pav.product_id
                WHERE attr.code = '${attributeCode}' AND p.identifier = ${productIdentifier}
            )
            `
        );

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                filters: {
                    id: {rule: 'equal', values: productIdentifier},
                    [attributeCode]: {rule: 'important-and-null'}
                },
                columnIds
            }
        });

        await this.browser.assertImage(['products-table', '\\tbody']);

        const url = new URL(await this.browser.getUrl());
        const query = decodeURIComponent(url.searchParams.toString());

        expect(query).to.match(new RegExp(`filters\\[id\\]\\[values\\]=${productIdentifier}`));
        expect(query).to.match(new RegExp(`filters\\[${attributeCode}\\]\\[rule\\]=important-and-null`));

        await this.browser.assertImage('filter-item-image', {removeShadows: true});

        await this.browser.clickInto('filter-item-image', {waitForClickable: true, waitRender: true});
        await this.browser.assertImage('select-option-picker', {removeShadows: true});
    });

    it('Фильтр товаров по пустому и обязательному атрибуту (обязательный и заполнен)', async function () {
        const attributeCode = 'image_attribute_code_1_0';
        const productIdentifier = 10000035;
        const columnIds = ['image', 'longNameLoc', 'info_model', attributeCode].join();

        // Делаем скриншот с проверяемым товаром, что он есть
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                filters: {id: {rule: 'equal', values: productIdentifier}},
                columnIds
            }
        });

        await this.browser.assertImage(['products-table', '\\tbody']);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                filters: {
                    id: {rule: 'equal', values: productIdentifier},
                    [attributeCode]: {rule: 'important-and-null'}
                },
                columnIds
            }
        });

        await this.browser.assertImage(['products-table', '\\tbody']);

        const url = new URL(await this.browser.getUrl());
        const query = decodeURIComponent(url.searchParams.toString());

        expect(query).to.match(new RegExp(`filters\\[id\\]\\[values\\]=${productIdentifier}`));
        expect(query).to.match(new RegExp(`filters\\[${attributeCode}\\]\\[rule\\]=important-and-null`));
    });

    it('Фильтр товаров по пустому и обязательному атрибуту (дополнительный и пустой), Израиль', async function () {
        const attributeCode = 'boolean_attribute_code_0_1';
        const productIdentifier = 10000151;
        const columnIds = ['image', 'longNameLoc', 'info_model', attributeCode].join();

        // Делаем скриншот с проверяемым товаров, что он есть
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'il',
            queryParams: {
                filters: {id: {rule: 'equal', values: productIdentifier}},
                columnIds
            }
        });

        await this.browser.assertImage(['products-table', '\\tbody']);

        // Удаляем значение атрибута у товара - 100% гарантия, что нет значения
        await this.browser.executeSql(
            `
            DELETE FROM ${DbTable.PRODUCT_ATTRIBUTE_VALUE}
            WHERE id IN (
                SELECT pav.id FROM ${DbTable.PRODUCT_ATTRIBUTE_VALUE} pav
                INNER JOIN ${DbTable.ATTRIBUTE} attr ON attr.id = pav.attribute_id
                INNER JOIN ${DbTable.PRODUCT} p ON p.id = pav.product_id
                WHERE attr.code = '${attributeCode}' AND p.identifier = ${productIdentifier}
            )
            `
        );

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            region: 'il',
            queryParams: {
                filters: {
                    id: {rule: 'equal', values: productIdentifier},
                    [attributeCode]: {rule: 'important-and-null'}
                },
                columnIds
            }
        });

        await this.browser.assertImage(['products-table', '\\tbody']);

        const url = new URL(await this.browser.getUrl());
        const query = decodeURIComponent(url.searchParams.toString());

        expect(query).to.match(new RegExp(`filters\\[id\\]\\[values\\]=${productIdentifier}`));
        expect(query).to.match(new RegExp(`filters\\[${attributeCode}\\]\\[rule\\]=important-and-null`));
    });

    it('При повторном открытии дропдауна выбора фильтров фокус на поиске сохраняется', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto('add-filter');
        await this.browser.clickInto('add-filter');
        await this.browser.clickInto('add-filter');

        await this.browser.assertImage('filters-menu', {removeShadows: true});
    });

    it('Свернуть и развернуть меню на странице Товаров России', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto('sidebar-switcher', {waitRender: true});
        await this.browser.assertImage();
        await this.browser.clickInto('sidebar-switcher', {waitRender: true});
        await this.browser.assertImage();
    });

    it('Добавить в таблицу товаров колонки, свернуть и развернуть боковое меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);

        await this.browser.clickInto('table-settings-button');
        await this.browser.clickInto('master_category');
        await this.browser.clickInto('front_category');
        await this.browser.clickInto('table-settings-button');

        await this.browser.clickInto('sidebar-switcher', {waitRender: true});
        await this.browser.assertImage();
        await this.browser.clickInto('sidebar-switcher', {waitRender: true});
        await this.browser.assertImage();
    });
});
