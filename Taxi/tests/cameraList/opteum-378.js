const CameraList = require('../../page/signalq/CameraList');

describe('SignalQ. Все камеры. Просмотр данных камер', () => {
    const SN = CameraList.testCameraSN;

    it('открыт раздел "Все камеры"', () => {
        CameraList.goTo();
    });

    it('Добавить камеру', () => {
        CameraList.addCamera();
    });

    it('Открыть камеру', () => {
        CameraList.findCamera(SN);
        CameraList.getRow().serialNumber.click();
    });

    it('Проверить данные в карточке', () => {
        expect(CameraList.getCameraCard().sn).toHaveTextContaining(SN);
        expect(CameraList.getCameraCard().streamButton).toHaveElemExist();
        expect(CameraList.getCameraCard().historyTitle).toHaveElemExist();
        expect(CameraList.getCameraCard().mapButton).toHaveElemExist();
        expect(CameraList.getCameraCard().deleteButton).toHaveElemExist();
        expect(CameraList.getCameraCard().geo).toHaveElemExist();
        expect(CameraList.getCameraCard().imei).toHaveElemExist();
        expect(CameraList.getCameraCard().driver).toHaveElemExist();
        expect(CameraList.getCameraCard().linkVehicleButton).toHaveElemExist();
        expect(CameraList.getCameraCard().group).toHaveElemExist();
        expect(CameraList.getCameraCard().monitoringCenterButton).toHaveElemExist();
    });

    it('Удалить камеру', () => {
        CameraList.deleteCamera();
    });

    it('Проверить данные в карточке', () => {
        browser.refresh();
        CameraList.getRow().serialNumber.waitForDisplayed();
        CameraList.getRow().serialNumber.click();

        expect(CameraList.getCameraCard().sn).toHaveTextContaining(SN);
        expect(CameraList.getCameraCard().imei).toHaveElemExist();
        expect(CameraList.getCameraCard().monitoringCenterButton).toHaveElemExist();
    });

});
