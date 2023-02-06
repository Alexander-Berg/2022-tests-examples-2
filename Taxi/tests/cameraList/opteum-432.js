const CameraList = require('../../page/signalq/CameraList');

describe('SignalQ. Все камеры. Поиск по группе камер (негатив)', () => {
    const emptyGroup = 'empty';
    const placeholderText = 'Пока ничего нет';

    it('открыт раздел "Все камеры"', () => {
        CameraList.goTo();
    });

    it('Выбрать в селекторе "Выбрать группу" группу у которой нет камеры', () => {
        CameraList.groupFilter.click();
        CameraList.groupFilterInput.addValue(emptyGroup);
        browser.keys('Enter');
    });

    it(`Отобразилось сообщение ${placeholderText}`, () => {
        expect(CameraList.reportTable.notFound).toHaveTextEqual(placeholderText);
    });

});
