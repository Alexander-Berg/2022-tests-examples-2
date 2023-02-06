import crypto from 'crypto';
import getEntityIdFromUrl from 'tests/e2e/helper/get-entity-id-from-url';
import {infoModels, masterCategories} from 'tests/e2e/seed-db-map';
import createImageFile from 'tests/e2e/utils/create-image-file';
import getFixturePath from 'tests/e2e/utils/fixture';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

const IDENTIFIER = '10000001';

describe('История изменений товара', function () {
    async function assertListItemImageStretched(ctx: Hermione.TestContext, selector: string) {
        const container = await ctx.browser.findByTestId('history-of-changes_list');

        await container.execute(
            (container, selector) => {
                if (container instanceof HTMLElement) {
                    container.style.removeProperty('height');
                    [...container.querySelectorAll('[data-testid^=list-item')]
                        .filter((it): it is HTMLElement => it instanceof HTMLElement)
                        .filter((it) => it.dataset.testid !== selector)
                        .forEach((it) => it.style.setProperty('display', 'none', 'important'));
                }
            },
            container,
            selector
        );

        await ctx.browser.assertImage(['history-of-changes_list', selector], {stretch: true});
    }

    it('Отображение страницы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER));
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage('base-layout');
    });

    it('Наличие автора и даты изменения', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER));
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', '^list-item', 'caption']);
    });

    it('Запись о создании товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER));
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await assertListItemImageStretched(this, 'list-item-2');
    });

    it('Запись о добавлении фронт-категории на товар, у которого уже была фронт-категория', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER), {clearLocalStorage: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('show-assigned');
        await this.browser.clickInto(['show-assigned', '\\input'], {waitRender: true});
        await this.browser.clickInto(['product_fc_row_front_category_code_1_0', 'expand_icon'], {waitRender: true});
        await this.browser.clickInto(['product_fc_row_front_category_code_5_3', 'checkbox'], {waitRender: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись об удалении фронт-категории с товара, у которого останется еще одна фронт-категория', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER), {clearLocalStorage: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories', {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('show-assigned');
        await this.browser.clickInto(['show-assigned', '\\input'], {waitRender: true});
        await this.browser.clickInto(['product_fc_row_front_category_code_1_0', 'expand_icon'], {waitRender: true});
        await this.browser.clickInto(['product_fc_row_front_category_code_5_0', 'checkbox'], {waitRender: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись о смене мастер-категории без изменения инфомодели', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY, {clearLocalStorage: true});

        // Создадим такую МК
        await this.browser.clickInto('parent-category-modal__input', {waitRender: true});
        await this.browser.clickInto(['row_master_category_code_1_0', '\\[class*=switcher]']);
        await this.browser.clickInto(['row_master_category_code_5_0', 'title']);
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
        await this.browser.clickInto('info-model-select', {waitRender: true});
        await this.browser.typeInto(['info-model-select', '\\input'], 'По восхваляющих великие');
        await this.browser.clickInto('im_node_compatible_info_model_code_1_14', {waitRender: true});
        await this.browser.typeInto('code', 'compatible_mc_code');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER), {clearLocalStorage: true});
        await this.browser.clickInto(['basic-attributes', 'parent-category-modal__input'], {waitRender: true});
        await this.browser.clickInto(['row_compatible_mc_code', 'title'], {waitRender: true});

        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись о смене мастер-категории с изменением инфомодели', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER), {clearLocalStorage: true});
        await this.browser.clickInto(['basic-attributes', 'parent-category-modal__input'], {waitRender: true});
        await this.browser.clickInto(['hide-inactive']);
        await this.browser.clickInto(['row_master_category_code_5_1', '\\[class*=switcher]'], {waitRender: true});
        await this.browser.clickInto(['row_master_category_code_26_0', 'title'], {waitRender: true});

        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись о смене статуса', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER), {clearLocalStorage: true});
        await this.browser.clickInto(['status', 'disabled']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    // eslint-disable-next-line max-len
    it('Запись об удалении фронт-категории через импорт, чтобы у товара не осталось фронт-категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(['import-upload', 'file-input'], getFixturePath('import-remove-all-fc.xlsx'));
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('import-success-alert', {timeout: 30_000});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER), {clearLocalStorage: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись об удалении значений атрибутов всех типов, кроме изображения', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-remove-all-attrs.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('import-success-alert', {timeout: 30_000});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER), {clearLocalStorage: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await assertListItemImageStretched(this, 'list-item-2');
    });

    it('Запись об удалении изображения', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER), {clearLocalStorage: true});
        await this.browser.clickInto(['product-image', 'delete-image'], {waitRender: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись об изменении локализуемого атрибута, Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT('10000101'), {clearLocalStorage: true, region: 'fr'});

        await this.browser.typeInto('longNameLoc_en', 'Foo bar baz');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись об изменении множественного атрибута через балковые действия', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto([`products-table-row_${IDENTIFIER}`, 'checkbox'], {waitRender: true});
        await this.browser.clickInto(['products-bottom-panel', 'bulk-edit'], {waitRender: true});
        await this.browser.clickInto('change-attributes-values', {waitRender: true});

        await this.browser.clickInto('add-attribute', {waitRender: true});
        await this.browser.typeInto(['select-user-attributes', 'search'], 'number_attribute_code_3_1');
        await this.browser.clickInto(['select-user-attributes', 'number_attribute_code_3_1'], {waitRender: true});
        await this.browser.clickInto(['select-user-attributes', 'confirm-select'], {waitRender: true});

        await this.browser.clickInto('add_new_number_attribute_code_3_1', {waitRender: true});
        await this.browser.typeInto('number_attribute_code_3_1__0', '666');

        await this.browser.clickInto('add_new_number_attribute_code_3_1', {waitRender: true});
        await this.browser.typeInto('number_attribute_code_3_1__1', '777');

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('import-info-update');

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert', {timeout: 30_000});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER), {clearLocalStorage: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Поиск', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER), {clearLocalStorage: true});
        await this.browser.clickInto('add_new_barcode', {waitRender: true});
        await this.browser.typeInto('barcode__2', 'test_bar_code_666');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await this.browser.typeInto('history-of-changes_search', 'barcode');
        await this.browser.waitUntilRendered();

        await this.browser.assertImage('history-of-changes_list');
    });

    it('Клик в миниатюру изображения открывает модал просмотра изображения', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER), {clearLocalStorage: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.typeInto('history-of-changes_search', 'фото товара');

        await this.browser.clickInto(
            ['history-of-changes_list', 'list-item-2', 'table-row_image', 'new-value', 'thumbnail'],
            {waitRender: true, waitForClickable: true}
        );

        await this.browser.waitForTestIdSelectorInDom('image-view-modal');
        await this.browser.assertImage('image-view-modal', {removeShadows: true});
    });

    it('Запись о замене значений атрибутов всех типов', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-replace-all-attrs.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('import-success-alert', {timeout: 30_000});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER), {clearLocalStorage: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await assertListItemImageStretched(this, 'list-item-2');
    });

    it('Запись о замене изображения', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER), {clearLocalStorage: true});
        await this.browser.clickInto(['product-image', 'delete-image'], {waitRender: true});
        await this.browser.uploadFileInto(['product-image', 'file-input'], createImageFile('test_product_image.png'));
        await this.browser.waitForTestIdSelectorInDom(['product-image', 'thumbnail', 'image']);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Удаленная из системы бывшая МК', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.typeInto('code', 'category_code');
        await this.browser.typeInto(['info-model-select', '\\input'], 'По восхваляющих великие');
        await this.browser.clickInto('im_node_compatible_info_model_code_1_14');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        const categoryUrl = await this.browser.getUrl();
        const categoryId = getEntityIdFromUrl(categoryUrl);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER));
        await this.browser.clickInto(['basic-attributes', 'parent-category-modal__input'], {waitRender: true});
        await this.browser.clickInto(['row_category_code', 'title'], {waitRender: true});
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.clickInto(['basic-attributes', 'parent-category-modal__input'], {waitRender: true});
        await this.browser.typeInto(['parent-category-modal__root', 'search_input'], 'Несло бы иной');
        await this.browser.clickInto(['row_master_category_code_25_0', 'title'], {waitRender: true});
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(categoryId));
        await this.browser.clickInto(['status', 'disabled']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.clickInto(['header-panel', 'delete-button'], {waitRender: true});
        await this.browser.clickInto('confirmation-modal__ok-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER));
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await assertListItemImageStretched(this, 'list-item-3');
    });

    it('Удаленная бывшая ИМ в бывшей МК', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_INFOMODEL);
        await this.browser.typeInto('code', 'info_model_code');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        const infoModelUrl = await this.browser.getUrl();
        const infoModeId = getEntityIdFromUrl(infoModelUrl);

        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.typeInto('code', 'category_code');
        await this.browser.clickInto('info-model-select');
        await this.browser.clickInto(['info-model-select_dropdown-menu', 'im_node_compatible_info_model_code']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        const categoryUrl = await this.browser.getUrl();
        const categoryId = getEntityIdFromUrl(categoryUrl);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER));
        await this.browser.clickInto(['basic-attributes', 'parent-category-modal__input'], {waitRender: true});
        await this.browser.clickInto(['row_category_code', 'title'], {waitRender: true});
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.clickInto(['basic-attributes', 'parent-category-modal__input'], {waitRender: true});
        await this.browser.typeInto(['parent-category-modal__root', 'search_input'], 'Несло бы иной');
        await this.browser.clickInto(['row_master_category_code_25_0', 'title'], {waitRender: true});
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(categoryId));
        await this.browser.clickInto('info-model-select');
        await this.browser.clickInto(['info-model-select_dropdown-menu', 'im_node_compatible_root']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModeId));
        await this.browser.clickInto(['header-panel', 'delete-button'], {waitRender: true});
        await this.browser.clickInto('confirmation-modal__ok-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER));
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await assertListItemImageStretched(this, 'list-item-3');
    });

    it('Удаленная из системы бывшая ФК', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.clickInto('active_label');
        await this.browser.typeInto('code', 'test_category_code');
        await this.browser.typeInto('name', 'Test category name');
        await this.browser.clickInto('parent-category-modal__input', {waitRender: true});
        await this.browser.clickInto(['row_front_category_code_1_0', 'title']);
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        const categoryUrl = await this.browser.getUrl();
        const categoryId = getEntityIdFromUrl(categoryUrl);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER), {
            clearLocalStorage: true,
            localStorageItems: {
                frontCategoryProductList: {
                    isAllSelected: false,
                    isAllActive: true,
                    isAllCollapsed: false,
                    isAllExpanded: true
                }
            }
        });
        await this.browser.clickInto('\\#rc-tabs-0-tab-front-categories');
        await this.browser.clickInto(['product_fc_row_test_category_code', 'checkbox']);
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.clickInto(['product_fc_row_test_category_code', 'checkbox']);
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(categoryId));
        await this.browser.clickInto('disabled_label');
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.clickInto(['header-panel', 'delete-button'], {waitForClickable: true});
        await this.browser.clickInto('confirmation-modal__ok-button', {waitForClickable: true, waitNavigation: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER));
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await assertListItemImageStretched(this, 'list-item-2');
    });

    it('Удаленные атрибуты, которые когда-то были заполнены и очищены в товаре', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.typeInto('code', 'test_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true, waitNavigation: true});
        const attributeUrl = await this.browser.getUrl();
        const attributeId = getEntityIdFromUrl(attributeUrl);

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_14));
        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['attributes-search'], {waitRender: true});
        await this.browser.typeInto('attributes-search', 'test_attribute_code', {clear: true});
        await this.browser.waitUntilRendered();
        await this.browser.clickInto(['attribute-select-virtual-list', 'test_attribute_code']);
        await this.browser.clickInto('im-user_attributes-table', {
            waitRender: true
        });
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER));
        await this.browser.clickInto('test_attribute_code_on');
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.clickInto('test_attribute_code_unset');
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributeId));
        await this.browser.clickInto(['header-panel', 'delete-button'], {waitForClickable: true});
        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button'], {
            waitForClickable: true,
            waitNavigation: true
        });

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER));
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-3']);
    });

    it('Поиск удаленного атрибута в истории товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.typeInto('code', 'test_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true, waitNavigation: true});
        const attributeUrl = await this.browser.getUrl();
        const attributeId = getEntityIdFromUrl(attributeUrl);

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_14));
        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['attributes-search'], {waitRender: true});
        await this.browser.typeInto('attributes-search', 'test_attribute_code', {clear: true});
        await this.browser.waitUntilRendered();
        await this.browser.clickInto(['attribute-select-virtual-list', 'test_attribute_code']);
        await this.browser.clickInto('im-user_attributes-table', {
            waitRender: true
        });
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER));
        await this.browser.clickInto('test_attribute_code_on');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.clickInto('test_attribute_code_unset');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributeId));
        await this.browser.clickInto(['header-panel', 'delete-button'], {waitRender: true});
        await this.browser.clickInto(['confirmation-modal', 'confirmation-modal__ok-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER));
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.typeInto('history-of-changes_search', 'test_attribute_code');
        await this.browser.assertImage('history-of-changes_list', {stretch: true});
    });

    it('Отображение истории изменения МК после изменения товара с сохранением МК', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER));
        await this.browser.clickInto(['status', 'disabled_label']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_25_0));
        await this.browser.typeInto(['info-model-select', '\\input'], 'Наследуемая');
        await this.browser.clickInto(['info-model-select_dropdown-menu', 'im_node_inherited_0']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER));
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-3']);
    });

    it('Скачивание изображения из истории товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER), {clearLocalStorage: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await this.browser.clickInto(
            ['list-item-2', 'table-row_image_attribute_code_1_0', 'new-value', 'download-image'],
            {
                waitForClickable: true
            }
        );
        const file = await this.browser.getDownloadedFile('product_attr..._code_1_8_0.png', {purge: true});

        const hash = crypto.createHash('md5').update(file);
        expect(hash.digest('hex')).to.matchSnapshot(this);
    });

    it('Кнопка скачать есть для старых загруженных значений', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER), {clearLocalStorage: true});

        await this.browser.uploadFileInto(['product-image', 'file-input'], createImageFile('test_product_image.png'));
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true, waitRender: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await this.browser.assertImage(['history-of-changes_list', 'list-item-2', 'table-row_image', 'old-value']);
    });

    it('Кнопка скачать есть для старых удаленных значений', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER), {clearLocalStorage: true});

        await this.browser.clickInto(['product-image', 'delete-image'], {waitRender: true});
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true, waitRender: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await this.browser.assertImage(['history-of-changes_list', 'list-item-2', 'table-row_image', 'old-value']);
    });

    it('Кнопка "скачать" есть для новых значений, которые уже были загружены', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER), {clearLocalStorage: true});

        await this.browser.uploadFileInto(['product-image', 'file-input'], createImageFile('test_product_image.png'));
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true, waitRender: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await this.browser.assertImage(['history-of-changes_list', 'list-item-2', 'table-row_image', 'new-value']);
    });

    it('Кнопка "скачать" есть для новых значений, которые только что загрузили', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(IDENTIFIER), {clearLocalStorage: true});

        await this.browser.clickInto(['product-image', 'delete-image'], {waitRender: true});
        await this.browser.uploadFileInto(['product-image', 'file-input'], createImageFile('test_product_image.png'));
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true, waitRender: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await this.browser.assertImage(['history-of-changes_list', 'list-item-2', 'table-row_image', 'new-value']);
    });
});
