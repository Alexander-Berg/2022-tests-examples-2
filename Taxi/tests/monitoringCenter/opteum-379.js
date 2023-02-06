const MonitoringCenter = require('../../page/signalq/MonitoringCenter');

describe('SignalQ. Центр мониторинга. Поиск камер', () => {
    let SN;
    const wrongSN = '6666666';

    it('Открыт раздел "Центр мониторинга"', () => {
        MonitoringCenter.goTo();
    });

    it('Ввести в поиск серийный номер камеры находящейся а центре мониторинга', () => {
        SN = MonitoringCenter.getSN().getText();
        MonitoringCenter.search.addValue(SN);
        browser.pause(1500);
    });

    it('Проверить что отобразилась только камера с введёным SN', () => {
        expect(MonitoringCenter.getSN()).toHaveTextEqual(SN);
        expect(MonitoringCenter.getSN(3)).not.toHaveElemExist();
    });

    it('Вести в поиск ТС или серийный номер которого нет в списке', () => {
        MonitoringCenter.clearWithBackspace(MonitoringCenter.search);
        MonitoringCenter.search.addValue(wrongSN);
        browser.pause(1500);
    });

    it('Проверить что отобразилось предупреждение и кнопка сброса фильтров', () => {
        expect(MonitoringCenter.nothingFoundMessage).toHaveTextEqual('По вашему запросу ничего не нашлось');
        expect(MonitoringCenter.clearFiltersButton).toHaveElemExist();
    });

    it('Нажать кнопку "сбросить фильтры"', () => {
        MonitoringCenter.clearFiltersButton.click();
        expect(MonitoringCenter.getSN()).toHaveTextEqual(SN);
    });

});
