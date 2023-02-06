const DatePicker = require('../../../../page/DatePicker');
const re = require('../../../../../../utils/consts/re');
const ReportsSummary = require('../../../../page/ReportsSummary');

describe('Фильтр по периоду', () => {

    let savedCars,
        savedDate;

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goToNotEmptyCars();
    });

    it('Отображается корректная дата в фильтре', () => {
        expect(DatePicker.block.filter).toHaveAttributeMatch('value', re.dates.period);
    });

    it('Сохранить текущую дату и машины', () => {
        savedDate = DatePicker.block.filter.getAttribute('value');
        savedCars = ReportsSummary.getCells({td: 1}).map(elem => elem.getText());
    });

    it('Открыть фильтр дат', () => {
        DatePicker.open();
    });

    it('Выбрать предыдущий месяц', () => {
        DatePicker.pickPrevMonth();
    });

    it('Отображается корректная дата в фильтре', () => {
        expect(DatePicker.block.filter).toHaveAttributeMatch('value', re.dates.period);
    });

    it('Дата в фильтре изменилась', () => {
        expect(DatePicker.block.filter).not.toHaveAttributeEqual('value', savedDate);
    });

    it('Машины в таблице изменились', () => {
        expect(ReportsSummary.getCells({td: 1})).not.toHaveTextEqual(savedCars);
    });

});
