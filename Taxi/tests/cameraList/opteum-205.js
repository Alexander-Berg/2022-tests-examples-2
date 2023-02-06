const CameraList = require('../../page/signalq/CameraList');

describe('SignalQ. Все камеры. Добавление камеры. (Негатив)', () => {
    const SNHint = 'Неправильный SN — должны быть цифры 0–9 и буквы A–F';
    const IMEIHint = 'Неправильный IMEI — должно быть 15 цифр';

    const hintsExpect = () => {
        CameraList.inputSNhint.waitForDisplayed();
        expect(CameraList.inputSNhint).toHaveText(SNHint);
        expect(CameraList.inputIMEIhint).toHaveText(IMEIHint);
    };

    it('открыт раздел "Все камеры"', () => {
        CameraList.goTo();
    });

    it('Нажать кнопку "добавить камеру"', () => {
        CameraList.addButton.click();
    });

    it('Ничего не вводим и нажимаем "Добавить в парк"', () => {
        CameraList.addToParkButton.click();

        hintsExpect();
    });

    it('В поле SN вводим GGGG и нажимаем "Добавить в парк"', () => {
        CameraList.inputSN.addValue('GGGG');
        CameraList.addToParkButton.click();

        hintsExpect();
    });

    it('Стираем предыдущие значения. В поле SN вводим 1111 и нажимаем "Добавить в парк"', () => {
        CameraList.clearWithBackspace(CameraList.inputSN);
        CameraList.inputSN.addValue('1111');
        CameraList.addToParkButton.click();

        hintsExpect();
    });

    it('Стираем предыдущие значения. В поле IMEI вводим 1111111 и нажимаем "Добавить в парк"', () => {
        CameraList.clearWithBackspace(CameraList.inputSN);
        CameraList.inputIMEI.addValue('1111111');
        CameraList.addToParkButton.click();

        hintsExpect();
    });

});
