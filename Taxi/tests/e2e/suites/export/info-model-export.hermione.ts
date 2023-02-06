import fs from 'fs';
import os from 'os';
import path from 'path';
import {parseSpreadSheetJSON} from 'tests/e2e/helper/parse-spreadsheet';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import type {ClientConfig} from 'service/cfg';

describe('Экспорт инфомоделей', function () {
    it('Вид страницы инфомоделей с нажатыми чекбоксами', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.clickInto('select-all-checkbox', {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('info-models-bottom-panel');
        await this.browser.assertImage('base-layout-content');
    });

    it('Экспорт всех инфомоделей кнопкой', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.clickInto('export-icon', {waitRender: true});
        const file = await this.browser.getDownloadedFile('exported-info-models.xlsx', {purge: true});

        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    it('Экспорт всех инфомоделей, выбор чекбоксом', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.clickInto('select-all-checkbox', {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('info-models-bottom-panel');
        await this.browser.clickInto(['info-models-bottom-panel', 'export'], {waitRender: true});
        const file = await this.browser.getDownloadedFile('exported-info-models.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    it('Экспорт одной инфомодели кнопкой', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.typeInto(['action-bar', 'search'], 'info_model_code_1_1');
        await this.browser.waitForTestIdSelectorNotInDom('infomodels-table__spinner');
        await this.browser.clickInto('export-icon', {waitRender: true});
        const file = await this.browser.getDownloadedFile('exported-info-models.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    it('Экспорт нескольких инфомоделей, Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS, {region: 'il'});
        await this.browser.clickInto(['im_row_info_model_code_4_1', 'checkbox'], {waitRender: true});
        await this.browser.clickInto(['im_row_info_model_code_4_2', 'checkbox'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('info-models-bottom-panel');
        await this.browser.clickInto(['info-models-bottom-panel', 'export'], {waitRender: true});
        const file = await this.browser.getDownloadedFile('exported-info-models.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    it('Проверка лимита экспорта', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.execute(() => {
            (window.__CONFIG__ as ClientConfig).import.maxSpreadsheetRows = 5;
        });

        await this.browser.clickInto('select-all-checkbox', {waitRender: true});

        await this.browser.waitForTestIdSelectorInDom('info-models-bottom-panel');
        await this.browser.clickInto(['im_row_info_model_code_1_5', 'checkbox'], {waitRender: true});
        await this.browser.assertImage('infomodels-table');
    });

    it('Импорт экспортированного файла', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.clickInto(['im_row_info_model_code_1_1', 'checkbox'], {waitRender: true});

        await this.browser.waitForTestIdSelectorInDom('info-models-bottom-panel');
        await this.browser.clickInto(['info-models-bottom-panel', 'export'], {waitRender: true});

        const buffer = await this.browser.getDownloadedFile('exported-info-models.xlsx', {purge: true});
        const pathToFile = path.resolve(os.tmpdir(), `exported-info-models-${this.currentTest.id()}.xlsx`);
        fs.writeFileSync(pathToFile, buffer);

        await this.browser.openPage(ROUTES.CLIENT.IMPORT_INFOMODELS);
        await this.browser.uploadFileInto(['import-upload', 'file-input'], pathToFile);
        await this.browser.waitForTestIdSelectorInDom('import-info-ignore');
        await this.browser.clickInto('import-info-ignore', {waitRender: true});
        await this.browser.assertImage('import-info-ignore');
    });
});
