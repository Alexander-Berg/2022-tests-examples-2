const CameraList = require('../../page/signalq/CameraList');
const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. добавление камеры в подгруппу', () => {
    const name = 'opteum454';
    const SN = '2310141310589074';
    const findSN = `SN ${SN}`;
    const IMEI = '374369356367574';

    it('Подготовка тестовых данных', () => {
        CameraList.goTo();
        CameraList.clearCameraData(SN, IMEI);

        DevicesGroups.goTo();
        DevicesGroups.clearOldTestData(name);
        DevicesGroups.addGroup(name);
        DevicesGroups.getGroupByName(name).click();
        browser.pause(300);
        DevicesGroups.addSubGroup(name);
        DevicesGroups.getGroupByName(name).click();
        DevicesGroups.addCamera(findSN);
    });

    it('открыт раздел "Все камеры"', () => {
        DevicesGroups.goTo();
    });

    it('Нажать на группу', () => {
        DevicesGroups.getGroupByName(name).click();
        browser.pause(500);
    });

    it('Нажать на подгруппу', () => {
        DevicesGroups.getSubGroupByName(name).click();
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

    it('добавленная камера отображается в списке "камеры" подгруппы', () => {
        DevicesGroups.cameraAddedCheck(findSN);
    });

    it('добавленная камера отображается в списке "камеры" группы', () => {
        DevicesGroups.getGroupByName(name).click();
        browser.pause(500);

        DevicesGroups.cameraAddedCheck(findSN);
    });

    it('добавленная камера не отображается в списке "камеры" подгруппы "все остальные"', () => {
        DevicesGroups.getSubGroupByName('Все остальные').click();
        browser.pause(500);

        expect(DevicesGroups.noCameraText).toHaveTextEqual('Пока нет ни одной камеры');

    });

    it('Почистить данные', () => {
        DevicesGroups.deleteGroupByName(name);
    });
});
