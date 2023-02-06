const CameraList = require('../../page/signalq/CameraList');

describe('SignalQ. Все камеры. Удаление камеры.', () => {
    const SN = CameraList.testCameraSN;

    it('открыт раздел "Все камеры"', () => {
        CameraList.goTo();
    });

    it('Добавить камеру', () => {
        CameraList.addCamera();
    });

    it('Удалить камеру', () => {
        CameraList.findCamera(SN);
        CameraList.getRow().serialNumber.click();
        CameraList.deleteCamera();
    });

    it('Проверить, что камера удалена', () => {
        expect(CameraList.getRow().status).toHaveTextEqual('Удалена');
    });

});
