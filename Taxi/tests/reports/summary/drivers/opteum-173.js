const ReportsSummary = require('../../../../page/ReportsSummary');

describe('Сводные отчеты. Наличие столбцов. По водителям', () => {

    const DATA = {
        type: 'По водителям',
        table: {
            columns: [
                'Водитель',
                'Позывной',
                'Успешно завершённые заказы',
                'Время на линии',
                'Наличные',
                'Безналичные платежи',
                'Комиссия платформы',
                'Комиссии парка',
                'Прочее',
            ],
            unselectable: 'Водитель',
        },
    };

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goTo('/drivers');
    });

    it(`По умолчанию выбран тип отчёта "${DATA.type}"`, () => {
        expect(ReportsSummary.typeSelector.checked).toHaveTextEqual(DATA.type);
    });

    it('По умолчанию отображаются корректные колонки', () => {
        expect(ReportsSummary.reportTable.header.columns).toHaveTextEqual(DATA.table.columns);
    });

    it('Открыть редактирование колонок', () => {
        ReportsSummary.table.buttons.columns.click();
    });

    it('При скрытии колонки она пропадает из таблицы', () => {
        ReportsSummary.reportTable.dropdown.checkedNotDisabled.forEach((elem, i) => {
            // колонку водитель нельзя снять, начинаем со следующего элемента
            i += 2;

            elem.click();

            expect(ReportsSummary.reportTable.header.columns).toHaveTextEqual([
                DATA.table.unselectable,
                ...DATA.table.columns.slice(i),
            ]);
        });
    });

});
