const CameraList = require('../../page/signalq/CameraList');

describe('SignalQ. Все камеры. Редирект в "Инструкция по монтажу"', () => {
    const link = 'https://signalq.yandex/support/installation';

    it('открыт раздел "Все камеры"', () => {
        CameraList.goTo();
    });

    it('Нажать кнопку "добавить камеру"', () => {
        CameraList.addButton.click();
    });

    it('Нажать на ссылку "Инструкция по монтажу"', () => {
        CameraList.instructionsLink.click();
    });

    it(`Открылась страница ${link}`, () => {
        expect(browser).toHaveUrl(link);
    });

});
