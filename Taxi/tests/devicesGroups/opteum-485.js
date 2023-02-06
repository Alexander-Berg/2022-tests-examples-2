const CameraList = require('../../page/signalq/CameraList');
const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. создание подгрупп с одинаковыми именами', () => {
    const name = 'opteum485';
    const SN = '1654727415073230';
    const findSN = `SN ${SN}`;
    const IMEI = '486849659529184';

    it('Подготовка тестовых данных', () => {
        CameraList.goTo();
        CameraList.clearCameraData(SN, IMEI);

        DevicesGroups.goTo();
        DevicesGroups.clearOldTestData(name);
        DevicesGroups.addGroup(name);
    });

    it('Создать две подгруппы с одинаковыми названиями', () => {
        DevicesGroups.getGroupByName(name).click();
        browser.pause(300);
        DevicesGroups.addSubGroup(name);
        DevicesGroups.getGroupByName(name).click();
        browser.pause(300);
        DevicesGroups.addSubGroup(name);
    });

    it('Добавить в одну из подгрупп камеру', () => {
        DevicesGroups.getGroupByName(name).click();
        browser.pause(300);
        DevicesGroups.addCamera(findSN);
        DevicesGroups.getSubGroupByName(name).click();
        browser.pause(300);
        DevicesGroups.addCamera(findSN);
    });

    it('Камера отображается в первой подгруппе', () => {
        DevicesGroups.cameraAddedCheck(findSN);
        DevicesGroups.subGroupDropdownButton.click();
        DevicesGroups.deleteButton.click();
        DevicesGroups.confirmDeleteButton.click();
    });

    it('Камера не отображается во второй подгруппе', () => {
        DevicesGroups.goTo();
        DevicesGroups.getGroupByName(name).click();
        browser.pause(300);
        DevicesGroups.getSubGroupByName(name).click();
        expect(DevicesGroups.noCameraText).toHaveTextEqual('Пока нет ни одной камеры');
    });

    it('Почистить данные', () => {
        DevicesGroups.deleteGroupByName(name);
    });

});
