const CameraList = require('../../page/signalq/CameraList');
const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. добавление камеры в группу (отмена)', () => {
    const name = 'opteum463';
    const SN = '8609496545071784';
    const findSN = `SN ${SN}`;
    const IMEI = '469803452204208';

    it('Подготовка тестовых данных', () => {
        CameraList.goTo();
        CameraList.clearCameraData(SN, IMEI);

        DevicesGroups.goTo();
        DevicesGroups.clearOldTestData(name);
        DevicesGroups.addGroup(name);
    });

    it('открыт раздел "Все камеры"', () => {
        DevicesGroups.goTo();
    });

    it('Нажать на группу', () => {
        DevicesGroups.getGroupByName(name).click();
        browser.pause(500);
    });

    it('Нажать на кнопку в виде трёх точек около списка "Камеры"', () => {
        DevicesGroups.cameraDropdownButton.click();
    });

    it('Нажать на кнопку "добавить камеру"', () => {
        DevicesGroups.addCameraButton.click();
        browser.pause(500);
    });

    it('Выбрать подготовленную камеру в списке', () => {
        try {
            DevicesGroups.getNewCameraByStr(findSN).click();
        } catch {
            DevicesGroups.addCameraListOneElement.click();
        }
    });

    it('Нажать кнопку "отмена"', () => {
        DevicesGroups.addCameraCancelButton.click();
    });

    it('Отображается надпись "Пока нет ни одной камеры"', () => {
        expect(DevicesGroups.noCameraText).toHaveTextEqual('Пока нет ни одной камеры');
    });

    it('Почистить данные', () => {
        DevicesGroups.deleteGroupByName(name);
    });
});
