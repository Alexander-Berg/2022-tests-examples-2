const CameraList = require('../../page/signalq/CameraList');

describe('SignalQ. Все камеры. Добавление камеры. (позитив)', () => {
    const SN = CameraList.testCameraSN;

    it('открыт раздел "Все камеры"', () => {
        CameraList.goTo();
    });

    it('Удалить камеру', () => {
        CameraList.findCamera(SN);

        if (CameraList.getRow().status.getText() !== 'Удалена') {
            CameraList.getRow().serialNumber.click();
            CameraList.deleteCamera();
        }
    });

    it('Добавить камеру', () => {
        CameraList.addCamera();
    });

    it('Проверить, что камера добавлена', () => {
        CameraList.clearSearch();
        CameraList.findCamera(SN);
        expect(CameraList.getRow().status).not.toHaveText('Удалена');
    });

});
