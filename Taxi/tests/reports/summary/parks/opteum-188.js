const ReportsSummary = require('../../../../page/ReportsSummary');

describe('Сводные отчеты. Наличие столбцов. По датам', () => {

    const DATA = {
        type: 'По датам',
        table: {
            columns: [
                'Месяц',
                'Активные автомобили',
                'Активные водители',
                'Новые водители',
                'Отток водителей',
                'Завершено заказов',
                'Среднее время водителя на линии',
                'Среднее время авто на линии',
                'Наличные',
                'Безналичные платежи',
                'Комиссия платформы',
                'Комиссия парка',
                'Дополнительная плата за программное обеспечение',
                'Услуги по привлечению водителей',
                'Услуга по возврату водителей',
            ],
            unselectable: 'Месяц',
        },
    };

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goTo('/parks');
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
            // колонку месяц нельзя снять, начинаем со следующего элемента
            i += 2;

            elem.click();

            expect(ReportsSummary.reportTable.header.columns).toHaveTextEqual([
                DATA.table.unselectable,
                ...DATA.table.columns.slice(i),
            ]);
        });
    });

});
