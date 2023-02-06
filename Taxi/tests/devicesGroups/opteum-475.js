const CameraList = require('../../page/signalq/CameraList');
const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. Удаление камеры из подгруппы', () => {
    const name = 'opteum475';
    const SN = '8945285435133588';
    const findSN = `SN ${SN}`;
    const IMEI = '722612481082260';

    it('Подготовка тестовых данных', () => {
        CameraList.goTo();
        CameraList.clearCameraData(SN, IMEI);

        DevicesGroups.goTo();
        DevicesGroups.clearOldTestData(name);
        DevicesGroups.addGroup(name);
        DevicesGroups.getGroupByName(name).click();
        browser.pause(300);
        DevicesGroups.addCamera(findSN);
        DevicesGroups.addSubGroup(name);
        DevicesGroups.getGroupByName(name).click();
        browser.pause(300);
        DevicesGroups.getSubGroupByName(name).click();
        DevicesGroups.addCamera(findSN);
    });

    it('Нажать на кнопку в виде трёх точек около списка "Камер"', () => {
        DevicesGroups.cameraDropdownButton.click();
    });

    it('Нажать кнопку "Удалить камеры"', () => {
        DevicesGroups.deleteCameraButton.click();
    });

    it('Нажать кнопку "удалить" около камеры', () => {
        const position = DevicesGroups.findPosition(DevicesGroups.CameraList, findSN);
        DevicesGroups.getDeleteButton(position).click();
    });

    it('Подтвердить удаление', () => {
        DevicesGroups.confirmDeleteButton.click();
    });

    it('Появилось уведомление "Камеры успешно удалены"', () => {
        expect(DevicesGroups.cameraDeletedAlertText).toHaveTextEqual('Камеры успешно удалены');
    });

    it('Камера не отображается в списке "камеры" подгруппы', () => {
        expect(DevicesGroups.noCameraText).toHaveTextEqual('Пока нет ни одной камеры');
    });

    it('Камера отображается в списке "камеры" группы', () => {
        DevicesGroups.getGroupByName(name).click();
        browser.pause(300);

        DevicesGroups.cameraAddedCheck(findSN);
    });

    it('Камера отображается в списке "камеры" подгруппы "все остальные"', () => {
        DevicesGroups.getSubGroupByName('Все остальные').click();
        browser.pause(300);

        DevicesGroups.cameraAddedCheck(findSN);
    });

    it('Почистить данные', () => {
        DevicesGroups.deleteGroupByName(name);
    });
});
