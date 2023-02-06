const GroupList = require('../../page/signalq/GroupList');
const MonitoringCenter = require('../../page/signalq/MonitoringCenter');

describe('SignalQ. Центр мониторинга. Фильтрация по группе (негатив)', () => {
    const group = 'empty';

    it('Открыт раздел "Центр мониторинга"', () => {
        MonitoringCenter.goTo();
    });

    it('Открыть фильтры', () => {
        MonitoringCenter.filterButton.click();
    });

    it('В фильтре выбрать группу в которой нет камер', () => {
        MonitoringCenter.getFilter().group.click();
        GroupList.element(GroupList.elementPosition(group)).click();
        MonitoringCenter.getFilter().acceptButton.click();
    });

    it('Проверить что отобразилось предупреждение и кнопка сброса фильтров', () => {
        expect(MonitoringCenter.nothingFoundMessage).toHaveTextEqual('По вашему запросу ничего не нашлось');
        expect(MonitoringCenter.clearFiltersButton).toHaveElemExist();
    });
});
