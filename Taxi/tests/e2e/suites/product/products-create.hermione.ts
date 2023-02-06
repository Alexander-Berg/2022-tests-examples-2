import {infoModels, requiredAttributes} from 'tests/e2e/seed-db-map';
import makeAttributeConfirmable from 'tests/e2e/utils/make-attribute-confirmable';
import {describe, expect, it} from 'tests/hermione.globals';

import {LANGUAGES} from '@/src/constants';
import {ROUTES} from '@/src/constants/routes';

import {chooseMasterCategory} from './util';

const INFO_MODEL_ID = infoModels.ru.info_model_code_1_1;

async function expandWindowAndAssertImage(browser: WebdriverIO.Browser, selector: Hermione.Selector) {
    const initialSize = await browser.getWindowSize();

    const additionalHeight = await browser.execute(
        () => document.documentElement.scrollHeight - document.documentElement.clientHeight
    );

    if (!additionalHeight) {
        throw new Error('additional height is undefined');
    }

    await browser.setWindowSize(initialSize.width, initialSize.height + additionalHeight);
    await browser.assertImage(selector);
    await browser.setWindowSize(initialSize.width, initialSize.height);
}

describe('Страница создания товаров', () => {
    async function fillRequiredAttributes(browser: WebdriverIO.Browser, lang = LANGUAGES[2]) {
        await browser.clickInto('add_new_barcode', {waitRender: true});
        await browser.typeInto('barcode__0', '0000000000000');
        await browser.typeInto(`longName_${lang}`, 'Foo product');
        await browser.typeInto(`shortNameLoc_${lang}`, 'Foo');
        await browser.typeInto('markCount', '12');
        await browser.typeInto('markCountUnit', 'gramm');
        await browser.clickInto('nomenclatureType');
        await browser.clickInto(['nomenclatureType_dropdown-menu', 'product']);
    }

    it('Шапка страницы создания товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS_CREATE);

        await chooseMasterCategory(this.browser);
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
        await this.browser.assertImage('header-panel');
    });

    it('Системные атрибуты, Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {region: 'il'});
        await this.browser.clickInto('create-button', {waitRender: true});
        await this.browser.clickInto(['action-bar', 'create-real'], {waitRender: true});

        await chooseMasterCategory(this.browser, 'IL');
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true, waitNavigation: true});

        expect(await this.browser.getPath()).to.match(new RegExp(ROUTES.CLIENT.PRODUCTS_CREATE));
        await this.browser.assertImage(['product_view', 'basic-attributes'], {removeShadows: true});
    });

    it('Системные атрибуты, Россия', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto('create-button', {waitRender: true});
        await this.browser.clickInto(['action-bar', 'create-real'], {waitRender: true});

        await chooseMasterCategory(this.browser);
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true, waitNavigation: true});

        expect(await this.browser.getPath()).to.match(new RegExp(ROUTES.CLIENT.PRODUCTS_CREATE));
        await this.browser.assertImage(['product_view', 'basic-attributes'], {removeShadows: true});
    });

    it('Клик на "Отмена" до изменений переводит к странице товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS_CREATE);

        await chooseMasterCategory(this.browser);
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
        await this.browser.clickInto('cancel-button', {waitRender: true, waitNavigation: true});

        expect(await this.browser.getPath()).to.match(new RegExp(ROUTES.CLIENT.PRODUCTS));
    });

    it('Клик на "Отмена" после изменений показывает модальное окно', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS_CREATE);

        await chooseMasterCategory(this.browser);
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
        await fillRequiredAttributes(this.browser);
        await this.browser.clickInto('cancel-button', {waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.PRODUCTS_CREATE));
        await this.browser.assertImage('confirmation-modal', {removeShadows: true});
    });

    it('Клик на "Создать" до заполнения обязательных полей, Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS_CREATE, {region: 'fr'});

        await chooseMasterCategory(this.browser, 'FR');
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
        await this.browser.clickInto('submit-button', {waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.PRODUCTS_CREATE));
        await this.browser.assertImage(['product_view', 'basic-attributes'], {removeShadows: true});
    });

    it('Создать товар', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS_CREATE);

        await chooseMasterCategory(this.browser);
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
        await fillRequiredAttributes(this.browser);
        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});

        const productId = await this.browser.execute(
            () => document.querySelector('[data-testid=product_id]')?.textContent
        );

        expect(await this.browser.getPath()).to.match(new RegExp(ROUTES.CLIENT.PRODUCT(productId as string)));
        await this.browser.assertImage('base-layout', {ignoreElements: '[data-testid=product_id]'});

        await this.browser.openPage(
            `${ROUTES.CLIENT.PRODUCTS}?filters[id][rule]=equal&filters[id][values]=${productId}`
        );
        const doesProductExistInTable = await this.browser.execute(
            (productId) => document.querySelector(`[data-testid=products-table-row_${productId}]`) !== null,
            productId
        );
        expect(doesProductExistInTable).to.be.equal(true);
    });

    it('Форма создания товара с множественными изображениями', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS_CREATE);
        await chooseMasterCategory(this.browser);
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
        await expandWindowAndAssertImage(this.browser, 'base-layout');

        await this.browser.clickInto('infomodel-link', {waitRender: true, waitNavigation: true});
        await this.browser.clickInto('\\#rc-tabs-1-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['im_attribute_row_image_attribute_code_1_1', 'switch-important']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS_CREATE);
        await chooseMasterCategory(this.browser);
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
        await expandWindowAndAssertImage(this.browser, 'base-layout');
    });

    it('Смена языка интерфейса на странице создания товара (Россия)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS_CREATE);
        await chooseMasterCategory(this.browser);
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('ui-lang-select', {waitRender: true});
        await this.browser.clickInto(['ui-lang-select_dropdown-menu', 'fr'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Форма создания товара в категории с обязательными атрибутами', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(INFO_MODEL_ID));
        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['im_attribute_row_boolean_attribute_code_0_0', 'delete']);
        await this.browser.clickInto(['im_attribute_row_multiselect_attribute_code_2_0', 'delete']);
        await this.browser.clickInto(['infomodel-groups-table', 'im_attribute-group_row_attribute_group_code_2']);
        await this.browser.clickInto(['im_attribute_row_select_attribute_code_4_0', 'delete']);
        await this.browser.clickInto(['infomodel-groups-table', 'im_attribute-group_row_attribute_group_code_3']);
        await this.browser.clickInto(['im_attribute_row_text_attribute_code_6_0', 'delete']);
        await this.browser.clickInto(['infomodel-groups-table', 'im_attribute-group_row_undefined']);
        await this.browser.clickInto(['im_attribute_row_image', 'delete']);
        await this.browser.clickInto(['header', 'header-panel', 'submit-button'], {
            waitRender: true
        });

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto(['base-layout-content', 'action-bar', 'create-button'], {waitRender: true});
        await this.browser.clickInto(['action-bar', 'create-real'], {waitRender: true});
        await this.browser.clickInto(['hide-inactive']);
        await this.browser.clickInto(['parent-category-modal', 'row_master_category_code_1_3'], {
            waitRender: true
        });
        await this.browser.clickInto(['parent-category-modal', 'row_master_category_code_8_1'], {
            waitRender: true
        });
        await this.browser.clickInto(['parent-category-modal', 'row_master_category_code_32_0'], {
            waitRender: true
        });
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
        await this.browser.assertImage('base-layout', {compositeImage: true});
    });

    it('Форма создания товара в категории с дополнительными атрибутами', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(INFO_MODEL_ID));
        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['im_attribute_row_image_attribute_code_1_0', 'delete']);
        await this.browser.clickInto(['infomodel-groups-table', 'im_attribute-group_row_attribute_group_code_2']);
        await this.browser.clickInto(['im_attribute_row_number_attribute_code_3_0', 'delete']);
        await this.browser.clickInto(['infomodel-groups-table', 'im_attribute-group_row_attribute_group_code_3']);
        await this.browser.clickInto(['im_attribute_row_string_attribute_code_5_0', 'delete']);
        await this.browser.clickInto(['infomodel-groups-table', 'im_attribute-group_row_undefined']);
        await this.browser.clickInto(['im_attribute_row_image', 'delete']);
        await this.browser.clickInto(['header', 'header-panel', 'submit-button'], {
            waitRender: true
        });

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto(['base-layout-content', 'action-bar', 'create-button'], {waitRender: true});
        await this.browser.clickInto(['action-bar', 'create-real'], {waitRender: true});
        await this.browser.clickInto(['hide-inactive']);
        await this.browser.clickInto(['parent-category-modal', 'row_master_category_code_1_3'], {
            waitRender: true
        });
        await this.browser.clickInto(['parent-category-modal', 'row_master_category_code_8_1'], {
            waitRender: true
        });
        await this.browser.clickInto(['parent-category-modal', 'row_master_category_code_32_0'], {
            waitRender: true
        });
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Форма создания товара в категории с изображением', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto(['base-layout-content', 'action-bar', 'create-button'], {waitRender: true});
        await this.browser.clickInto(['action-bar', 'create-real'], {waitRender: true});
        await this.browser.clickInto(['hide-inactive']);
        await this.browser.clickInto(['parent-category-modal', 'row_master_category_code_1_3'], {
            waitRender: true
        });
        await this.browser.clickInto(['parent-category-modal', 'row_master_category_code_8_1'], {
            waitRender: true
        });
        await this.browser.clickInto(['parent-category-modal', 'row_master_category_code_32_0'], {
            waitRender: true
        });
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Нельзя создать товар без типа номенклатуры через UI', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS_CREATE);

        await chooseMasterCategory(this.browser);
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});

        await this.browser.clickInto('add_new_barcode', {waitRender: true});
        await this.browser.typeInto('barcode__0', '0000000000000');
        await this.browser.typeInto('longName_ru', 'Foo product');
        await this.browser.typeInto('shortNameLoc_ru', 'Foo');
        await this.browser.typeInto('markCount', '12');
        await this.browser.typeInto('markCountUnit', 'gramm');

        await this.browser.clickInto(['header-panel', 'submit-button']);

        await this.browser.assertImage('basic-attributes', {removeShadows: true});
    });

    it('Нельзя создать товары состоящий только из скрытых символов', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS_CREATE);

        await chooseMasterCategory(this.browser);
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});

        await fillRequiredAttributes(this.browser);

        const formatChar = '\u202C';
        await this.browser.typeInto('barcode__0', formatChar.repeat(3), {clear: true});

        await this.browser.clickInto(['header-panel', 'submit-button']);

        await this.browser.assertImage('basic-attributes', {removeShadows: true});
    });

    // eslint-disable-next-line max-len
    it('Нельзя создать товары с одинаковым штрихкодом, отличающимся наличием скрытого символа, через UI', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS_CREATE, {
            patchStyles: {enableNotifications: true}
        });

        await chooseMasterCategory(this.browser);
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});

        await fillRequiredAttributes(this.browser);

        const formatChar = '\u202C';
        await this.browser.typeInto('barcode__0', `3286357016302${formatChar}`, {clear: true});

        await this.browser.clickInto(['header-panel', 'submit-button']);

        await this.browser.waitForTestIdSelectorInDom('notification');
        await this.browser.assertImage('notification', {removeShadows: true});
    });

    // eslint-disable-next-line max-len
    it('Нельзя создать товары с одинаковым штрихкодом, отличающимся наличием двух или более символов, через UI', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS_CREATE, {
            patchStyles: {enableNotifications: true}
        });

        await chooseMasterCategory(this.browser);
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});

        await fillRequiredAttributes(this.browser);

        const formatChar = '\u202C';
        await this.browser.typeInto('barcode__0', `${formatChar.repeat(3)}3286357016302${formatChar.repeat(3)}`, {
            clear: true
        });
        await this.browser.clickInto(['header-panel', 'submit-button']);

        await this.browser.waitForTestIdSelectorInDom('notification');
        await this.browser.assertImage('notification', {removeShadows: true});
    });

    it('МП: Атрибут можно подтвердить на странице создания товара', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});
        await makeAttributeConfirmable(this.browser, requiredAttributes.markCount);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS_CREATE);
        await chooseMasterCategory(this.browser);
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
        await fillRequiredAttributes(this.browser);

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
});
