import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Создание комбинации', function () {
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

    it('Форма создания комбинации', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS_CREATE);
        await this.browser.waitForTestIdSelectorDisabled(['header-panel', 'submit-button']);
        await this.browser.assertImage('header-panel');
        await this.browser.assertImage('base-layout-content');
    });

    it('Отмена создания комбинации (без изменений)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS_CREATE);
        await this.browser.clickInto(['base.status', 'active']);
        await this.browser.clickInto(['base.status', 'disabled']);
        await this.browser.clickInto(['header-panel', 'cancel-button'], {waitNavigation: true});
        await expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.PRODUCT_COMBOS));
    });

    it('Отмена создания комбинации (с внесением изменений)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS_CREATE);
        await this.browser.clickInto(['base.status', 'active']);
        await this.browser.clickInto(['header-panel', 'cancel-button'], {waitForClickable: true, waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('confirmation-modal');
        await this.browser.assertImage('confirmation-modal', {removeShadows: true});
    });

    it('Нельзя создать комбинацию без группы с названием и товаром', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS_CREATE);
        await this.browser.waitForTestIdSelectorDisabled(['header-panel', 'submit-button']);

        await this.browser.typeInto('groups.0.nameTranslations.ru', 'foo-bar-baz');
        await this.browser.waitForTestIdSelectorDisabled(['header-panel', 'submit-button']);

        await this.browser.typeInto('groups.0.nameTranslations.ru', '', {clear: true, blur: true});
        await selectProductOption(this, 'groups.0.options', 10000001, {close: true});
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.assertImage('groups.0.nameTranslations.ru_container');
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.PRODUCT_COMBOS_CREATE));
    });

    it('Создание активной комбинации без мета-товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS_CREATE);

        await this.browser.clickInto(['base.status', 'active']);
        await this.browser.clickInto('base.type', {waitRender: true});
        await this.browser.clickInto(['base.type_dropdown-menu', 'discount']);
        await this.browser.typeInto('groups.0.nameTranslations.ru', 'Test group name');
        await this.browser.typeInto('groups.0.optionsToSelect', '2', {clear: true});
        await selectProductOption(this, 'groups.0.options', 10000001);
        await selectProductOption(this, 'groups.0.options', 10000002, {close: true});

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitForClickable: true, waitNavigation: true});
        await expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.PRODUCT_COMBO('\\d')));
        await this.browser.assertImage('base-layout-content', {
            ignoreElements: ['[data-testid=entity-header-info-title]', '[data-testid=product-combo-uuid]']
        });
    });

    it('Создание неактивной комбинации с мета-товаром', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS_CREATE);

        await selectProductOption(this, 'metaProducts', 10000201);

        await this.browser.clickInto('base.type');
        await this.browser.clickInto(['base.type_dropdown-menu', 'recipe']);
        await this.browser.typeInto(['translations', 'ru', 'name'], 'Test combo name');
        await this.browser.typeInto(['translations', 'ru', 'description'], 'Test combo description');

        await this.browser.typeInto('groups.0.nameTranslations.ru', 'Test group name');
        await this.browser.typeInto('groups.0.optionsToSelect', '2', {clear: true});
        await selectProductOption(this, 'groups.0.options', 10000001);
        await selectProductOption(this, 'groups.0.options', 10000002, {close: true});

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitForClickable: true, waitNavigation: true});
        await expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.PRODUCT_COMBO('\\d')));
        await this.browser.assertImage('base-layout-content', {ignoreElements: '[data-testid=product-combo-uuid]'});
    });

    it('Поиск мета-товара по названию. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS_CREATE, {region: 'il', dataLang: 'en'});

        await this.browser.clickInto(['metaProducts', 'search']);
        await this.browser.typeInto(['metaProducts', 'search'], 'Ex provident accusantium');
        await this.browser.waitForTestIdSelectorInDom(['metaProducts', 'product-combo-option-list']);
        await this.browser.waitForTestIdSelectorNotInDom([
            'metaProducts',
            'product-combo-option-list',
            'spinner-loading'
        ]);
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['metaProducts', 'product-combo-option-list'], {removeShadows: true});
    });

    it('Поиск по товарам в группе по названию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS_CREATE);

        await this.browser.clickInto(['groups.0.options', 'search']);
        await this.browser.typeInto(['groups.0.options', 'search'], 'Перед истину');
        await this.browser.waitForTestIdSelectorInDom(['groups.0.options', 'product-combo-option-list']);
        await this.browser.waitForTestIdSelectorNotInDom([
            'groups.0.options',
            'product-combo-option-list',
            'spinner-loading'
        ]);
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['groups.0.options', 'product-combo-option-list'], {removeShadows: true});
    });

    it('Нельзя создать комбинацию без групп товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS_CREATE);
        await this.browser.clickInto(['\\#product-combo-group-panel_1', 'list-item-header', 'delete-icon'], {
            waitRender: true
        });
        await this.browser.assertImage('header-panel');
        await this.browser.assertImage('groups-parameters', {removeShadows: true});
    });

    // eslint-disable-next-line max-len
    it('Нельзя создать комбинацию с группой, в которой товаров меньше чем необходимо для получения скидки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS_CREATE);

        await this.browser.typeInto('groups.0.nameTranslations.ru', 'Test group name');
        await this.browser.typeInto('groups.0.optionsToSelect', '3', {clear: true});
        await selectProductOption(this, 'groups.0.options', 10000001);
        await selectProductOption(this, 'groups.0.options', 10000002, {close: true});

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitForClickable: true, waitRender: true});
        await this.browser.assertImage('groups.0.optionsToSelect_container');
    });

    it('Нельзя создать комбинацию с группой, в которой необходимо ноль товаров для скидки', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS_CREATE);

        await this.browser.typeInto('groups.0.nameTranslations.ru', 'Test group name');
        await this.browser.typeInto('groups.0.optionsToSelect', '0', {clear: true});
        await selectProductOption(this, 'groups.0.options', 10000001, {close: true});

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitForClickable: true, waitRender: true});
        await this.browser.assertImage('groups.0.optionsToSelect_container');
    });

    it('Свернуть/развернуть группу товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS_CREATE);

        await this.browser.clickInto(['\\#product-combo-group-panel_1', 'list-item-header'], {waitRender: true});
        await this.browser.assertImage('\\#product-combo-group-panel_1');

        await this.browser.clickInto(['\\#product-combo-group-panel_1', 'list-item-header'], {waitRender: true});
        await this.browser.assertImage('\\#product-combo-group-panel_1');
    });

    it('Смена порядка товаров в группе', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS_CREATE);

        await selectProductOption(this, 'groups.0.options', 10000001);
        await selectProductOption(this, 'groups.0.options', 10000002);
        await selectProductOption(this, 'groups.0.options', 10000003, {close: true});

        await this.browser.execute(() => window.scrollTo({top: 1000}));

        await this.browser.assertImage('groups.0.options_container');

        await this.browser.dragAndDrop(
            [
                'groups.0.options_container',
                'product-combo-selected-option-list',
                'product-combo-option-row_10000003',
                'drag-icon'
            ],
            [
                'groups.0.options_container',
                'product-combo-selected-option-list',
                'product-combo-option-row_10000001',
                'drag-icon'
            ],
            {offset: 'bottom'}
        );

        await this.browser.assertImage('groups.0.options_container');
    });

    it('Страница создания комбинации по кнопке из таблицы. Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS, {region: 'fr'});
        await this.browser.clickInto(['action-bar', 'create-button'], {waitNavigation: true});
        await expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.PRODUCT_COMBOS_CREATE));
        await this.browser.assertImage('base-layout-content');
    });

    it('Нельзя создать комбинацию без типа', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS_CREATE);

        await this.browser.typeInto('groups.0.nameTranslations.ru', 'Test group name');
        await selectProductOption(this, 'groups.0.options', 10000001);
        await selectProductOption(this, 'groups.0.options', 10000002, {close: true});

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitForClickable: true, waitRender: true});
        await this.browser.assertImage('base.type_container');
    });
});
