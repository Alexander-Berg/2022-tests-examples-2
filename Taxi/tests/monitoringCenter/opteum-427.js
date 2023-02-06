const CameraList = require('../../page/signalq/CameraList');
const MonitoringCenter = require('../../page/signalq/MonitoringCenter');

describe('SignalQ. Центр мониторинга. Переход в сайдбар камеры', () => {
    let SN;

    it('Открыт раздел "Центр мониторинга"', () => {
        MonitoringCenter.goTo();
    });

    it('Открыть любую камеру в центре мониторинга', () => {
        SN = MonitoringCenter.getSN(3).getText();
        MonitoringCenter.getSN(3).click();
    });

    it('Нажать кнопку "Описание камеры"', () => {
        MonitoringCenter.cameraDescription.click();
        CameraList.getCameraCard().sn.waitForDisplayed();
    });

    it('Проверить, что открылась соответствующая камера', () => {
        expect(CameraList.getCameraCard().sn).toHaveTextIncludes(SN);
    });

});
