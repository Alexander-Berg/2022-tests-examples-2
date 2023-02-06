const CameraList = require('../../page/signalq/CameraList');
const GroupList = require('../../page/signalq/GroupList');
const MonitoringCenter = require('../../page/signalq/MonitoringCenter');

describe('SignalQ. Центр мониторинга. Фильтрация по подгруппе (негатив)', () => {
    const group = 'notEmpty';
    const subGroup = 'empty';
    const SN = '001A826B7EFED2EC';
    const IMEI = '720625637632177';

    it('Подготовка тестовых данных', () => {
        CameraList.goTo();

        CameraList.clearCameraData(SN, IMEI);

        CameraList.getRow().status.click();

        CameraList.getCameraCard().group.click();
        const position = GroupList.elementPosition(group);
        GroupList.element(position).click();
    });

    it('Открыт раздел "Центр мониторинга"', () => {
        MonitoringCenter.goTo();
    });

    it('Открыть фильтры', () => {
        MonitoringCenter.filterButton.click();
    });

    it('В фильтре выбрать группу в которой есть камеры и в этом же селекторе подгруппу в которой камер нет', () => {
        MonitoringCenter.getFilter().group.click();
        GroupList.element(GroupList.elementPosition(group)).click();

        MonitoringCenter.getFilter().group.click();
        GroupList.element(GroupList.elementPosition(subGroup)).waitForDisplayed();
        GroupList.element(GroupList.elementPosition(subGroup)).click();
        MonitoringCenter.getFilter().acceptButton.click();
    });

    it('Проверить что отобразилось предупреждение и кнопка сброса фильтров', () => {
        expect(MonitoringCenter.nothingFoundMessage).toHaveTextEqual('По вашему запросу ничего не нашлось');
        expect(MonitoringCenter.clearFiltersButton).toHaveElemExist();
    });
});
