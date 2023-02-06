import {productCombos} from 'tests/e2e/seed-db-map';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Страница комбинации', function () {
    async function selectProductOption(
        ctx: Hermione.TestContext,
        baseSelector: string,
        optionSku: string | number,
        options?: {close?: true}
    ) {
        await ctx.browser.clickInto([baseSelector, 'search'], {waitForClickable: true});
        await ctx.browser.typeInto([baseSelector, 'search'], String(optionSku ?? ''), {clear: true});

        await ctx.browser.waitForTestIdSelectorInDom([
            baseSelector,
            'product-combo-option-list',
            `product-combo-option_${optionSku}`
        ]);

        await ctx.browser.waitForTestIdSelectorNotInDom([baseSelector, 'product-combo-option-list', 'spinner-loading']);
        await ctx.browser.waitUntilRendered();
        await ctx.browser.clickInto([baseSelector, 'product-combo-option-list', `product-combo-option_${optionSku}`]);

        if (options?.close) {
            await ctx.browser.clickInto('groups-parameters', {x: 5, y: 5, waitRender: true});
        }
    }

    it('Поиск мета-товара по id на странице комбинации', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['51e2ac6a-6baa-44e5-8763-9cfbe03f7e1b'])
        );

        await this.browser.clickInto(['metaProducts', 'search']);
        await this.browser.typeInto(['metaProducts', 'search'], '10000203');
        await this.browser.waitForTestIdSelectorInDom(['metaProducts', 'product-combo-option-list']);
        await this.browser.waitForTestIdSelectorNotInDom([
            'metaProducts',
            'product-combo-option-list',
            'spinner-loading'
        ]);
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['metaProducts', 'product-combo-option-list'], {removeShadows: true});
    });

    it('Удаление мета-товара с комбинации. Израиль', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.il['ea6ffd03-73b6-4964-bee4-f63de4906cf8']),
            {region: 'il'}
        );

        await this.browser.clickInto([
            'metaProducts_container',
            'product-combo-selected-option-list',
            'product-combo-option-row_10000211',
            'delete-icon'
        ]);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.il['ea6ffd03-73b6-4964-bee4-f63de4906cf8']),
            {region: 'il'}
        );

        await this.browser.assertImage('meta-product-parameters', {removeShadows: true});
    });

    it('Замена мета-товара у комбинации', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['52d07868-aa1d-4114-9e2e-73789319c33f'])
        );

        await this.browser.clickInto([
            'metaProducts_container',
            'product-combo-selected-option-list',
            'product-combo-option-row_10000202',
            'delete-icon'
        ]);

        await selectProductOption(this, 'metaProducts', 10000201, {close: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['52d07868-aa1d-4114-9e2e-73789319c33f'])
        );

        await this.browser.assertImage('meta-product-parameters', {removeShadows: true});
    });

    it('Ссылка на мета-товар открывается в новом окне', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['52d07868-aa1d-4114-9e2e-73789319c33f'])
        );

        await this.browser.clickInto([
            'metaProducts_container',
            'product-combo-selected-option-list',
            'product-combo-option-row_10000202',
            'product-link'
        ]);

        const handles = await this.browser.getWindowHandles();
        expect(handles.length).to.equal(2);

        await this.browser.switchToWindow(handles[1]);
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.PRODUCT(10000202)));

        await this.browser.closeWindow();
        await this.browser.switchToWindow(handles[0]);
    });

    it('Ссылка на товар в группе открывается в новом окне', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['52d07868-aa1d-4114-9e2e-73789319c33f'])
        );

        await this.browser.execute(() => window.scrollTo({top: 1000}));

        await this.browser.clickInto([
            'groups.0.options_container',
            'product-combo-selected-option-list',
            'product-combo-option-row_10000004',
            'product-link'
        ]);

        const handles = await this.browser.getWindowHandles();
        expect(handles.length).to.equal(2);

        await this.browser.switchToWindow(handles[1]);
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.PRODUCT(10000004)));

        await this.browser.closeWindow();
        await this.browser.switchToWindow(handles[0]);
    });

    it('Смена статуса комбинации', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['b6b0eb6f-c701-4aa2-a830-910f5745f6aa'])
        );

        await this.browser.clickInto(['base.status', 'disabled']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['b6b0eb6f-c701-4aa2-a830-910f5745f6aa'])
        );

        await this.browser.assertImage('combination-parameters', {removeShadows: true});
    });

    it('Поиск по товарам в группе по id', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['b6b0eb6f-c701-4aa2-a830-910f5745f6aa'])
        );

        await this.browser.execute(() => window.scrollTo({top: 1000}));

        await this.browser.clickInto(['groups.0.options', 'search']);
        await this.browser.typeInto(['groups.0.options', 'search'], '10000010');
        await this.browser.waitForTestIdSelectorInDom(['groups.0.options', 'product-combo-option-list']);
        await this.browser.waitForTestIdSelectorNotInDom([
            'groups.0.options',
            'product-combo-option-list',
            'spinner-loading'
        ]);
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['groups.0.options', 'product-combo-option-list'], {removeShadows: true});
    });

    it('Поиск по товарам в группе по баркоду', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['b6b0eb6f-c701-4aa2-a830-910f5745f6aa'])
        );

        await this.browser.execute(() => window.scrollTo({top: 1000}));

        await this.browser.clickInto(['groups.0.options', 'search']);
        await this.browser.typeInto(['groups.0.options', 'search'], '7758221173891');
        await this.browser.waitForTestIdSelectorInDom(['groups.0.options', 'product-combo-option-list']);
        await this.browser.waitForTestIdSelectorNotInDom([
            'groups.0.options',
            'product-combo-option-list',
            'spinner-loading'
        ]);
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['groups.0.options', 'product-combo-option-list'], {removeShadows: true});
    });

    it('Нельзя стереть название группы в комбинации. Израиль', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.il['218eaddc-149a-4c0a-91aa-088a5bf94242']),
            {region: 'il'}
        );

        await this.browser.execute(() => window.scrollTo({top: 1000}));
        await this.browser.typeInto('groups.0.nameTranslations.en', '', {clear: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.assertImage('groups.0.nameTranslations.en_container');

        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.il['218eaddc-149a-4c0a-91aa-088a5bf94242']),
            {region: 'il'}
        );

        await this.browser.execute(() => window.scrollTo({top: 1000}));

        await this.browser.assertImage('groups.0.nameTranslations.en_container');
    });

    it('Общий вид страницы комбинации', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['b6b0eb6f-c701-4aa2-a830-910f5745f6aa'])
        );

        await this.browser.waitForTestIdSelectorDisabled('product-combo-uuid');
        await this.browser.assertImage('header-panel');
        await this.browser.assertImage('base-layout-content');
    });

    it('Закрытие комбинации', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['b6b0eb6f-c701-4aa2-a830-910f5745f6aa'])
        );

        await this.browser.clickInto(['header-panel', 'close-button'], {waitForClickable: true, waitNavigation: true});
        await expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.PRODUCT_COMBOS));
    });

    it('Отмена внесения изменений в комбинацию', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['b6b0eb6f-c701-4aa2-a830-910f5745f6aa'])
        );

        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'cancel-button']);
        await this.browser.clickInto(['base.status', 'disabled']);
        await this.browser.assertImage('header-panel');

        await this.browser.clickInto(['header-panel', 'cancel-button'], {waitRender: true});
        await this.browser.assertImage('confirmation-modal', {removeShadows: true});
        await this.browser.clickInto('confirmation-modal__ok-button');
        await this.browser.assertImage('header-panel');
        await this.browser.assertImage('combination-parameters', {removeShadows: true});
    });

    it('Удаление комбинации', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['d2fc5c0d-83d6-4242-941a-5acb01bc6940'])
        );

        await this.browser.clickInto(['header-panel', 'delete-button'], {waitRender: true});
        await this.browser.assertImage('confirmation-modal', {removeShadows: true});

        await this.browser.clickInto('confirmation-modal__ok-button', {waitNavigation: true});
        await expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.PRODUCT_COMBOS));

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000203));
        await this.browser.execute(() => window.scrollTo({top: 1000}));
        await this.browser.assertImage('linked-product-combos', {removeShadows: true});
    });

    it('Нельзя удалить все товары из группы в комбинации', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['b6b0eb6f-c701-4aa2-a830-910f5745f6aa'])
        );
        await this.browser.execute(() => window.scrollTo({top: 1000}));

        await this.browser.clickInto([
            'groups.0.options_container',
            'product-combo-selected-option-list',
            'product-combo-option-row_10000001',
            'delete-icon'
        ]);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.assertImage('groups.0.options_container', {removeShadows: true});

        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['b6b0eb6f-c701-4aa2-a830-910f5745f6aa'])
        );
        await this.browser.execute(() => window.scrollTo({top: 1000}));
        await this.browser.assertImage('groups.0.options_container', {removeShadows: true});
    });

    it('Редактирование группы товаров у активной комбинации', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['b6b0eb6f-c701-4aa2-a830-910f5745f6aa'])
        );
        await this.browser.execute(() => window.scrollTo({top: 1000}));

        await this.browser.typeInto('groups.0.nameTranslations.ru', 'foo-bar-baz', {clear: true});
        await this.browser.typeInto('groups.0.optionsToSelect', '2', {clear: true});
        await this.browser.clickInto('groups.0.canRepeatOptionSelect');
        await selectProductOption(this, 'groups.0.options', 10000002, {close: true});

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.clickInto('confirmation-modal__apply', {waitRender: true, waitForClickable: true});
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['b6b0eb6f-c701-4aa2-a830-910f5745f6aa'])
        );
        await this.browser.execute(() => window.scrollTo({top: 1000}));

        await this.browser.assertImage('groups-parameters', {removeShadows: true});
    });

    it('Сохранение комбинации с группой, с повторно выбираемыми товарами. Израиль', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.il['6a1f6ad8-f910-4341-8c8c-37bd2f2de997']),
            {region: 'il'}
        );
        await this.browser.execute(() => window.scrollTo({top: 1000}));

        await this.browser.typeInto('groups.0.optionsToSelect', '10', {clear: true});
        await this.browser.clickInto('groups.0.canRepeatOptionSelect');

        await this.browser.execute(() => window.scrollTo({top: 0}));

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.clickInto('confirmation-modal__apply', {waitRender: true, waitForClickable: true});

        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.il['6a1f6ad8-f910-4341-8c8c-37bd2f2de997']),
            {region: 'il'}
        );
        await this.browser.execute(() => window.scrollTo({top: 1000}));

        await this.browser.assertImage('groups-parameters', {removeShadows: true});
    });

    it('Смена порядка групп у активной комбинации', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['d2fc5c0d-83d6-4242-941a-5acb01bc6940'])
        );
        await this.browser.execute(() => window.scrollTo({top: 1000}));

        await this.browser.dragAndDrop(
            ['\\#product-combo-group-panel_3', 'list-item-header', 'drag-icon'],
            ['\\#product-combo-group-panel_1', 'list-item-header', 'drag-icon'],
            {offset: 'bottom'}
        );

        await this.browser.execute(() => window.scrollTo({top: 0}));
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['d2fc5c0d-83d6-4242-941a-5acb01bc6940'])
        );
        await this.browser.execute(() => window.scrollTo({top: 1000}));
        await this.browser.assertImage('groups-parameters', {removeShadows: true});
    });

    it('Удаление одной из групп у активной комбинацию - сохранение с деактивацией', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['792fdfd3-5317-42bb-9db4-20a602c7cc3b'])
        );
        await this.browser.execute(() => window.scrollTo({top: 1000}));

        await this.browser.clickInto(['\\#product-combo-group-panel_1', 'list-item-header', 'delete-icon'], {
            waitRender: true
        });

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('confirmation-modal');
        await this.browser.assertImage('confirmation-modal', {removeShadows: true});
        await this.browser.clickInto('confirmation-modal__deactivate-and-apply', {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.assertImage('combination-parameters', {removeShadows: true});
        await this.browser.assertImage('groups-parameters', {removeShadows: true});
    });

    // eslint-disable-next-line max-len
    it('Добавление дополнительной группы товаров в активную комбинацию - сохранение без деактивации', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['52d07868-aa1d-4114-9e2e-73789319c33f'])
        );
        await this.browser.execute(() => window.scrollTo({top: 1000}));

        await this.browser.clickInto(['groups-parameters', 'add-group']);
        await this.browser.execute(() => window.scrollTo({top: 1000}));
        await this.browser.typeInto('groups.1.nameTranslations.ru', 'foo-bar-baz');
        await selectProductOption(this, 'groups.1.options', 10000001, {close: true});

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.clickInto('confirmation-modal__apply', {waitRender: true, waitForClickable: true});

        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['52d07868-aa1d-4114-9e2e-73789319c33f'])
        );
        await this.browser.execute(() => window.scrollTo({top: 1000}));
        await this.browser.assertImage('groups-parameters', {removeShadows: true});
    });

    it('Можно изменить тип комбинации', async function () {
        await this.browser.openPage(
            ROUTES.CLIENT.PRODUCT_COMBO(productCombos.ru['51e2ac6a-6baa-44e5-8763-9cfbe03f7e1b'])
        );

        await this.browser.clickInto('base.type', {waitRender: true, waitForClickable: true});
        await this.browser.clickInto(['base.type_dropdown-menu', 'recipe']);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitForClickable: true});
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.assertImage('base.type_container');
    });
});
