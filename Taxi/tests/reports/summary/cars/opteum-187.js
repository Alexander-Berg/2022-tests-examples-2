const ReportsSummary = require('../../../../page/ReportsSummary');

describe('Скрытие и отображение полей в сводном отчете по автомобилям', () => {

    const DATA = {
        columns: [
            'Автомобиль',
            'Водители со списаниями',
            'Сдаваемость',
            'Категории',
            'Успешно выполненные заказы',
            'Км на заказах',
            'Наличные',
            'Безналичные',
            'Аренда',
        ],
        remove: ['Сдаваемость', 'Категории'],
    };

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goToNotEmptyCars();
    });

    it('Отображаются корректные колонки таблицы', () => {
        expect(ReportsSummary.reportTable.header.columns).toHaveTextEqual(DATA.columns);
    });

    it('Открыть редактирование колонок', () => {
        ReportsSummary.table.buttons.columns.click();
    });

    DATA.remove.forEach(column => {
        it(`Скрыть колонку "${column}"`, () => {
            ReportsSummary.reportTable.dropdown.itemNotDisabled[DATA.columns.indexOf(column)].click();
        });

        it('Колонка пропала из таблицы', () => {
            delete DATA.columns[DATA.columns.indexOf(column)];
            expect(ReportsSummary.reportTable.header.columns).toHaveTextEqual(DATA.columns.filter(Boolean));
        });
    });

});
