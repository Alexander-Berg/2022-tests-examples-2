const Rating = require('../../page/Rating');
const timeouts = require('../../../../utils/consts/timeouts');

describe('Рейтинг: блокировка кнопки переключения на предыдущий месяц', () => {

    const DATA = {
        clickError: 'element click intercepted',
    };

    it('Открыть раздел рейтинга', () => {
        Rating.goToWithRating();
    });

    it('Отображается селектор выбора предыдущего месяца', () => {
        expect(Rating.filters.month.buttons.arrows.left).toHaveElemVisible();
    });

    it('Селектор выбора предыдущего месяца кликабелен', () => {
        expect(Rating.filters.month.buttons.arrows.left).toHaveAttributeEqual('aria-disabled', 'false');
    });

    it('Нажимать на селектор выбора предыдущего месяца пока он не станет отключенным', () => {
        browser.waitUntil(() => {
            Rating.filters.month.buttons.arrows.left.click();
            browser.pause(timeouts.waitUntilInterval);
            return Rating.filters.month.buttons.arrows.left.getAttribute('aria-disabled') === 'true';
        }, {
            timeout: timeouts.waitUntilShort,
            timeoutMsg: 'Кнопка выбора предыдущего месяца осталась активной',
        });
    });

    it('На селектор выбора предыдущего месяца нельзя кликнуть', () => {
        expect(() => Rating.filters.month.buttons.arrows.left.click()).toThrowError(DATA.clickError);
    });

});
