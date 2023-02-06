import {addDays} from 'date-fns';
import {frontCategories} from 'tests/e2e/seed-db-map';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {MOCKED_UPDATED_AT} from 'service/seed-db/fixtures';

const basePikerPath = ['\\[class*="ant-picker-dropdown"]:not([class*="ant-picker-dropdown-hidden"])'];

const dateMockTs = addDays(new Date(MOCKED_UPDATED_AT), 1).getTime();
async function mockNow(ctx: Hermione.TestContext) {
    await ctx.browser.execute((dateMockTs) => {
        const mock = new Date(dateMockTs);
        const OriginalDate = Date;
        class MockedDate extends OriginalDate {
            constructor(...args: unknown[]) {
                // @ts-expect-error ---
                super(...(args.length ? args : [mock]));
            }
        }
        Object.assign(window, {Date: MockedDate, OriginalDate});
        Date.now = () => mock.getTime();
    }, dateMockTs);
}

describe('Расписание категорий', function () {
    it('Добавление корректного периода публикации подкатегории (дата начала раньше даты окончания)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_6_0));

        await mockNow(this);

        await this.browser.assertImage('base-layout');

        await this.browser.clickInto('target-date_from', {waitRender: true});
        await this.browser.clickInto([...basePikerPath, '\\table', '\\tr:nth-of-type(3)', '\\td:nth-of-type(3)'], {
            waitRender: true
        });
        await this.browser.clickInto('target-date_to', {waitRender: true});
        await this.browser.clickInto([...basePikerPath, '\\table', '\\tr:nth-of-type(4)', '\\td:nth-of-type(4)'], {
            waitRender: true
        });
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.assertImage('timetable', {removeShadows: true});
    });

    // eslint-disable-next-line max-len
    it('Добавление первого селектора с днем и временем доступности подкатегории, заполнение любым днём недели и временем', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_6_0));

        await this.browser.clickInto('add-more-days');

        await this.browser.clickInto(['days-row_1', 'select-days'], {waitRender: true});
        await this.browser.clickInto(['select-days-menu', 'saturday']);
        await this.browser.clickInto(['days-row_1', 'select-days'], {waitRender: true});

        await this.browser.clickInto(['days-row_1', 'target-time_from']);
        await this.browser.clickInto([...basePikerPath, '\\ul:nth-of-type(1)', '\\li:nth-of-type(5)']);
        await this.browser.clickInto([...basePikerPath, '\\[class*="ant-picker-ok"]', '\\button']);

        await this.browser.clickInto(['days-row_1', 'target-time_to']);
        await this.browser.clickInto([...basePikerPath, '\\ul:nth-of-type(1)', '\\li:nth-of-type(6)']);
        await this.browser.clickInto([...basePikerPath, '\\[class*="ant-picker-ok"]', '\\button']);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.assertImage('timetable', {removeShadows: true});
    });

    // eslint-disable-next-line max-len
    it('Добавление второго селектора с днём и временем доступности к уже существующему в подкатегории и его заполнение', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_5_1));

        await this.browser.clickInto('add-more-days');

        await this.browser.clickInto(['days-row_2', 'select-days'], {waitRender: true});
        await this.browser.clickInto(['select-days-menu', 'saturday']);
        await this.browser.clickInto(['days-row_2', 'select-days'], {waitRender: true});

        await this.browser.clickInto(['days-row_2', 'target-time_from']);
        await this.browser.clickInto([...basePikerPath, '\\ul:nth-of-type(1)', '\\li:nth-of-type(5)']);
        await this.browser.clickInto([...basePikerPath, '\\[class*="ant-picker-ok"]', '\\button']);

        await this.browser.clickInto(['days-row_2', 'target-time_to']);
        await this.browser.clickInto([...basePikerPath, '\\ul:nth-of-type(1)', '\\li:nth-of-type(6)']);
        await this.browser.clickInto([...basePikerPath, '\\[class*="ant-picker-ok"]', '\\button']);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.assertImage('timetable', {removeShadows: true});
    });

    it('Удаление периода публикации подкатегории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_5_0), {
            patchStyles: {showAntPickerClear: true}
        });

        await mockNow(this);

        await this.browser.clickInto(['target-date_from', '\\~.ant-picker-clear']);
        await this.browser.clickInto(['target-date_to', '\\~.ant-picker-clear']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);
        await this.browser.assertImage('timetable', {removeShadows: true});
    });

    it('Удаление селектора дня и времени (через иконку корзины) доступности подкатегории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_5_0), {
            patchStyles: {showAntPickerClear: true}
        });
        await this.browser.clickInto(['timetable', 'days-row_1', 'delete']);
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);
        await this.browser.assertImage('timetable', {removeShadows: true});
    });

    it('При просмотре подкатегории есть блок с расписанием категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_5_0));
        await this.browser.waitForTestIdSelectorInDom('timetable');
        await this.browser.assertImage('timetable', {removeShadows: true});
    });

    it('При просмотре родительской категории нет блока с расписанием', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        await this.browser.waitForTestIdSelectorNotInDom('timetable');
    });

    // eslint-disable-next-line max-len
    it('Нельзя сохранить селектор дня и времени доступности подкатегории, если не выбран день в селекторе', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_5_2));

        await this.browser.clickInto('add-more-days');

        await this.browser.clickInto(['days-row_1', 'target-time_from']);
        await this.browser.clickInto([...basePikerPath, '\\ul:nth-of-type(1)', '\\li:nth-of-type(5)']);
        await this.browser.clickInto([...basePikerPath, '\\[class*="ant-picker-ok"]', '\\button']);

        await this.browser.clickInto(['days-row_1', 'target-time_to']);
        await this.browser.clickInto([...basePikerPath, '\\ul:nth-of-type(1)', '\\li:nth-of-type(6)']);
        await this.browser.clickInto([...basePikerPath, '\\[class*="ant-picker-ok"]', '\\button']);

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.assertImage('days-row_1');
    });

    // eslint-disable-next-line max-len
    it('Нельзя сохранить селектор дня и времени доступности подкатегории, если не выбрано время в селекторе', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_5_2));

        await this.browser.clickInto('add-more-days');

        await this.browser.clickInto(['days-row_1', 'select-days'], {waitRender: true});
        await this.browser.clickInto(['select-days-menu', 'saturday']);
        await this.browser.clickInto(['days-row_1', 'select-days'], {waitRender: true});

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.assertImage('days-row_1');
    });

    it('Нельзя выставить дату окончания до даты начала в периоде публикации категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_5_1));

        await mockNow(this);

        await this.browser.clickInto('target-date_from', {waitRender: true});
        await this.browser.clickInto([...basePikerPath, '\\table', '\\tr:nth-of-type(3)', '\\td:nth-of-type(3)']);
        await this.browser.clickInto('target-date_from', {waitRender: true});
        await this.browser.assertImage(basePikerPath);

        await this.browser.clickInto('target-date_to', {waitRender: true});
        await this.browser.assertImage(basePikerPath);
    });

    it('Нельзя выставить дату начала позже даты окончания в периоде публикации категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_5_1));

        await mockNow(this);

        await this.browser.clickInto('target-date_to', {waitRender: true});
        await this.browser.clickInto([...basePikerPath, '\\table', '\\tr:nth-of-type(4)', '\\td:nth-of-type(4)']);
        await this.browser.clickInto('target-date_to', {waitRender: true});
        await this.browser.assertImage(basePikerPath);

        await this.browser.clickInto('target-date_from', {waitRender: true});
        await this.browser.assertImage(basePikerPath);
    });

    it('Нельзя редактировать расписание категории в режиме read only', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_5_1), {
            isReadonly: true
        });
        await this.browser.assertImage('timetable', {removeShadows: true});
    });
});
