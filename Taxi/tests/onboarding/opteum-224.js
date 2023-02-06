const Onboarding = require('../../page/signalq/Onboarding');
const {assert} = require('chai');

describe('SignalQ: онбординг: добавление камеры: попап: верстка', () => {
    it('открыт раздел "С чего начать"', () => {
        Onboarding.goTo();
    });

    it('Нажать кнопку "Добавить камеру" и заполнить форму релевантными данными', () => {
        Onboarding.addCamera();
        Onboarding.getCameraPopUpElement().header.waitForDisplayed({timeout: 10_000});
    });

    it('Проверить соответствие всех элементов попапа ожиданиям', () => {
        assert.equal(Onboarding.getCameraPopUpElement().header.getText(), 'Камера появилась в парке');
        assert.isTrue(Onboarding.getCameraPopUpElement().acceptButton.isExisting());
        assert.isTrue(Onboarding.getCameraPopUpElement().allCamerasButton.isExisting());
        assert.isTrue(Onboarding.getCameraPopUpElement().closeButton.isExisting());
    });

    it('Закрыть попап по крестику в правом верхнем углу', () => {
        Onboarding.getCameraPopUpElement().closeButton.click();
        Onboarding.getCameraPopUpElement().closeButton.waitForDisplayed({reverse: true, timeout: 10_000});
    });
});
