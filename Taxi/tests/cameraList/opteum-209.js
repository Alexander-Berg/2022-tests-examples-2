const CameraList = require('../../page/signalq/CameraList');
const MonitoringCenter = require('../../page/signalq/MonitoringCenter');

describe('SignalQ. Все камеры. Редирект по "Центр мониторинга".', () => {
    const SN = CameraList.testCameraSN;

    it('открыт раздел "Все камеры"', () => {
        CameraList.goTo();
    });

    it('Добавить камеру', () => {
        CameraList.addCamera();
    });

    it('Открыть камеру и нажать на кнопку "Центр мониторинга"', () => {
        CameraList.findCamera(SN);
        CameraList.getRow().serialNumber.click();
        CameraList.getCameraCard().monitoringCenterButton.waitForDisplayed();
        CameraList.getCameraCard().monitoringCenterButton.click();
    });

    it('Проверить, что открылся трэд этой камеры', () => {
        MonitoringCenter.selectedCameraSN.waitForDisplayed();
        expect(MonitoringCenter.selectedCameraSN).toHaveTextEqual(SN);

    });

});
