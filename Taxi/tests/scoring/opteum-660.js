const ScoringPage = require('../../page/ScoringPage');

describe('Скоринг: водитель без купленной истории: карточки', () => {

    const DATA = {
        buy: {
            title: 'Снизьте риски при найме, купив подробный отчёт',
            text: 'Купите 3 отчёта за сутки, чтобы получить следующие 3 за 50 ₽',
            buttons: [
                'Посмотреть примеры отчётов',
                'Купить за 60 ₽',
            ],
            cards: {
                count: 3,
                titles: [
                    'Вождение',
                    'Активность',
                    'Качество',
                ],
            },
        },
    };

    it('Открыть страницу скоринга водителей', () => {
        ScoringPage.goTo('?license=7716235662');
    });

    it('Отображается заголовок покупки истории', () => {
        expect(ScoringPage.buy.title).toHaveTextEqual(DATA.buy.title);
    });

    it('Под заголовком отображается дополнительный текст покупки истории', () => {
        expect(ScoringPage.buy.text).toHaveTextEqual(DATA.buy.text);
    });

    it('Отображаются кнопки покупки', () => {
        expect(ScoringPage.buy.buttons).toHaveTextEqual(DATA.buy.buttons);
    });

    it(`Отображаются "${DATA.buy.cards.count}" рекламные карточки`, () => {
        expect(ScoringPage.buy.blocks.elements).toHaveElemLengthEqual(DATA.buy.cards.count);
    });

    it('Отображаются иконки в рекламных карточках', () => {
        expect(ScoringPage.buy.blocks.icons).toHaveElemVisible();
    });

    it('Отображаются корректные заголовки в рекламных карточках', () => {
        expect(ScoringPage.buy.blocks.titles).toHaveTextEqual(DATA.buy.cards.titles);
    });

    it('Отображаются корректные тексты в рекламных карточках', () => {
        expect(ScoringPage.buy.blocks.bodies).toHaveTextOk();
    });

});
