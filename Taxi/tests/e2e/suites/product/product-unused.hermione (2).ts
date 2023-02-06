import {openChangeAttributesBulkPage} from 'tests/e2e/helper/bulk';
import {parseSpreadSheetJSON} from 'tests/e2e/helper/parse-spreadsheet';
import {infoModels, masterCategories} from 'tests/e2e/seed-db-map';
import getFixturePath from 'tests/e2e/utils/fixture';
import makeDataTestIdSelector from 'tests/e2e/utils/make-data-test-id-selector';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

async function changeMasterCategory(ctx: Hermione.TestContext, code: string, name: string, inactive?: boolean) {
    await ctx.browser.clickInto('parent-category-modal__input', {waitRender: true});
    await ctx.browser.waitForTestIdSelectorInDom('parent-category-modal__tree-list');
    if (inactive) {
        await ctx.browser.clickInto(['hide-inactive']);
    }
    await ctx.browser.typeInto(['parent-category-modal__tree-list', 'search_input'], name, {clear: true});
    await ctx.browser.clickInto([`row_${code}`, 'title'], {waitRender: true});
    await ctx.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});
    await ctx.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
    await ctx.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);
}

describe('Неиспользуемые атрибуты', function () {
    it('Смена мастер-категории с появлением неиспользуемых атрибутов (Израиле)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000151), {region: 'il'});
        await changeMasterCategory(this, 'master_category_code_59_0', 'Которого воспользоваться');
        await this.browser.assertImage('unused-attributes', {removeShadows: true});
    });

    it('Очистить неиспользуемый атрибут-изображение через интерфейс', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await changeMasterCategory(this, 'master_category_code_29_0', 'Возлюбил а');
        await this.browser.clickInto(['image_attribute_code_1_1-array', 'image-drag-0', 'delete-image'], {
            waitRender: true
        });
        await this.browser.clickInto(['image_attribute_code_1_1-array', 'image-drag-1', 'delete-image'], {
            waitRender: true
        });
        await this.browser.clickInto(['image_attribute_code_1_1-array', 'image-drag-2', 'delete-image'], {
            waitRender: true
        });
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.assertImage('unused-attributes', {removeShadows: true});
    });

    it('Редактировать неиспользуемый множественный атрибут-список через интерфейс (Франция)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000104), {region: 'fr', dataLang: 'en'});
        await changeMasterCategory(this, 'master_category_code_51_1', 'Vel ut');

        await this.browser.clickInto(['multiselect_attribute_code_2_0'], {waitRender: true});
        await this.browser.clickInto(['multiselect_attribute_code_2_0_dropdown-menu', 'attribute_option_code_10_2'], {
            waitRender: true
        });
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.assertImage('unused-attributes', {removeShadows: true});
    });

    it('В таблице товаров не видны значения неиспользуемых атрибутов', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await changeMasterCategory(this, 'master_category_code_29_0', 'Возлюбил а');

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {
                search: '10000001',
                columnIds: ['longNameLoc', 'barcode', 'image', 'multiselect_attribute_code_2_1'].join()
            }
        });
        await this.browser.assertImage(['products-table', '\\tbody']);
    });

    it('Значение неиспользуемого атрибута не теряется', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await changeMasterCategory(this, 'master_category_code_29_0', 'Возлюбил а');

        await this.browser.clickInto('infomodel-link', {waitRender: true, waitNavigation: true});
        await this.browser.clickInto('\\#rc-tabs-1-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['attributes-search'], {waitRender: true});
        await this.browser.typeInto('attributes-search', 'number_attribute_code_3_1');
        await this.browser.waitUntilRendered();
        await this.browser.clickInto(['attribute-select-virtual-list', 'number_attribute_code_3_1']);
        await this.browser.clickInto('im-user_attributes-table', {
            waitRender: true
        });
        await this.browser.clickInto('submit-button');

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.assertImage('attribute_group_code_2', {removeShadows: true});
    });

    // eslint-disable-next-line max-len
    it('Одновременная смена мастер-категории и изменение неиспользуемого атрибута через импорт (Франция)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000104), {region: 'fr', dataLang: 'en'});
        await changeMasterCategory(this, 'master_category_code_51_1', 'Vel ut');

        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS, {region: 'fr', dataLang: 'en'});
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-unused-change-mc-and-attribute.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('import-success-alert', {timeout: 30_000});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000104), {region: 'fr', dataLang: 'en'});
        await this.browser.assertImage('product_view', {
            compositeImage: true,
            ignoreElements: [makeDataTestIdSelector('basic-attributes'), makeDataTestIdSelector('product-image')]
        });
    });

    it('Смена инфомодели у мастер-категории с появлением неиспользуемых атрибутов (Великобритания)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.gb.master_category_code_35_0), {
            region: 'gb'
        });
        await this.browser.clickInto('info-model-select', {waitRender: true});
        await this.browser.clickInto('im_node_compatible_info_model_code_2_9', {waitRender: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000051), {region: 'gb'});
        await this.browser.assertImage('unused-attributes', {removeShadows: true});
    });

    it('Нельзя поменять значение неиспользуемого атрибута через балк', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await changeMasterCategory(this, 'master_category_code_29_0', 'Возлюбил а');

        await openChangeAttributesBulkPage(this, [10000001], {
            queryParams: {
                search: '10000001',
                columnIds: ['longNameLoc', 'barcode', 'image', 'number_attribute_code_3_1'].join()
            }
        });
        await this.browser.clickInto('add-attribute', {waitForClickable: true, waitRender: true});
        await this.browser.typeInto(['select-user-attributes', 'search'], 'number_attribute_code_3_1', {clear: true});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('number_attribute_code_3_1');
    });

    it('Редактировать неиспользуемый текстовый атрибут через импорт (Израиль)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000151), {region: 'il', dataLang: 'en'});
        await changeMasterCategory(this, 'master_category_code_61_1', 'Aut molestiae consequatur', true);

        await this.browser.typeInto('string_attribute_code_5_0', '12345', {clear: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.assertImage('unused-attributes', {removeShadows: true});
    });

    it('Очистить неиспользуемый числовой атрибут через импорт', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await changeMasterCategory(this, 'master_category_code_31_1', 'Стал приносят', true);

        await this.browser.typeInto('number_attribute_code_3_0', '', {clear: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.assertImage('unused-attributes', {removeShadows: true});
    });

    it('Удаление атрибута из инфомодели', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_14));
        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
        await this.browser.clickInto(['infomodel-groups-table', 'im_attribute-group_row_attribute_group_code_3']);
        await this.browser.clickInto(['im_attribute_row_string_attribute_code_5_1', 'delete'], {waitRender: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await this.browser.assertImage('unused-attributes', {removeShadows: true});
    });

    it('В истории отображается изменение неиспользуемого атрибута (Великобритания)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000051), {region: 'gb'});
        await changeMasterCategory(this, 'master_category_code_35_1', 'Voluptatum ex voluptate');
        await this.browser.waitUntilRendered();

        await this.browser.typeInto('number_attribute_code_3_1__0', '12345');
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-history', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-3']);
    });

    it('В экспорте не показываются значения неиспользуемых атрибутов', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000001));
        await changeMasterCategory(this, 'master_category_code_27_1', 'Поняли назвал');

        await this.browser.openPage(ROUTES.CLIENT.PRODUCTS, {
            queryParams: {search: '10000001', columnIds: ['barcode', 'multiselect_attribute_code_2_1'].join()}
        });
        await this.browser.clickInto('export-icon', {waitRender: true});
        await this.browser.clickInto(['export-menu', 'export-from-table'], {waitRender: true});
        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file, {blankrows: true, defval: ''})).to.matchSnapshot(this);
    });
});
