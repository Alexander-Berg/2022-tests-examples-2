const DriverCard = require('../../../page/driverCard/DriverCard');
const ReportsQuality = require('../../../page/ReportsQuality');

describe('Фильтрация по статусу водителя', () => {

    const STATUSES = [
        {name: 'Работает', key: 'works'},
        {name: 'Не работает', key: 'doesntWork'},
        {name: 'Уволен', key: 'fired'},
    ];

    it('Открыть страницу Качество', () => {
        ReportsQuality.goTo();
    });

    STATUSES.forEach(({name, key}, i) => {
        describe(name, () => {

            it('Выбрать статус в фильтре', () => {
                ReportsQuality.filtersBlock.statuses.dropdown.click();
                ReportsQuality.filtersBlock.statuses[key].click();
            });

            it('Открыть первого водителя', () => {
                ReportsQuality.openFirstDriver();
            });

            it('В карточке водителя отображается корректный статус', () => {
                expect(DriverCard.status).toHaveTextEqual(name);
            });

            if (i < STATUSES.length - 1) {
                it('Закрыть открытую вкладку', () => {
                    browser.closeWindow();
                    ReportsQuality.switchTab(0);
                });
            }

        });
    });

});
