const CameraList = require('../../page/signalq/CameraList');

describe('SignalQ. Все камеры. Проверка поиска по таблице.', () => {
    const SN = CameraList.testCameraSN;
    const partOfSN = SN.slice(3, 7);
    const wrongSN = 'FFFFFFFFFF';

    it('открыт раздел "Все камеры"', () => {
        CameraList.goTo();
    });

    it(`В поле поиск ввести ${SN}`, () => {
        CameraList.findCamera(SN);
        expect(CameraList.getRow().serialNumber).toHaveText(SN);
        CameraList.clearSearch();
    });

    it(`В поле поиск ввести ${partOfSN}`, () => {
        CameraList.findCamera(partOfSN);
        expect(CameraList.getRow().serialNumber).toHaveTextContaining(partOfSN);
        CameraList.clearSearch();
    });

    it(`В поле поиск ввести ${wrongSN}`, () => {
        CameraList.findCamera(wrongSN);
        expect(CameraList.reportTable.notFound).toHaveTextContaining('Тут ничего нет');
    });
});
