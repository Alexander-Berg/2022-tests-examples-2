const ScoringPage = require('../../page/ScoringPage');

describe('Скоринг: водитель без купленной истории: вопросы', () => {

    const DATA = {
        faq: {
            title:
                'Популярные вопросы\n'
                + 'Подробнее об «Истории водителя»',
            questions: [
                'Как происходит оплата?\nСумма будет удержана из следующей выплаты парку',
                'Как посмотреть купленный отчёт?\nИнформация, актуальная на дату покупки, отобразится после ввода водительского удостоверения',
                'В стоимость включён НДС?\nСтоимость услуги указана без НДС',
                'Как узнать, сколько я заплатил за сервис «История водителя»?\nУдержанную сумму можно посмотреть в детализации платежного поручения в разделе «Выплаты»',
            ],
            extra: 'Каких данных вам не хватает в подробном отчёте? Поделитесь своим мнением',
        },
        path: '/knowledge-base/drivers-history.html',
    };

    it('Открыть страницу скоринга водителей', () => {
        ScoringPage.goTo('?license=7716235662');
    });

    it('Отображается заголовок ответов на вопросы', () => {
        expect(ScoringPage.faq.title).toHaveTextEqual(DATA.faq.title);
    });

    it('Отображаются ответы на вопросы', () => {
        expect(ScoringPage.faq.questions).toHaveTextEqual(DATA.faq.questions);
    });

    it('Отображается дополнительный текст', () => {
        expect(ScoringPage.faq.extra).toHaveTextEqual(DATA.faq.extra);
    });

    it('Нажать на кнопку в заголовке блока', () => {
        ScoringPage.faq.about.click();
    });

    it('Открылась корректная страница', () => {
        ScoringPage.switchTab();
        expect(browser).toHaveUrlContaining(DATA.path);
    });

});
