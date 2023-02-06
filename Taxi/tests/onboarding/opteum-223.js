const CameraList = require('../../page/signalq/CameraList');
const Onboarding = require('../../page/signalq/Onboarding');

describe('SignalQ: онбординг: добавление камеры', () => {
    it('открыт раздел "С чего начать"', () => {
        Onboarding.goTo();
    });

    it('Нажать кнопку "Добавить камеру" и заполнить форму релевантными данными', () => {
        Onboarding.addCamera();
        Onboarding.getCameraPopUpElement().header.waitForDisplayed({timeout: 10_000});
        expect(Onboarding.getCameraPopUpElement().header).toHaveText('Камера появилась в парке');
    });

    it('В модалке нажать кнопку "Все камеры"', () => {
        Onboarding.getCameraPopUpElement().allCamerasButton.click();
        CameraList.findCamera(Onboarding.testCameraSN);
        CameraList.getRow().serialNumber.waitForDisplayed({timeout: 10_000});
        expect(CameraList.getRow().serialNumber).toHaveText(Onboarding.testCameraSN);
    });
});
