const CameraList = require('../../page/signalq/CameraList');

describe('SignalQ. Все камеры. Привязка авто.', () => {
    const SN = CameraList.testCameraSN;
    const ts = 'А133АА75';

    it('открыт раздел "Все камеры"', () => {
        CameraList.goTo();
    });

    it('Добавить камеру', () => {
        CameraList.addCamera();
    });

    it('Привязать машину', () => {
        CameraList.findCamera(SN);
        CameraList.getRow().serialNumber.click();

        if (CameraList.linkVehicleButton.getText() !== 'Привязать к транспорту') {
            CameraList.linkVehicleButton.click();
            browser.refresh();
            CameraList.getRow().serialNumber.waitForDisplayed();
            CameraList.getRow().serialNumber.click();
        }

        CameraList.linkVehicle(ts);
    });

    it('Проверить, что машина привязана', () => {
        browser.refresh();
        browser.pause(300);

        if (CameraList.getRow().tsNumber.getText() !== ts) {
            browser.pause(1000);
        }

        expect(CameraList.getRow().tsNumber).toHaveTextEqual(ts);
    });

});
