import {attributes} from 'tests/e2e/seed-db-map';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('История изменений атрибута', function () {
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

    it('Запись об изменении названия у логического атрибута', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributes.boolean_attribute_code_0_0));

        await this.browser.typeInto(['translations', 'ru', 'name'], 'foo bar baz', {clear: true});

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitRender: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись об удалении описания у атрибута-изображения', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributes.image_attribute_code_1_0));

        await this.browser.typeInto(['translations', 'ru', 'description'], '', {clear: true});

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitRender: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись о создании локализуемой строки с диапазоном длины', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto(['attribute-type_dropdown-menu', 'attribute-type-string'], {waitRender: true});

        await this.browser.typeInto('code', 'test_string_attr');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');

        await this.browser.typeInto(['symbols-count', 'min'], '2');
        await this.browser.typeInto(['symbols-count', 'max'], '6');

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true, waitNavigation: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitRender: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await assertListItemImageStretched(this, 'list-item-2');
    });

    it('Запись о создании текстового множественного атрибута', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto(['attribute-type_dropdown-menu', 'attribute-type-text'], {waitRender: true});

        await this.browser.typeInto('code', 'test_text_attr');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto('is-array');

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true, waitNavigation: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitRender: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await assertListItemImageStretched(this, 'list-item-2');
    });

    it('Запись о создании числового множественного атрибута с ограничением на количество', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto(['attribute-type_dropdown-menu', 'attribute-type-number'], {waitRender: true});

        await this.browser.typeInto('code', 'test_number_attr');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto('is-array', {waitRender: true});
        await this.browser.typeInto('max-array-size', '3');

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true, waitNavigation: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitRender: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await assertListItemImageStretched(this, 'list-item-2');
    });

    it('Запись о создании числового положительного атрибута с диапазоном значений', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto(['attribute-type_dropdown-menu', 'attribute-type-number'], {waitRender: true});

        await this.browser.typeInto('code', 'test_number_attr');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto('can-be-negative');
        await this.browser.typeInto(['symbols-count', 'min'], '2');
        await this.browser.typeInto(['symbols-count', 'max'], '6');

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true, waitNavigation: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitRender: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await assertListItemImageStretched(this, 'list-item-2');
    });

    it('Запись о добавлении описания на одном языке у атрибута', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto(['attribute-type_dropdown-menu', 'attribute-type-number'], {waitRender: true});

        await this.browser.typeInto('code', 'test_number_attr');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true, waitNavigation: true});

        await this.browser.typeInto(['translations', 'ru', 'description'], 'foo bar baz');

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitRender: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Поиск по значению параметра', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributes.number_attribute_code_3_0));

        // Сделаем еще одну запись в истории, чтобы проверить что при поиске будет отображаться
        // только та таблица, в которой нашлось значение
        await this.browser.typeInto(['translations', 'ru', 'description'], 'foo bar baz', {clear: true});

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitRender: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await this.browser.typeInto('history-of-changes_search', 'number_attribute_code_3_0');
        await this.browser.waitUntilRendered();

        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Скролл страницы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributes.number_attribute_code_3_0));

        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await this.browser.performScroll('history-of-changes_list');
        await this.browser.assertImage('base-layout-content');
    });

    it('Запись о смене перевода опции у множественного списка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributes.multiselect_attribute_code_2_0));

        await this.browser.clickInto('select-option-header-attribute_option_code_10_1', {waitRender: true});
        await this.browser.typeInto('select-option-translation_ru_attribute_option_code_10_1', 'foo bar baz', {
            clear: true
        });

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitRender: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись о добавлении и смене порядка опций у атрибута-списка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributes.multiselect_attribute_code_2_0));

        await this.browser.dragAndDrop(
            ['select-option-header-attribute_option_code_10_2', 'drag-icon'],
            ['select-option-header-attribute_option_code_10_1', 'drag-icon']
        );

        await this.browser.clickInto('select-option-add', {waitRender: true});
        await this.browser.typeInto(['select-option-header', 'select-option-code'], 'test_option_code');

        await this.browser.typeInto('select-option-translation_ru_test_option_code', 'foo bar baz');

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitRender: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись об изменении группы атрибута в истории атрибута', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributes.boolean_attribute_code_0_0));

        await this.browser.clickInto(['attribute-base_params', 'group-parameter']);
        await this.browser.clickInto(['group-parameter_dropdown-menu', 'attribute_group_code_2']);
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorNotInDom('submit-button');
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('МП: изменение подтверждаемости атрибута отражается в истории товара', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTE(attributes.boolean_attribute_code_0_0));

        await this.browser.clickInto(['attribute-base_params', 'is-confirmable_container', 'is-confirmable']);

        await this.browser.clickInto('submit-button');

        await this.browser.waitForTestIdSelectorNotInDom('submit-button');
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);

        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись о создании в истории атрибута типа "Видео"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto(['attribute-type_dropdown-menu', 'attribute-type-video'], {waitRender: true});

        await this.browser.typeInto('code', 'test_video_attr');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true, waitNavigation: true});
        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitRender: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await assertListItemImageStretched(this, 'list-item-2');
    });
});
