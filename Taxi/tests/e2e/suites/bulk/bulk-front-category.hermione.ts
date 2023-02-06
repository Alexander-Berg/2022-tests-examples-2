import {openChangeFrontCategoryBulkPage} from 'tests/e2e/helper/bulk';
import {parseSpreadSheetJSON} from 'tests/e2e/helper/parse-spreadsheet';
import {describe, expect, it} from 'tests/hermione.globals';

describe('Балковые действия для фронт-категорий', function () {
    it('Добавить ФК во все товары', async function () {
        await openChangeFrontCategoryBulkPage(this, 'all', 'add');
        await this.browser.clickInto('fc_row_front_category_code_1_0', {waitRender: true});
        await this.browser.clickInto(['fc_row_front_category_code_5_0', 'checkbox'], {waitRender: true});
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');
        await this.browser.clickInto('import-info-update', {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Удалить ФК у всех товаров', async function () {
        await openChangeFrontCategoryBulkPage(this, 'all', 'remove');
        await this.browser.clickInto('fc_row_front_category_code_1_0', {waitRender: true});
        await this.browser.clickInto(['fc_row_front_category_code_5_0', 'checkbox'], {waitRender: true});
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');
        await this.browser.clickInto('import-info-update', {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Добавить нескольким товарам фронт-категорию', async function () {
        await openChangeFrontCategoryBulkPage(this, [10000001, 10000002], 'add');
        await this.browser.clickInto('fc_row_front_category_code_1_1', {waitRender: true});
        await this.browser.clickInto(['fc_row_front_category_code_6_1', 'checkbox'], {waitRender: true});
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');
        await this.browser.clickInto('download-xlsx-link', {waitRender: true});
        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    it('Убрать у одного товара фронт-категорию', async function () {
        await openChangeFrontCategoryBulkPage(this, [10000001], 'remove');
        await this.browser.clickInto('fc_row_front_category_code_1_0', {waitRender: true});
        await this.browser.clickInto(['fc_row_front_category_code_5_1', 'checkbox'], {waitRender: true});
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('bulk-success-alert');
        await this.browser.clickInto('download-xlsx-link', {waitRender: true});
        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    it('Показ неактивных категорий при добавлении во фронт-категории', async function () {
        await openChangeFrontCategoryBulkPage(this, [10000001], 'add');

        await this.browser.performScroll(['tree-table', 'list-holder']);
        await this.browser.assertImage('tree-table');

        await this.browser.clickInto(['action-bar', 'show-inactive'], {waitRender: true});

        await this.browser.performScroll(['tree-table', 'list-holder']);
        await this.browser.assertImage('tree-table');
    });

    it('Показ неактивных категорий при удалении из фронт-категорий', async function () {
        await openChangeFrontCategoryBulkPage(this, [10000004], 'remove');

        await this.browser.performScroll(['tree-table', 'list-holder']);
        await this.browser.assertImage('tree-table');

        await this.browser.clickInto(['action-bar', 'show-inactive'], {waitRender: true});

        await this.browser.performScroll(['tree-table', 'list-holder']);
        await this.browser.assertImage('tree-table');
    });

    it('Поиск активной фронт-категории по названию при добавлении', async function () {
        await openChangeFrontCategoryBulkPage(this, [10000001], 'add');

        const frontCategoryName = 'Как жизни презирает';

        await this.browser.typeInto('search', frontCategoryName);
        await this.browser.waitUntilRendered();

        await this.browser.assertImage(['list-holder', 'fc_row_front_category_code_1_0']);
    });

    it('Поиск неактивной фронт-категории по названию при удалении', async function () {
        await openChangeFrontCategoryBulkPage(this, [10000005], 'remove');

        const frontCategoryName = 'Не предпочел';

        await this.browser.clickInto('show-inactive');
        await this.browser.typeInto('search', frontCategoryName);
        await this.browser.waitUntilRendered();

        await this.browser.assertImage(['list-holder', 'fc_row_front_category_code_7_4']);
    });

    it('Страница массового добавления фронт-категории', async function () {
        await openChangeFrontCategoryBulkPage(this, [10000001, 10000002], 'add');

        await this.browser.assertImage('base-layout');
    });

    it('Страница массового удаления фронт-категории', async function () {
        await openChangeFrontCategoryBulkPage(this, [10000001, 10000002], 'remove');

        await this.browser.assertImage('base-layout');
    });
});
