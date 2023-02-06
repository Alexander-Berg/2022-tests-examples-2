import {parseSpreadSheetJSON} from 'tests/e2e/helper/parse-spreadsheet';
import {infoModels} from 'tests/e2e/seed-db-map';
import getFixturePath from 'tests/e2e/utils/fixture';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Импорт инфомоделей', function () {
    async function assertUserAttributes(browser: WebdriverIO.Browser) {
        await browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab');
        await browser.assertImage('im-user_attributes-table');

        await browser.clickInto(['infomodel-groups-table', 'im_attribute-group_row_attribute_group_code_2']);
        await browser.assertImage('im-user_attributes-table');

        await browser.clickInto(['infomodel-groups-table', 'im_attribute-group_row_attribute_group_code_3']);
        await browser.assertImage('im-user_attributes-table');

        await browser.clickInto(['infomodel-groups-table', 'im_attribute-group_row_undefined']);
        await browser.assertImage('im-user_attributes-table');
    }

    it('Клик на иконку импорта открывает страницу импорта инфомоделей', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.clickInto(['action-bar', 'import-button-link'], {waitRender: true, waitNavigation: true});
        await this.browser.assertImage('base-layout');
    });

    it('Страница импорта инфомоделей открывается по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_INFOMODELS);
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('base-layout');
    });

    it('Шаблон файла для импорта', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_INFOMODELS);
        const link = await this.browser.findByTestId('xlsx-template-link');
        const url = await link.getProperty('href');
        expect(url).to.match(new RegExp('templates/import-info-model-spreadsheet_ru_rev\\d.xlsx'));
    });

    it('Создать инфомодель с необязательными атрибутами', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_INFOMODELS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('create-info-model-with-not-required-attributes.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-create');
        await this.browser.clickInto(['import-info-create', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-create');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');

        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.clickInto('im_row_test_info_model_code', {waitNavigation: true, waitRender: true});
        await this.browser.assertImage('base-layout-content');

        await assertUserAttributes(this.browser);
    });

    it('Изменение всех параметров инфомодели', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_INFOMODELS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('change-all-info-model-parameters.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_7));
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('base-layout-content');

        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab');
        await this.browser.assertImage('im-user_attributes-table');

        await this.browser.clickInto(['infomodel-groups-table', 'im_attribute-group_row_attribute_group_code_3']);
        await this.browser.assertImage('im-user_attributes-table');
    });

    it('Изменить английское название и описание, Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_INFOMODELS, {region: 'il'});
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('change-info-model-en-title-and-description-il.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.il.info_model_code_4_1), {region: 'il'});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(['translations', 'en']);
    });

    it('Добавить, удалить атрибут и изменить важность, Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_INFOMODELS, {region: 'fr'});
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('add-remove-and-change-importance-info-model-fr.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.fr.info_model_code_3_8), {region: 'fr'});
        await this.browser.waitUntilRendered();

        await this.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab');
        await this.browser.assertImage('im-user_attributes-table');

        await this.browser.clickInto(['infomodel-groups-table', 'im_attribute-group_row_attribute_group_code_2']);
        await this.browser.assertImage('im-user_attributes-table');
    });

    it('Нельзя удалить атрибут типа boolean из инфомодели', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_INFOMODELS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('removing-boolean-attribute-from-info-model-is-forbidden.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-not-upload');
        await this.browser.clickInto(['import-info-not-upload', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('import-cell-tooltip-help-icon', {waitRender: true});
        await this.browser.assertImage('import-info-not-upload');
        await this.browser.waitForTestIdSelectorDisabled(['header-panel', 'submit-button']);
    });

    it('Проверка ссылки при попытке удаления атрибута, присутствующего в товаре, Великобритания', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_INFOMODELS, {region: 'gb'});
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('delete-linked-to-product-attribute-from-info-model.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-not-upload');
        await this.browser.clickInto(['import-info-not-upload', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('import-cell-tooltip-help-icon', {waitRender: true});
        await this.browser.assertImage('import-info-not-upload');
        await this.browser.clickInto(['error-tooltip-body', 'error-tooltip-link'], {waitRender: true});

        const handles = await this.browser.getWindowHandles();
        expect(handles.length).to.equal(2);

        await this.browser.switchToWindow(handles[1]);
        expect(await this.browser.getUrl()).to.match(new RegExp(`${ROUTES.CLIENT.PRODUCTS}\\?filters`));

        await this.browser.waitUntilRendered();
        await this.browser.assertImage('filter-list');

        await this.browser.closeWindow();
        await this.browser.switchToWindow(handles[0]);
    });

    it('Экспорт файла после успешного импорта', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_INFOMODELS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('purge-info-model-title.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');

        await this.browser.clickInto('download-xlsx-link', {waitRender: true});

        const file = await this.browser.getDownloadedFile('exported-info-models.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    it('Очистить поле title (без локали в заголовке) инфомодели', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_INFOMODELS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('purge-info-model-title.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');

        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_1));
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('translations');
    });

    it('Очистить один из переводов описания, Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_INFOMODELS, {region: 'fr'});
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('purge-info-model-description-fr.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');

        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.fr.info_model_code_3_1), {region: 'fr'});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('translations');
    });

    it('Изменить обязательность атрибутов всеми способами', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_INFOMODELS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('check-is-important-values.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');

        await this.browser.openPage(ROUTES.CLIENT.INFOMODEL(infoModels.ru.info_model_code_1_1));
        await this.browser.waitUntilRendered();

        await assertUserAttributes(this.browser);
    });

    it('Уведомление об ошибке в заголовке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_INFOMODELS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-info-model-with-invalid-header.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('alert-warning');
        await this.browser.assertImage('alert-warning');
    });

    it('Нельзя импортировать файл с пустым полем код', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_INFOMODELS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-info-model-with-empty-code.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-not-upload');
        await this.browser.clickInto(['import-info-not-upload', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('import-cell-tooltip-help-icon', {waitRender: true});
        await this.browser.assertImage('import-info-not-upload');
    });

    it('Игнорирование пустых строк и столбцов в файле', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_INFOMODELS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-info-model-with-empty-columns-and-rows.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Нельзя редактировать скрытую инфомодель с помощью импорта', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_INFOMODELS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('change-hidden-info-model.xlsx')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-not-upload');
        await this.browser.waitForTestIdSelectorDisabled('submit-button');
        await this.browser.clickInto(['import-info-not-upload', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('import-cell-tooltip-help-icon', {waitRender: true});
        await this.browser.assertImage('import-info-not-upload');
    });
});
