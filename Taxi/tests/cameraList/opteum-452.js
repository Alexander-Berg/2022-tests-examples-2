const CameraList = require('../../page/signalq/CameraList');
const GroupList = require('../../page/signalq/GroupList');

describe('SignalQ. Все камеры. Поиск по подгруппе камер (негатив)', () => {
    const group = 'notEmpty';
    const subGroup = 'empty';
    const SN = '001A826B7EFED2EC';
    const IMEI = '720625637632177';
    const placeholderText = 'Тут ничего нет';

    it('открыт раздел "Все камеры"', () => {
        CameraList.goTo();
    });

    it('Подготовка тестовых данных', () => {
        CameraList.clearCameraData(SN, IMEI);

        CameraList.getRow().status.click();

        CameraList.getCameraCard().group.click();
        const position = GroupList.elementPosition(group);
        GroupList.element(position).click();
    });

    it('Выбрать группу в которой есть камеры и в этом же селекторе подгруппу в которой камер нет', () => {
        CameraList.groupFilter.click();
        CameraList.groupFilterInput.addValue(group);
        browser.keys('Enter');
        CameraList.getRow().status.waitForDisplayed();

        CameraList.groupFilter.click();
        CameraList.groupFilterInput.addValue(subGroup);
        browser.keys('Enter');
    });

    it(`Отобразилось сообщение ${placeholderText}`, () => {
        expect(CameraList.reportTable.notFound).toHaveTextEqual(placeholderText);
    });

});
