const CameraList = require('../../page/signalq/CameraList');
const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. добавление камеры в группу', () => {
    const name = 'opteum453';
    const SN = '2859323277929881';
    const findSN = `SN ${SN}`;
    const IMEI = '150620757992103';

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

    it('Нажать кнопку "сохранить"', () => {
        DevicesGroups.addCameraSaveButton.click();
    });

    it('отобразилось уведомление "камеры успешно добавлены"', () => {
        expect(DevicesGroups.cameraAddedAlertText).toHaveTextEqual('Камеры успешно добавлены');
    });

    it('добавленная камера отображается в списке "камеры"', () => {
        DevicesGroups.cameraAddedCheck(findSN);
    });

    it('Почистить данные', () => {
        DevicesGroups.deleteGroupByName(name);
    });
});
