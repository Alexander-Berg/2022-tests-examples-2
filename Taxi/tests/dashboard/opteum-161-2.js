const DashboardPage = require('../../page/DashboardPage');
const DatePicker = require('../../page/DatePicker');
const re = require('../../../../utils/consts/re');

describe('Сводка: фильтры: период', () => {

    const DATA = {
        filter: 'Выберите период',
        index: 4,
    };

    let savedGraphs;

    it('Открыть страницу сводки', () => {
        DashboardPage.goTo();
    });

    it('Отображается кнопка выбора периода', () => {
        expect(DashboardPage.filter.buttons).toHaveTextArrayIncludes(DATA.filter);
    });

    it('Сохранить текущие графики', () => {
        savedGraphs = DashboardPage.dashboards.paths;
    });

    it('Нажать на кнопку выбора периода', () => {
        DashboardPage.filter.buttons[DATA.index].click();
    });

    it('Отобразилось поле даты', () => {
        expect(DashboardPage.filter.date).toHaveAttributeMatch('value', re.dates.period);
    });

    it('Нажать на поле даты', () => {
        DashboardPage.filter.date.click();
    });

    it('Открылся календарь выбора дат', () => {
        expect(DatePicker.block.popup).toHaveElemVisible();
    });

    it('Выбрать период за предыдущий месяц', () => {
        DatePicker.pickPrevMonth();
    });

    it('Графики изменились', () => {
        expect(DashboardPage.dashboards.paths).not.toHaveElemEqual(savedGraphs);
    });

});
