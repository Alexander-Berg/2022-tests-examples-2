import {parseSpreadSheetCSV} from 'tests/e2e/helper/parse-spreadsheet';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {USER_LOGIN} from 'service/seed-db/fixtures';

describe('Таблица инфомоделей', function () {
    async function getBrowserDate(ctx: Hermione.TestContext) {
        return ctx.browser.execute(() => {
            const now = new Date();
            return [now.getDate(), now.getMonth() + 1]
                .map(String)
                .map((part) => part.padStart(2, '0'))
                .concat(String(now.getFullYear()))
                .join('.');
        });
    }

    it('Заголовок шапки страницы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        const defaultHeaderElement = await this.browser.findByTestId('default_panel');
        const innerText = await defaultHeaderElement.getText();
        expect(innerText).to.equal('Инфомодели');
    });

    it('Общий вид таблицы инфомоделей', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('infomodels-table__container');
    });

    it('Клик в строку таблицы открывает страницу инфомодели', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.clickInto('im_row_root', {waitNavigation: true, waitRender: true, x: 200});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.INFOMODEL('\\d')));
    });

    it('Клик в автора в таблице инфомоделей открывает его стафф', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.clickInto('author-link');
        const handles = await this.browser.getWindowHandles();
        expect(handles.length).to.equal(2);

        await this.browser.switchToWindow(handles[1]);
        expect(await this.browser.getUrl()).to.contain(
            encodeURIComponent(`https://staff.yandex-team.ru/${USER_LOGIN}`)
        );

        await this.browser.closeWindow();
        await this.browser.switchToWindow(handles[0]);
    });

    it('Скролл таблицы инфомоделей при развернутом меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);

        await this.browser.performScroll('infomodels-table__container', {
            direction: 'down',
            beforeIterationDelay: () => this.browser.waitForTestIdSelectorNotInDom('infomodels-table__spinner'),
            afterIterationDelay: () => this.browser.waitUntilRendered()
        });

        await this.browser.assertImage('infomodels-table__container');
    });

    it('Скролл таблицы инфомоделей при свернутом меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS, {collapseSidebar: true});

        await this.browser.performScroll('infomodels-table__container', {
            direction: 'down',
            beforeIterationDelay: () => this.browser.waitForTestIdSelectorNotInDom('infomodels-table__spinner'),
            afterIterationDelay: () => this.browser.waitUntilRendered()
        });

        await this.browser.assertImage('infomodels-table__container');
    });

    it('Поиск ИМ по названию (Великобритания)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS, {region: 'gb', queryParams: {search: 'quia'}});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('infomodels-table__container');
    });

    it('Поиск ИМ по коду (Израиль)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS, {region: 'il', queryParams: {search: 'code_4_4'}});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('infomodels-table__container');
    });

    it('Экшн-бар в обычном режиме', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.assertImage('action-bar');
    });

    it('Смена языка данных (Израиль)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS, {region: 'il', dataLang: 'he', uiLang: 'en'});
        await this.browser.waitUntilRendered();
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('data-lang-select', {waitRender: true});
        await this.browser.clickInto(['data-lang-select_dropdown-menu', 'ru'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Клик в три точки открывает контекстное меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.clickInto('table-more-button', {waitRender: true});
        await this.browser.assertImage(['table-more-button', 'more-menu']);
    });

    it('Скачать шаблон из таблицы инфомоделей', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);

        const basePath = ['im_row_info_model_code_1_14', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'download-template'], {waitRender: true});

        const date = await getBrowserDate(this);
        const fileName = `template_IM_info_model_code_1_14_${date}.xlsx`;

        const file = await this.browser.getDownloadedFile(fileName, {purge: true});
        expect(parseSpreadSheetCSV(file)).to.matchSnapshot(this);
    });

    it('Скачать шаблон инфомодели без товаров из таблицы инфомоделей', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);

        const basePath = ['im_row_info_model_code_1_13', 'table-more-button'];
        await this.browser.clickInto(basePath, {waitRender: true});
        await this.browser.clickInto([...basePath, 'more-menu', 'download-template'], {waitRender: true});

        const date = await getBrowserDate(this);
        const fileName = `template_IM_info_model_code_1_13_${date}.xlsx`;

        const file = await this.browser.getDownloadedFile(fileName, {purge: true});
        expect(parseSpreadSheetCSV(file)).to.matchSnapshot(this);
    });

    it('Клик к количество товаров ИМ в общей таблице открывает таблицу товаров с этой ИМ', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.clickInto('products-count-link', {waitRender: true, waitNavigation: true});
        await this.browser.assertImage('filter-list');
    });

    // eslint-disable-next-line max-len
    it('Клик в количество заполненных товаров ИМ в общей таблице открывает таблицу активных заполненных товаров с этой ИМ', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.clickInto(['filled-products-count', 'products-count-link'], {
            waitRender: true,
            waitNavigation: true
        });
        await this.browser.assertImage('filter-list');
    });

    // eslint-disable-next-line max-len
    it('Клик в количество не заполненных товаров общей таблице открывает таблицу активных незаполненных товаров с этой ИМ', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.clickInto(['not-filled-products-count', 'products-count-link'], {
            waitRender: true,
            waitNavigation: true
        });
        await this.browser.assertImage('filter-list');
    });

    it('Свернуть и развернуть меню на странице ИМ России', async function () {
        await this.browser.openPage(ROUTES.CLIENT.INFOMODELS);
        await this.browser.clickInto('sidebar-switcher', {waitRender: true});
        await this.browser.assertImage();
        await this.browser.clickInto('sidebar-switcher', {waitRender: true});
        await this.browser.assertImage();
    });
});
