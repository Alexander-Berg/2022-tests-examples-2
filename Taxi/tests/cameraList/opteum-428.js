const CameraList = require('../../page/signalq/CameraList');
const GroupList = require('../../page/signalq/GroupList');

describe('SignalQ. Все камеры. отображение групп камер', () => {
    const SN = '001A722A2109722B';
    const IMEI = '494870021788903';
    let group, subGroup;

    it('открыт раздел "Все камеры"', () => {
        CameraList.goTo();
    });

    it('Открыть камеру без группы', () => {
        CameraList.clearCameraData(SN, IMEI);

        CameraList.getRow().status.click();
    });

    it('В пункте группа выбрать любую группу', () => {
        CameraList.getCameraCard().group.click();
        group = GroupList.element().getText();
        GroupList.element().click();
        expect(CameraList.getCameraCard().group).toHaveTextIncludes(group);
    });

    it('Появился пункт "подгруппа"', () => {
        expect(CameraList.getCameraCard().subGroup).toExist();
    });

    it('Группа отображается в таблице в столбце "группа"', () => {
        expect(CameraList.getRow().group).toHaveTextEqual(group);
    });

    it('В пункте подгруппа выбирать любую подгруппу', () => {
        CameraList.getCameraCard().subGroup.click();
        subGroup = GroupList.element().getText();
        GroupList.element().click();
        expect(CameraList.getCameraCard().subGroup).toHaveTextIncludes(subGroup);
    });

    it('Группа и подгруппа отображаются в таблице в столбце "группа"', () => {
        expect(CameraList.getRow().group).toHaveTextEqual(`${group} > ${subGroup}`);
    });
});
