const CameraList = require('../../page/signalq/CameraList');
const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. Удаление группы - проверка состояния камеры', () => {
    const name = 'opteum483';
    const SN = '3265365765294316';
    const findSN = `SN ${SN}`;
    const IMEI = '778555551538342';

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

    it('Удалить подготовленную группу', () => {
        DevicesGroups.deleteGroupByName(name);
    });

    it('Перейти в раздел "Все камеры"', () => {
        CameraList.goTo();
    });

    it('Найти подготовленную камеру', () => {
        CameraList.findCamera(SN);
    });

    it('Камера включена', () => {
        expect(CameraList.getRow().status).not.toHaveTextEqual('Удалена');
    });

    it('Нажать на подготовленную камеру', () => {
        CameraList.getRow().serialNumber.click();
    });

    it('В сайдбаре отображается пустой селектор группы', () => {
        expect(CameraList.getCameraCard().group).toHaveTextEqual('Выбрать');
    });

});
