const DriversBlock = require('../../../../page/DriversBlock');
const ReportsSummary = require('../../../../page/ReportsSummary');

describe('Сводный отчёт по КИС АРТ: фильтрация водителей в отчёте по статусу КИС АРТ', () => {

    const DATA = {
        title: 'Статус КИС «АРТ»',
        statuses: [
            'Недействительный',
            'Постоянный',
            'Запрошенный',
            'Временный',
            'Отсутствует/Просрочен',
        ],
    };

    const statusToChooseIndex = DATA.statuses.indexOf('Отсутствует/Просрочен');
    const statusToChooseText = DATA.statuses[statusToChooseIndex];

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goTo('/kis-art?date_from=2021-11-01&date_to=2021-11-30');
    });

    it('Открыть первый отчёт', () => {
        ReportsSummary.getCells({td: 1, tr: 1}).click();
    });

    it('Отобразился сайдбар водителей', () => {
        DriversBlock.drivers.list.waitForDisplayed();
    });

    it('Открыть фильтрацию по статусу', () => {
        DriversBlock.filter.button.click();
    });

    it('В фильтре статуса отображается корректный заголовок', () => {
        expect(DriversBlock.status.title).toHaveTextEqual(DATA.title);
    });

    it('Отображаются корректные статусы для выбора', () => {
        expect(DriversBlock.status.items).toHaveTextEqual(DATA.statuses);
    });

    it(`Выбрать статус "${statusToChooseText}"`, () => {
        DriversBlock.status.items[statusToChooseIndex].click();
        DriversBlock.actions.button.click();
    });

    it('У всех водителей отобразился выбранный статус', () => {
        expect(DriversBlock.drivers.status).toHaveTextArrayEachEqual(statusToChooseText);
    });

});
