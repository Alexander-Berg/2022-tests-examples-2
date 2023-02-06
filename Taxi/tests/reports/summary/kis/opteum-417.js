const DatePicker = require('../../../../page/DatePicker');
const ReportsSummary = require('../../../../page/ReportsSummary');

describe('Сводный отчёт по КИС АРТ: фильтрация по периоду', () => {

    const DATA = {
        dates: {
            path: '?date_from=2021-08-01'
                + '&date_to=2021-08-31',
            current: {
                filter: '1 авг. – 31 авг. 2021 г.',
                table: /^\d{1,2} августа 2021 г.$/,
            },
            prev: {
                filter: '1 июл. – 31 июл. 2021 г.',
                table: /^\d{1,2} июля 2021 г.$/,
            },
        },
    };

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goTo(`/kis-art${DATA.dates.path}`);
    });

    it('Отображается корректная дата в фильтре', () => {
        expect(DatePicker.block.filter).toHaveAttributeEqual('value', DATA.dates.current.filter);
    });

    it('Отображаются корректные даты в таблице', () => {
        expect(ReportsSummary.getCells({td: 1})).toHaveTextMatch(DATA.dates.current.table);
    });

    it('Открыть фильтр дат', () => {
        DatePicker.open();
    });

    it('Выбрать предыдущий месяц', () => {
        DatePicker.pickPrevMonth();
    });

    it('Отображается корректная дата в фильтре', () => {
        expect(DatePicker.block.filter).toHaveAttributeEqual('value', DATA.dates.prev.filter);
    });

    it('Отображаются корректные даты в таблице', () => {
        expect(ReportsSummary.getCells({td: 1})).toHaveTextMatch(DATA.dates.prev.table);
    });

});
