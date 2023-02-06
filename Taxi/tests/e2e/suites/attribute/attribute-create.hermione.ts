import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {AttributeType} from 'types/attribute';

describe('Страница создания атрибута', function () {
    async function openPageAndFillDefaults(ctx: Hermione.TestContext, options: {type: AttributeType}) {
        await ctx.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await ctx.browser.clickInto('attribute-type', {waitRender: true});
        await ctx.browser.clickInto(options.type, {waitRender: true});
        await ctx.browser.typeInto('code', `test_${options.type}_attribute_code`);
        await ctx.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
    }

    it('Дефолтное состояние', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.assertImage('base-layout');
    });

    it('Показываются дополнительные параметры для атрибута числового типа', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto('number', {waitRender: true});
        await this.browser.assertImage('attribute_params');
    });

    it('Показываются дополнительные параметры для атрибута типа "текстовая строка"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto('string', {waitRender: true});
        await this.browser.assertImage('attribute_params');
    });

    it('Показываются дополнительные параметры для атрибута типа "многострочный текст"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto('text', {waitRender: true});
        const paramsElement = await this.browser.findByTestId('attribute-base_params');
        await paramsElement.moveTo();
        await this.browser.assertImage('attribute_params');
    });

    it('Показываются дополнительные параметры для атрибута типа "выпадающий список"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto('select', {waitRender: true});
        await this.browser.assertImage('attribute_params');
    });

    it('Показываются дополнительные параметры для атрибута типа "множественный выпадающий список"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto(['attribute-type_dropdown-menu', 'multiselect'], {waitRender: true});
        await this.browser.assertImage('attribute_params');
    });

    it('Удаляется опция выпадающего списка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type');
        await this.browser.clickInto('select');
        await this.browser.clickInto('select-option-add');
        await this.browser.waitForTestIdSelectorInDom('select-option-header');
        await this.browser.clickInto('select-option-delete');
        await this.browser.waitForTestIdSelectorNotInDom('select-option-header');
    });

    it('Показываются дополнительные параметры для атрибута типа "изображение"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto('image', {waitRender: true});
        await this.browser.assertImage('attribute_params');
    });

    it('Кнопка "Создать" неактивна если не заполнены все обязательные поля', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.waitForTestIdSelectorDisabled('submit-button');
    });

    it('Кнопка "Создать" активируется, когда заполнены все обязательные поля', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.typeInto('code', 'test1');
        await this.browser.typeInto('ticket-parameter', 'test2');
        await this.browser.waitForTestIdSelectorEnabled('submit-button');
    });

    it('Клик в "Отмена" возвращает к таблице атрибутов', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('cancel-button', {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.ATTRIBUTES));
    });

    it('Клик в "Отмена" при наличии изменений вызывает модал "Отмена изменений"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.typeInto('code', 'test');
        await this.browser.clickInto('cancel-button', {waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.CREATE_ATTRIBUTE));
        await this.browser.assertImage('confirmation-modal', {removeShadows: true});
    });

    it('Клик в селект "Тип атрибута" открывает список типов', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type-boolean', {waitRender: true});

        await this.browser.assertImage('attribute-type_dropdown-menu');
    });

    it('Включение локализуемости атрибута отключает множественность', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto('string', {waitRender: true});

        await this.browser.clickInto('is-array');
        await this.browser.clickInto('is-localizable');

        await this.browser.assertImage('attribute_params');
    });

    it('Ошибка при создании атрибута с зарезервированным словом в поле "Код"', async function () {
        const RESERVED_WORD = 'id';

        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE, {patchStyles: {enableNotifications: true}});
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto('boolean', {waitRender: true});
        await this.browser.typeInto('code', RESERVED_WORD);
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto('submit-button', {waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.CREATE_ATTRIBUTE));
        await this.browser.assertImage('notification', {removeShadows: true});
    });

    it('Создание логического атрибута', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto('boolean', {waitRender: true});
        await this.browser.typeInto('code', 'test_boolean_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.ATTRIBUTE('\\d')));
        await this.browser.assertImage('attribute-base_params');
    });

    it('Создание числового атрибута', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto('number', {waitRender: true});
        await this.browser.typeInto('code', 'test_number_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');

        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.ATTRIBUTE('\\d')));
        await this.browser.assertImage('attribute-base_params');
    });

    it('Создание числового множественного атрибута с диапазоном значений', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto('number', {waitRender: true});
        await this.browser.typeInto('code', 'test_number_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto('is-array', {waitRender: true});
        await this.browser.typeInto('max-array-size', '100');
        await this.browser.typeInto(['symbols-count', 'min'], '10');
        await this.browser.typeInto(['symbols-count', 'max'], '50');

        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.ATTRIBUTE('\\d')));
        await this.browser.assertImage('attribute_params');
    });

    it('Создание строкового множественного атрибута', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto('string', {waitRender: true});
        await this.browser.typeInto('code', 'test_string_multiple_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto('is-array');

        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.ATTRIBUTE('\\d')));
        await this.browser.assertImage('attribute-base_params');
    });

    it('Создание строкового локализуемого атрибута с ограничением на количество букв', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto('string', {waitRender: true});
        await this.browser.typeInto('code', 'test_text_localizable_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto('is-localizable');
        await this.browser.typeInto(['symbols-count', 'max'], '4');

        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.ATTRIBUTE('\\d')));
        await this.browser.assertImage('attribute_params');
    });

    it('Создание текстового локализуемого атрибута', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto('text', {waitRender: true});
        await this.browser.typeInto('code', 'test_text_localizable_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');

        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.ATTRIBUTE('\\d')));
        await this.browser.assertImage('attribute_params');
    });

    it('Создание атрибута типа "Список"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto('select', {waitRender: true});
        await this.browser.typeInto('code', 'test_select_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto(['select-option', 'select-option-add'], {waitRender: true});
        await this.browser.typeInto(
            ['select-option', 'select-option-header', 'select-option-code'],
            'select_option_code'
        );

        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.ATTRIBUTE('\\d')));
        await this.browser.assertImage('attribute_params');
    });

    it('Создание атрибута типа "Множественный Список"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto('multiselect', {waitRender: true});
        await this.browser.typeInto('code', 'test_multiselect_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto(['select-option', 'select-option-add'], {waitRender: true});
        await this.browser.typeInto(
            ['select-option', 'select-option-header', 'select-option-code'],
            'select_option_code'
        );

        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.ATTRIBUTE('\\d')));
        await this.browser.assertImage('attribute_params');
    });

    it('Создание атрибута типа "Изображение"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto('image', {waitRender: true});
        await this.browser.typeInto('code', 'test_image_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.ATTRIBUTE('\\d')));
        await this.browser.assertImage('attribute-base_params');
    });

    it('Создание множественного атрибута типа "Изображение" с ограничением на кол-во значений', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto('image', {waitRender: true});
        await this.browser.typeInto('code', 'test_image_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto('is-array', {waitRender: true});
        await this.browser.typeInto('max-array-size', '2');
        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.ATTRIBUTE('\\d')));
        await this.browser.assertImage('attribute-base_params');
    });

    it('Просмотр созданного атрибута в таблице', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto('number', {waitRender: true});
        await this.browser.typeInto('code', 'test_number_multiple_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto('is-array');

        await this.browser.clickInto('submit-button', {waitNavigation: true});

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES);
        await this.browser.typeInto(['action-bar', 'search'], 'test_number_multiple_attribute_code');

        await this.browser.waitForTestIdSelectorNotInDom('attribute_table__spinner');
        await this.browser.waitUntilRendered();

        await this.browser.assertImage('attributes-table_table');
    });

    it('Смена языка интерфейса на странице создания атрибута (Россия)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('ui-lang-select', {waitRender: true});
        await this.browser.clickInto(['ui-lang-select_dropdown-menu', 'fr'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Значение Is immutable по-умолчанию "выключен"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.waitForTestIdSelectorAriaNotChecked('is-immutable');
    });

    it('Создать неизменный множественный атрибут', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type');
        await this.browser.clickInto(['attribute-type_dropdown-menu', 'string']);
        await this.browser.typeInto('code', 'test_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto('is-immutable');
        await this.browser.clickInto('is-array');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});

        await this.browser.assertImage('is-immutable');
        await this.browser.waitForTestIdSelectorAriaChecked('is-array');
    });

    it('Нельзя сделать неизменным обычный атрибут', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.typeInto('code', 'test_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});

        await this.browser.waitForTestIdSelectorDisabled('is-immutable');
    });

    it('Нельзя сделать обычным неизменный атрибут', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.typeInto('code', 'test_attribute_code');
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');
        await this.browser.clickInto('is-immutable');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitNavigation: true, waitRender: true});

        await this.browser.waitForTestIdSelectorDisabled('is-immutable');
    });

    it('Ввод некорректного значения параметра Ссылка на задачу', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.BOOLEAN});
        await this.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/FOOBARBAZ-666', {clear: true});
        await this.browser.clickInto('submit-button');
        await this.browser.assertImage('ticket-parameter_container');
    });

    // eslint-disable-next-line max-len
    it('Ввод отрицательного значения в максимальное количество возможных значений множественного атрибута', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.STRING});
        await this.browser.clickInto('is-array');
        await this.browser.typeInto('max-array-size', '-1', {clear: true});
        await this.browser.clickInto('submit-button');
        await this.browser.assertImage('max-array-size_container');
    });

    // eslint-disable-next-line max-len
    it('Ввод отрицательных значений в диапазон Числового атрибута с выключенным параметром "Может быть отрицательным"', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.NUMBER});
        await this.browser.clickInto('can-be-negative');
        await this.browser.typeInto(['symbols-count', 'min'], '-1', {clear: true});
        await this.browser.clickInto('submit-button');
        await this.browser.assertImage('symbols-count_container');
    });

    // eslint-disable-next-line max-len
    it('Ввод дробных значений в диапазон Числового атрибута с выключенным параметром "Может быть десятичной дробью"', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.NUMBER});
        await this.browser.typeInto(['symbols-count', 'min'], '1.25', {clear: true});
        await this.browser.clickInto('can-be-decimal');
        await this.browser.clickInto('submit-button');
        await this.browser.assertImage('symbols-count_container');
    });

    // eslint-disable-next-line max-len
    it('Ввод минимального значения диапазона Числового атрибута бОльшего, чем максимальное значение', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.NUMBER});
        await this.browser.typeInto(['symbols-count', 'min'], '2', {clear: true});
        await this.browser.typeInto(['symbols-count', 'max'], '1', {clear: true});
        await this.browser.clickInto('submit-button');
        await this.browser.assertImage('symbols-count_container');
    });

    it('При выборе типа атрибута Текстовая строка флаг Локализуемый по умолчанию включен', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto('string', {waitRender: true});
        await this.browser.assertImage('is-localizable_container');
    });

    it('При выборе типа атрибута Многострочный текст флаг Локализуемый по умолчанию включен', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
        await this.browser.clickInto('attribute-type', {waitRender: true});
        await this.browser.clickInto('text', {waitRender: true});
        await this.browser.assertImage('is-localizable_container');
    });

    it('Ввод отрицательных значений в количество символов атрибута Текстовая строка', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.STRING});
        await this.browser.typeInto(['symbols-count', 'min'], '-1', {clear: true});
        await this.browser.clickInto('submit-button');
        await this.browser.assertImage('symbols-count_container');
    });

    it('Ввод отрицательных значений в количество символов атрибута Многострочный текст', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.TEXT});
        await this.browser.typeInto(['symbols-count', 'max'], '-1', {clear: true});
        await this.browser.clickInto('submit-button');
        await this.browser.assertImage('symbols-count_container');
    });

    it('Ввод дробных значений в количество символов атрибута Текстовая строка', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.STRING});
        await this.browser.typeInto(['symbols-count', 'min'], '1.25', {clear: true});
        await this.browser.clickInto('submit-button');
        await this.browser.assertImage('symbols-count_container');
    });

    it('Ввод дробных значений в количество символов атрибута Многострочный текст', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.TEXT});
        await this.browser.typeInto(['symbols-count', 'max'], '1.25', {clear: true});
        await this.browser.clickInto('submit-button');
        await this.browser.assertImage('symbols-count_container');
    });

    // eslint-disable-next-line max-len
    it('Ввод минимального значения количество символов атрибута Текстовая строка бОльшего, чем максимальное значение', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.STRING});
        await this.browser.typeInto(['symbols-count', 'min'], '2', {clear: true});
        await this.browser.typeInto(['symbols-count', 'max'], '1', {clear: true});
        await this.browser.clickInto('submit-button');
        await this.browser.assertImage('symbols-count_container');
    });

    // eslint-disable-next-line max-len
    it('Ввод минимального значения количество символов атрибута Многострочный текст бОльшего, чем максимальное значение', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.STRING});
        await this.browser.typeInto(['symbols-count', 'min'], '2', {clear: true});
        await this.browser.typeInto(['symbols-count', 'max'], '1', {clear: true});
        await this.browser.clickInto('submit-button');
        await this.browser.assertImage('symbols-count_container');
    });

    it('Ввод некорректного значения кода опции атрибута Выпадающий список', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.SELECT});
        await this.browser.clickInto('select-option-add', {waitRender: true});
        await this.browser.typeInto('select-option-code', 'йцукен');
        await this.browser.clickInto('submit-button');
        await this.browser.assertImage('attribute-additional_params');
    });

    it('Ввод некорректного значения кода опции атрибута Множественный список', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.MULTISELECT});
        await this.browser.clickInto('select-option-add', {waitRender: true});
        await this.browser.typeInto('select-option-code', 'йцукен');
        await this.browser.clickInto('submit-button');
        await this.browser.assertImage('attribute-additional_params');
    });

    it('Включение неизменности выключает локализуемость', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.STRING});
        await this.browser.waitForTestIdSelectorAriaChecked('is-localizable');
        await this.browser.waitForTestIdSelectorAriaNotChecked('is-immutable');

        await this.browser.clickInto('is-immutable');

        await this.browser.waitForTestIdSelectorAriaChecked('is-immutable');
        await this.browser.assertImage('is-immutable');
        await this.browser.waitForTestIdSelectorAriaNotChecked('is-localizable');
        await this.browser.assertImage('is-localizable');
    });

    it('Включение локализуемости выключает множественность и неизменность', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.STRING});
        await this.browser.clickInto('is-array');
        await this.browser.clickInto('is-immutable');

        await this.browser.waitForTestIdSelectorAriaChecked('is-array');
        await this.browser.waitForTestIdSelectorAriaChecked('is-immutable');
        await this.browser.waitForTestIdSelectorAriaNotChecked('is-localizable');

        await this.browser.clickInto('is-localizable');

        await this.browser.waitForTestIdSelectorAriaNotChecked('is-array');
        await this.browser.assertImage('is-array');
        await this.browser.waitForTestIdSelectorAriaNotChecked('is-immutable');
        await this.browser.assertImage('is-immutable');
        await this.browser.waitForTestIdSelectorAriaChecked('is-localizable');
        await this.browser.assertImage('is-localizable');
    });

    it('Нельзя создать атрибут-изображения, не выбрав ни один поддерживаемый формат файлов', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.IMAGE});

        await this.browser.clickInto('additional.allowedImageExtensions', {waitRender: true});
        await this.browser.clickInto(['additional.allowedImageExtensions_dropdown-menu', 'png']);
        await this.browser.clickInto(['additional.allowedImageExtensions_dropdown-menu', 'jpg']);
        await this.browser.clickInto(['additional.allowedImageExtensions_dropdown-menu', 'jpeg']);

        await this.browser.clickInto('submit-button');

        await this.browser.assertImage('additional.allowedImageExtensions_container');
    });

    it('Смена допустимого формата для атрибута-изображения', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.IMAGE});

        await this.browser.clickInto('additional.allowedImageExtensions', {waitRender: true});
        await this.browser.clickInto(['additional.allowedImageExtensions_dropdown-menu', 'jpeg']);
        await this.browser.clickInto(['additional.allowedImageExtensions_dropdown-menu', 'gif']);

        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.assertImage('allowed-image-extensions_container');
    });

    it('При создании атрибута поле подтверждаемости задизейблено', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.IMAGE});

        await this.browser.waitForTestIdSelectorDisabled([
            'attribute-base_params',
            'is-confirmable_container',
            'is-confirmable'
        ]);
        await this.browser.assertImage(['attribute-base_params', 'is-confirmable_container']);
    });

    it('МП: "Необходимо подтверждать" доступно в форме создания атрибута', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        await openPageAndFillDefaults(this, {type: AttributeType.IMAGE});

        await this.browser.waitForTestIdSelectorEnabled([
            'attribute-base_params',
            'is-confirmable_container',
            'is-confirmable'
        ]);
    });

    it('Показываются дополнительные параметры для атрибута типа "видео"', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.VIDEO});

        await this.browser.assertImage('attribute-additional_params', {removeShadows: true});
    });

    it('Создать обычный атрибут типа "Видео"', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.VIDEO});

        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.assertImage('base-layout-content');

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES);
        await this.browser.typeInto(['action-bar', 'search'], 'test_video_attribute_code');

        await this.browser.waitForTestIdSelectorNotInDom('attribute_table__spinner');
        await this.browser.waitUntilRendered();

        await this.browser.assertImage('attributes-table_table');
    });

    it('Создать множественный атрибут типа "Видео" с ограничением на количество равным 3', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.VIDEO});
        await this.browser.clickInto('is-array');
        await this.browser.typeInto('max-array-size', '3', {clear: true});

        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.assertImage('base-layout-content');

        await this.browser.openPage(ROUTES.CLIENT.ATTRIBUTES);
        await this.browser.typeInto(['action-bar', 'search'], 'test_video_attribute_code');

        await this.browser.waitForTestIdSelectorNotInDom('attribute_table__spinner');
        await this.browser.waitUntilRendered();

        await this.browser.assertImage('attributes-table_table');
    });

    it('Нельзя создать атрибут типа видео без выбранного формата', async function () {
        await openPageAndFillDefaults(this, {type: AttributeType.VIDEO});

        await this.browser.clickInto('additional.allowedVideoExtensions', {waitRender: true});
        await this.browser.clickInto(['additional.allowedVideoExtensions_dropdown-menu', 'mp4']);

        await this.browser.clickInto('submit-button');

        await this.browser.assertImage('additional.allowedVideoExtensions_container');
    });
});
