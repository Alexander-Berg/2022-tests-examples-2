const Onboarding = require('../../page/signalq/Onboarding');
const {assert} = require('chai');

describe('SignalQ: онбординг: верстка', () => {
    it('открыт раздел "С чего начать"', () => {
        Onboarding.goTo();
    });

    it('Проверить наличие основных элементов на странице', () => {
        assert.equal(Onboarding.pageHeader.getText(), 'С чего начать');
        assert.isTrue(Onboarding.addCameraButton.isExisting());
    });

    it('Проверить первый раздел', () => {
        assert.equal(Onboarding.getSlideshowContainerElement(1).header.getText(), '«Центр мониторинга» позволяет');
        assert.equal(Onboarding.getSlideshowContainerElement(1).firstButton.getText(), 'История событий');
        assert.equal(Onboarding.getSlideshowContainerElement(1).secondButton.getText(), 'Выбор типов событий');
        assert.equal(Onboarding.getSlideshowContainerElement(1).thirdButton.getText(), 'Салон в реальном времени');
    });

    it('Проверить второй раздел', () => {
        assert.equal(Onboarding.getSlideshowContainerElement(2).header.getText(), '«Статистика» показывает');
        assert.equal(Onboarding.getSlideshowContainerElement(2).firstButton.getText(), 'Дисциплина в парке');
        assert.equal(Onboarding.getSlideshowContainerElement(2).secondButton.getText(), 'Как используются камеры');
        assert.equal(Onboarding.getSlideshowContainerElement(2).thirdButton.getText(), 'Кто нарушает больше других');
    });

    it('Проверить третий раздел', () => {
        assert.equal(Onboarding.getSlideshowContainerElement(3).header.getText(), 'На странице «Все камеры» есть');
        assert.equal(Onboarding.getSlideshowContainerElement(3).firstButton.getText(), 'Статус каждой камеры');
        assert.equal(Onboarding.getSlideshowContainerElement(3).secondButton.getText(), 'Статистика конкретной камеры');
        assert.equal(Onboarding.getSlideshowContainerElement(3).thirdButton.getText(), 'Настройки критичности событий');
    });
});
