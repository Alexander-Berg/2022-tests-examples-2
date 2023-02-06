const SupportMessagesList = require('../../page/SupportMessagesList.js');

const status = 'Закрыт';
const allStatuses = 'Любой статус';

const selectStatus = statusName => {
    SupportMessagesList.filters.status.click();
    SupportMessagesList.selectDropdownItem(statusName);
    browser.pause(2000);
};

describe('Фильтрация обращений по статусу', () => {
    it('открыть раздел "Мои обращения"', () => {
        SupportMessagesList.goTo();
    });

    it('Выбрать любой статус, в котором есть обращения', () => {
        selectStatus(status);
    });

    it('отображается список обращений согласно фильтру', () => {
        expect(SupportMessagesList.getColumn(5)).toHaveTextArrayEachEqual(status);
    });

    it('Выбрать статус "Любой статус"', () => {
        selectStatus(allStatuses);
    });

    it('отображается список всех обращений', () => {
        const elems = SupportMessagesList.getColumn(5)
            .map(elem => elem.getText())
            .filter(elem => elem !== status);

        expect(elems.length).toBeGreaterThan(0);
    });
});
