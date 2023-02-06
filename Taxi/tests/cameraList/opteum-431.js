const CameraList = require('../../page/signalq/CameraList');
const GroupList = require('../../page/signalq/GroupList');

describe('SignalQ. Все камеры. Поиск по группе камер (позитив)', () => {
    const group = 'Group';
    const subGroup = 'underGroup';
    const SN = '212020E103F59';
    const IMEI = '864004040545078';

    it('открыт раздел "Все камеры"', () => {
        CameraList.goTo();
    });

    it('Подготовка тестовых данных', () => {
        CameraList.clearCameraData(SN, IMEI);

        CameraList.getRow().status.click();

        CameraList.getCameraCard().group.click();
        let position = GroupList.elementPosition(group);
        GroupList.element(position).click();

        CameraList.getCameraCard().subGroup.click();
        position = GroupList.elementPosition(subGroup);
        GroupList.element(position).click();
    });

    it('Выбрать в селекторе "Выбрать группу" группу у которой есть камеры', () => {
        CameraList.groupFilter.click();
        CameraList.groupFilterInput.addValue(group);
        browser.keys('Enter');
    });

    it('Отобразился список камер с соответствующей группой', () => {
        CameraList.statusCell.forEach((el, i) => {
            expect(CameraList.getRow(i + 1).group).toHaveTextIncludes(group);
        });
    });

    it('выбрать подгруппу в этом же селекторе в которой есть камеры', () => {
        CameraList.groupFilter.click();
        CameraList.groupFilterInput.addValue(subGroup);
        browser.keys('Enter');
    });

    it('Отобразился список камер с соответствующей группой и подгруппой', () => {
        CameraList.statusCell.forEach((el, i) => {
            expect(CameraList.getRow(i + 1).group).toHaveTextEqual(`${group} > ${subGroup}`);
        });
    });

});
