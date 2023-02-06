const CameraList = require('../../page/signalq/CameraList');
const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. Удаление камеры из группы', () => {
    const name = 'opteum474';
    const SN = '4927033083983382';
    const findSN = `SN ${SN}`;
    const IMEI = '303850217012044';

    it('Подготовка тестовых данных', () => {
        CameraList.goTo();
        CameraList.clearCameraData(SN, IMEI);

        DevicesGroups.goTo();
        DevicesGroups.clearOldTestData(name);
        DevicesGroups.addGroup(name);
        DevicesGroups.getGroupByName(name).click();
        browser.pause(300);
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

    it('Отображается текст "Пока нет ни одной камеры"', () => {
        expect(DevicesGroups.noCameraText).toHaveTextEqual('Пока нет ни одной камеры');
    });

    it('Почистить данные', () => {
        DevicesGroups.deleteGroupByName(name);
    });
});
