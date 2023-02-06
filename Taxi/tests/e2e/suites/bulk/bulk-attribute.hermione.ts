import {openChangeAttributesBulkPage, selectAttribute} from 'tests/e2e/helper/bulk';
import {attributes} from 'tests/e2e/seed-db-map';
import {addAttributeToInfomodelByCode} from 'tests/e2e/utils/add-attribute-to-infomodel-by-code';
import setAttributeConfirmationValue from 'tests/e2e/utils/confirm-attribute';
import {createAttribute} from 'tests/e2e/utils/create-attribute';
import makeAttributeConfirmable from 'tests/e2e/utils/make-attribute-confirmable';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {AttributeType} from 'types/attribute';

describe('Балковые действия для атрибутов', function () {
    async function commitAndAssertChanges(ctx: Hermione.TestContext) {
        await ctx.browser.clickInto(['header-panel', 'submit-button']);
        await ctx.browser.waitForTestIdSelectorInDom('import-info-update');

        await ctx.browser.clickInto(['header-panel', 'submit-button']);
        await ctx.browser.waitForTestIdSelectorInDom('bulk-success-alert');
        await ctx.browser.clickInto('import-info-update', {waitRender: true});

        await ctx.browser.assertImage('import-info-update');
    }

    it('Изменить логический атрибут, Россия', async function () {
        await openChangeAttributesBulkPage(this, [10000001]);
        await selectAttribute(this, 'boolean_attribute_code_0_0');

        await this.browser.clickInto(['attributes-list', 'boolean_attribute_code_0_0_on']);
        await commitAndAssertChanges(this);
    });

    it('Изменить числовой атрибут, Великобритания', async function () {
        await openChangeAttributesBulkPage(this, [10000051], {region: 'gb'});
        await selectAttribute(this, 'number_attribute_code_3_0');

        await this.browser.typeInto(['attributes-list', 'number_attribute_code_3_0'], '666');
        await commitAndAssertChanges(this);
    });

    it('Изменить строковый атрибут, Израиль', async function () {
        await openChangeAttributesBulkPage(this, [10000151], {region: 'il'});
        await selectAttribute(this, 'string_attribute_code_5_0');

        await this.browser.typeInto(['attributes-list', 'string_attribute_code_5_0'], 'foo bar baz');
        await commitAndAssertChanges(this);
    });

    it('Изменить атрибут–текст, Франция', async function () {
        await openChangeAttributesBulkPage(this, [10000101], {region: 'fr'});
        await selectAttribute(this, 'text_attribute_code_6_0');

        await this.browser.typeInto(['attributes-list', 'text_attribute_code_6_0'], 'foo1 bar1 baz1 foo2 bar2 baz2');
        await commitAndAssertChanges(this);
    });

    it('Изменить атрибут-список', async function () {
        await openChangeAttributesBulkPage(this, [10000001]);
        await selectAttribute(this, 'select_attribute_code_4_0');

        await this.browser.clickInto(['attributes-list', 'select_attribute_code_4_0'], {waitRender: true});
        await this.browser.clickInto(['select_attribute_code_4_0_dropdown-menu', 'attribute_option_code_14_2'], {
            waitRender: true
        });

        await commitAndAssertChanges(this);
    });

    it('Заменить локализуемый атрибут, Франция', async function () {
        await openChangeAttributesBulkPage(this, [10000101], {region: 'fr'});
        await selectAttribute(this, 'longName');

        await this.browser.typeInto(['attributes-list', 'longName_en'], 'The Foo bar');
        await this.browser.typeInto(['attributes-list', 'longName_fr'], 'Le F`oo bar');

        await commitAndAssertChanges(this);
    });

    it('Отсутствующий в ИМ товаров атрибут задизейблен', async function () {
        await openChangeAttributesBulkPage(this, [10000009]);

        await this.browser.clickInto('add-attribute', {waitForClickable: true, waitRender: true});
        await this.browser.typeInto(['select-user-attributes', 'search'], 'text_attribute_code_6_1');
        await this.browser.waitUntilRendered();
        await this.browser.clickInto(['select-user-attributes', 'text_attribute_code_6_1'], {waitRender: true});

        await this.browser.assertImage('select-user-attributes');
    });

    it('Нельзя изменить значение атрибута балком, если его нет ни у одного из выбранных товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS);
        await this.browser.clickInto(['products-table-row_10000001', 'checkbox']);
        await this.browser.clickInto(['products-table-row_10000003', 'checkbox']);
        await this.browser.clickInto(['products-table-row_10000006', 'checkbox']);
        await this.browser.clickInto(['products-bottom-panel', 'bulk-edit'], {waitRender: true, waitNavigation: true});
        await this.browser.clickInto('change-attributes-values');

        await this.browser.clickInto('add-attribute', {waitForClickable: true, waitRender: true});

        await this.browser.clickInto(['select-user-attributes', 'boolean_attribute_code_0_0'], {waitRender: true});
        await this.browser.clickInto(['select-user-attributes', 'boolean_attribute_code_0_1'], {waitRender: true});
        // Этот атрибут задизейблен, клик ничего не делает, не должен отображаться после клика на Подтвердить
        await this.browser.clickInto(['select-user-attributes', 'image_attribute_code_1_0'], {waitRender: true});

        await this.browser.clickInto('confirm-select', {waitRender: true});

        await this.browser.assertImage('base-layout');
    });

    it('Нельзя изменить картинку', async function () {
        await openChangeAttributesBulkPage(this, [10000001]);

        await this.browser.clickInto('add-attribute', {waitForClickable: true, waitRender: true});
        await this.browser.typeInto(['select-user-attributes', 'search'], 'image');
        await this.browser.waitUntilRendered();
        await this.browser.clickInto(['select-user-attributes', 'image']);

        await this.browser.assertImage('select-user-attributes', {removeShadows: true});
    });

    it('Нельзя изменить штрихкод', async function () {
        await openChangeAttributesBulkPage(this, [10000001]);

        await this.browser.clickInto('add-attribute', {waitForClickable: true, waitRender: true});
        await this.browser.typeInto(['select-user-attributes', 'search'], 'barcode');
        await this.browser.waitUntilRendered();
        await this.browser.clickInto(['select-user-attributes', 'barcode']);

        await this.browser.assertImage('select-user-attributes', {removeShadows: true});
    });

    it('Удалить значение множественного строкового атрибута, Россия', async function () {
        await openChangeAttributesBulkPage(this, [10000001]);
        await selectAttribute(this, 'string_attribute_code_5_1');

        await this.browser.clickInto('select-modification-type', {waitRender: true});
        await this.browser.clickInto(['select-modification-type_dropdown-menu', 'remove'], {waitRender: true});

        await this.browser.clickInto('add_new_string_attribute_code_5_1');
        await this.browser.typeInto('string_attribute_code_5_1__0', 'счастливой людей из-за когда вами или.');

        await commitAndAssertChanges(this);
    });

    it('Удалить значение множественного числового атрибута, Великобритания', async function () {
        await openChangeAttributesBulkPage(this, [10000051], {region: 'gb'});
        await selectAttribute(this, 'number_attribute_code_3_1');

        await this.browser.clickInto('select-modification-type', {waitRender: true});
        await this.browser.clickInto(['select-modification-type_dropdown-menu', 'remove'], {waitRender: true});

        await this.browser.clickInto('add_new_number_attribute_code_3_1');
        await this.browser.typeInto('number_attribute_code_3_1__0', '18');

        await commitAndAssertChanges(this);
    });

    it('Удалить значение множественного текстового атрибута, Израиль', async function () {
        await openChangeAttributesBulkPage(this, [10000152], {region: 'il'});
        await selectAttribute(this, 'text_attribute_code_6_1');

        await this.browser.clickInto('select-modification-type', {waitRender: true});
        await this.browser.clickInto(['select-modification-type_dropdown-menu', 'remove'], {waitRender: true});

        await this.browser.clickInto('add_new_text_attribute_code_6_1');
        await this.browser.typeInto('text_attribute_code_6_1__0', 'وكأنه إلى مؤقتة الخصوص، نفس كما أن حقيقية مفيد.');

        await commitAndAssertChanges(this);
    });

    it('Удалить значение множественного списка, Франция', async function () {
        await openChangeAttributesBulkPage(this, [10000105], {region: 'fr'});
        await selectAttribute(this, 'multiselect_attribute_code_2_0');

        await this.browser.clickInto('select-modification-type', {waitRender: true});
        await this.browser.clickInto(['select-modification-type_dropdown-menu', 'remove'], {waitRender: true});

        await this.browser.clickInto(['attributes-list', 'multiselect_attribute_code_2_0'], {waitRender: true});
        await this.browser.clickInto(['multiselect_attribute_code_2_0_dropdown-menu', 'attribute_option_code_10_1'], {
            waitRender: true
        });

        await commitAndAssertChanges(this);
    });

    it('Добавить значение множественной строки, Россия', async function () {
        await openChangeAttributesBulkPage(this, [10000001]);
        await selectAttribute(this, 'string_attribute_code_5_1');

        await this.browser.clickInto('select-modification-type', {waitRender: true});
        await this.browser.clickInto(['select-modification-type_dropdown-menu', 'add'], {waitRender: true});

        await this.browser.clickInto('add_new_string_attribute_code_5_1');
        await this.browser.typeInto('string_attribute_code_5_1__0', 'фу бар баз');

        await commitAndAssertChanges(this);
    });

    it('Добавить значение множественного числа, Великобритания', async function () {
        await openChangeAttributesBulkPage(this, [10000051], {region: 'gb'});
        await selectAttribute(this, 'number_attribute_code_3_1');

        await this.browser.clickInto('select-modification-type', {waitRender: true});
        await this.browser.clickInto(['select-modification-type_dropdown-menu', 'add'], {waitRender: true});

        await this.browser.clickInto('add_new_number_attribute_code_3_1');
        await this.browser.typeInto('number_attribute_code_3_1__0', '666');

        await commitAndAssertChanges(this);
    });

    it('Добавить значение множественного текста, Израиль', async function () {
        await openChangeAttributesBulkPage(this, [10000152], {region: 'il'});
        await selectAttribute(this, 'text_attribute_code_6_1');

        await this.browser.clickInto('select-modification-type', {waitRender: true});
        await this.browser.clickInto(['select-modification-type_dropdown-menu', 'add'], {waitRender: true});

        await this.browser.clickInto('add_new_text_attribute_code_6_1');
        // TODO бесполезный тест, нового значения на скриншоте все равно не видно
        await this.browser.typeInto('text_attribute_code_6_1__0', 'foo bar baz');

        await commitAndAssertChanges(this);
    });

    it('Добавить значение множественного списка, Франция', async function () {
        await openChangeAttributesBulkPage(this, [10000104], {region: 'fr'});
        await selectAttribute(this, 'multiselect_attribute_code_2_0');

        await this.browser.clickInto('select-modification-type', {waitRender: true});
        await this.browser.clickInto(['select-modification-type_dropdown-menu', 'add'], {waitRender: true});

        await this.browser.clickInto(['attributes-list', 'multiselect_attribute_code_2_0'], {waitRender: true});
        await this.browser.clickInto(['multiselect_attribute_code_2_0_dropdown-menu', 'attribute_option_code_10_3'], {
            waitRender: true
        });

        await commitAndAssertChanges(this);
    });

    it('Выбор максимального количества атрибутов для всех товаров, Россия', async function () {
        const attributeCodesToSelect = [
            'longName',
            'markCount',
            'markCountUnit',
            'boolean_attribute_code_0_0',
            'boolean_attribute_code_0_1',
            'multiselect_attribute_code_2_0',
            'multiselect_attribute_code_2_1',
            'number_attribute_code_3_0',
            'number_attribute_code_3_1',
            'select_attribute_code_4_0'
        ];

        await openChangeAttributesBulkPage(this, 'all', {region: 'ru'});
        await this.browser.clickInto('add-attribute', {waitForClickable: true, waitRender: true});

        for (const attrCode of attributeCodesToSelect) {
            await this.browser.clickInto(['select-user-attributes', attrCode], {waitRender: true});
        }

        await this.browser.clickInto(['select-user-attributes', 'shortNameLoc'], {waitRender: true});
        await this.browser.assertImage('select-user-attributes');
    });

    it('Выбор максимального количества атрибутов для всех товаров, Израиль', async function () {
        const attributeCodesToSelect = [
            'longName',
            'markCount',
            'markCountUnit',
            'boolean_attribute_code_0_0',
            'boolean_attribute_code_0_1',
            'multiselect_attribute_code_2_0',
            'multiselect_attribute_code_2_1',
            'number_attribute_code_3_0'
        ];

        await openChangeAttributesBulkPage(this, 'all', {region: 'il'});
        await this.browser.clickInto('add-attribute', {waitForClickable: true, waitRender: true});

        for (const attrCode of attributeCodesToSelect) {
            await this.browser.clickInto(['select-user-attributes', attrCode], {waitRender: true});
        }

        await this.browser.clickInto(['select-user-attributes', 'shortNameLoc'], {waitRender: true});
        await this.browser.assertImage('select-user-attributes');
    });

    it('Изменить на false пустой атрибут через балк', async function () {
        await openChangeAttributesBulkPage(this, [10000001]);
        await selectAttribute(this, 'boolean_attribute_code_0_1');

        await this.browser.clickInto('boolean_attribute_code_0_1_off');
        await commitAndAssertChanges(this);
    });

    it('Изменить на true пустой атрибут через балк', async function () {
        await openChangeAttributesBulkPage(this, [10000001]);
        await selectAttribute(this, 'boolean_attribute_code_0_1');

        await this.browser.clickInto('boolean_attribute_code_0_1_on');
        await commitAndAssertChanges(this);
    });

    it('Очистить false-атрибут через балк', async function () {
        await openChangeAttributesBulkPage(this, [10000001]);
        await selectAttribute(this, 'boolean_attribute_code_0_0');

        await commitAndAssertChanges(this);
    });

    it('Очистить true-атрибут через балк', async function () {
        await openChangeAttributesBulkPage(this, [10000002]);
        await selectAttribute(this, 'boolean_attribute_code_0_0');

        await commitAndAssertChanges(this);
    });

    it('Установить значение "не определен" атрибута в два клика', async function () {
        await openChangeAttributesBulkPage(this, [10000002]);
        await selectAttribute(this, 'boolean_attribute_code_0_0');

        await this.browser.clickInto('boolean_attribute_code_0_0_on');
        await this.browser.clickInto('boolean_attribute_code_0_0_unset');
        await commitAndAssertChanges(this);
    });

    it('Неизменный атрибут можно задать через балк', async function () {
        await openChangeAttributesBulkPage(this, [10000001]);
        await selectAttribute(this, 'boolean_attribute_code_0_1');

        await this.browser.clickInto('boolean_attribute_code_0_1_on');

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.clickInto('import-info-update', {waitForClickable: true});

        await this.browser.assertImage('import-info-update');
    });

    it('Неизменный атрибут нельзя изменить через балк', async function () {
        await openChangeAttributesBulkPage(this, [10000005]);
        await selectAttribute(this, 'boolean_attribute_code_0_1');

        await this.browser.clickInto('boolean_attribute_code_0_1_off');

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.clickInto('import-info-ignore', {waitForClickable: true});
        const tooltipIcon = await this.browser.findByTestId('import-cell-tooltip-help-icon');
        await tooltipIcon.moveTo();

        await this.browser.assertImage('import-info-ignore');
    });

    it('"Отсутствую изменения", если в балке менялись только неизменные атрибуты', async function () {
        await openChangeAttributesBulkPage(this, [10000020]);
        await selectAttribute(this, 'string_attribute_code_5_2_loc');
        await selectAttribute(this, 'boolean_attribute_code_0_1');

        await this.browser.typeInto('string_attribute_code_5_2_loc_ru', 'some text');
        await this.browser.clickInto('boolean_attribute_code_0_1_on');

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.clickInto('import-info-ignore', {waitForClickable: true});
        const tooltipIcon = await this.browser.findByTestId('import-cell-tooltip-help-icon');
        await tooltipIcon.moveTo();

        await this.browser.assertImage('import-info-ignore');
    });

    it('Очистить локализуемый атрибут, Франция', async function () {
        await openChangeAttributesBulkPage(this, [10000113], {region: 'fr'});
        await selectAttribute(this, 'text_attribute_code_6_2_loc');

        await this.browser.typeInto(['attributes-list', 'text_attribute_code_6_2_loc_en'], '', {clear: true});
        await this.browser.typeInto(['attributes-list', 'text_attribute_code_6_2_loc_fr'], '', {clear: true});

        await commitAndAssertChanges(this);

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000113), {region: 'fr'});
        await this.browser.assertImage('text_attribute_code_6_2_loc_en');
        await this.browser.assertImage('text_attribute_code_6_2_loc_fr');
    });

    it('Страница массового изменения атрибутов', async function () {
        await openChangeAttributesBulkPage(this, [10000001, 10000002]);

        await this.browser.assertImage('base-layout');
    });

    it('Тип номенклатуры товара в Израиле нельзя очистить через балк', async function () {
        await openChangeAttributesBulkPage(this, [10000151], {region: 'il'});
        await selectAttribute(this, 'nomenclatureType');

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.assertImage('input_wrapper-nomenclatureType');
    });

    it('Нельзя изменить подтвержденный атрибут через балк', async function () {
        await makeAttributeConfirmable(this.browser, attributes.boolean_attribute_code_0_0);
        await setAttributeConfirmationValue({
            browser: this.browser,
            productIdentifier: 10000001,
            attributeId: attributes.boolean_attribute_code_0_0
        });

        await openChangeAttributesBulkPage(this, [10000001]);
        await selectAttribute(this, 'boolean_attribute_code_0_0');

        await this.browser.clickInto(['attributes-list', 'boolean_attribute_code_0_0_on']);

        await this.browser.clickInto(['header-panel', 'submit-button']);

        await this.browser.waitForTestIdSelectorInDom('import-info-not-upload');
        await this.browser.clickInto(['import-info-not-upload', 'expand-icon'], {waitRender: true});
        const tooltipIcon = await this.browser.findByTestId('import-cell-tooltip-help-icon');
        await tooltipIcon.moveTo();

        await this.browser.assertImage('import-info-not-upload');
    });

    it('Можно изменить подтверждаемый, но не подтвержденный атрибут через балк', async function () {
        await makeAttributeConfirmable(this.browser, attributes.boolean_attribute_code_0_0);

        await openChangeAttributesBulkPage(this, [10000001]);
        await selectAttribute(this, 'boolean_attribute_code_0_0');

        await this.browser.clickInto(['attributes-list', 'boolean_attribute_code_0_0_on']);

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await commitAndAssertChanges(this);
    });

    it('МП: Неподтвержденные атрибуты меняются через балк', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        await makeAttributeConfirmable(this.browser, attributes.boolean_attribute_code_0_0);

        await openChangeAttributesBulkPage(this, [10000001]);
        await selectAttribute(this, 'boolean_attribute_code_0_0');

        await this.browser.clickInto(['attributes-list', 'boolean_attribute_code_0_0_on']);

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await commitAndAssertChanges(this);
    });

    it('МП: Подтвержденные атрибуты не меняются через балк', async function () {
        await this.browser.addUserRole({rules: {canConfirm: true}});

        await makeAttributeConfirmable(this.browser, attributes.boolean_attribute_code_0_0);
        await setAttributeConfirmationValue({
            browser: this.browser,
            productIdentifier: 10000001,
            attributeId: attributes.boolean_attribute_code_0_0
        });

        await openChangeAttributesBulkPage(this, [10000001]);
        await selectAttribute(this, 'boolean_attribute_code_0_0');

        await this.browser.clickInto(['attributes-list', 'boolean_attribute_code_0_0_on']);

        await this.browser.clickInto(['header-panel', 'submit-button']);

        await this.browser.waitForTestIdSelectorInDom('import-info-not-upload');
        await this.browser.clickInto(['import-info-not-upload', 'expand-icon'], {waitRender: true});
        const tooltipIcon = await this.browser.findByTestId('import-cell-tooltip-help-icon');
        await tooltipIcon.moveTo();

        await this.browser.assertImage('import-info-not-upload');
    });

    it('Нельзя изменить видео', async function () {
        await createAttribute(this, {type: AttributeType.VIDEO});
        await addAttributeToInfomodelByCode(this, {code: 'test_video_attribute_code'});

        await openChangeAttributesBulkPage(this, [10000001]);

        await this.browser.clickInto('add-attribute', {waitForClickable: true, waitRender: true});
        await this.browser.typeInto(['select-user-attributes', 'search'], 'video');
        await this.browser.waitUntilRendered();

        await this.browser.assertImage('select-user-attributes', {removeShadows: true});
    });
});
