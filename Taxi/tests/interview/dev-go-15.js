const Interview = require('../../page/Interview');
const re = require('../../../../utils/consts/re');

describe('Интервью: общий текст', () => {

    const DATA = {
        sidebar: {
            vacancies: {
                text: 'Все вакансии',
                link: '/vacancies',
            },
        },
        main: {
            date: '12 октября 2021',
            quote: {
                header: 'Как подготовиться к собеседованию',
            },
            articles: {
                headers: [
                    'Из чего состоит отбор',
                    'Как успешно пройти интервью',
                ],
            },
        },
    };

    it('Открыть страницу интервью', () => {
        Interview.goTo();
    });

    it('В сайдбаре отображается ссылка на вакансии', () => {
        expect(Interview.sidebarBlock.vacancies).toHaveTextEqual(DATA.sidebar.vacancies.text);
        expect(Interview.sidebarBlock.vacancies).toHaveAttributeEqual('href', DATA.sidebar.vacancies.link);
    });

    it('Перед главным блоком отображается дата', () => {
        expect(Interview.mainBlock.date).toHaveTextEqual(DATA.main.date);
    });

    it('В главном блоке отображается заголовок', () => {
        Interview.mainBlock.quote.header.scrollIntoView();
        expect(Interview.mainBlock.quote.header).toHaveTextEqual(DATA.main.quote.header);
    });

    it('В главном блоке отображается аватар сотрудника', () => {
        expect(Interview.mainBlock.quote.avatar).toHaveAttributeMatch('src', re.avatarPic);
        expect(Interview.mainBlock.quote.avatar).toHaveAttributeLinkRequestStatus('src', 200);
    });

    it('В главном блоке отображается имя сотрудника', () => {
        expect(Interview.mainBlock.quote.name).toHaveTextMatch(re.nameSurname);
    });

    it('В главном блоке отображается должность сотрудника', () => {
        expect(Interview.mainBlock.quote.position).toHaveTextOk();
    });

    it('В главном блоке отображается текст', () => {
        expect(Interview.mainBlock.quote.text).toHaveTextOk();
    });

    it('В блоках статей отображаются заголовки', () => {
        expect(Interview.aboutBlock.headers).toHaveTextEqual(DATA.main.articles.headers);
    });

    it('В блоках статей отображается корректный текст', () => {
        expect(Interview.aboutBlock.texts).toHaveTextOk();
    });

    it('В блоках статей отображается корректный список', () => {
        expect(Interview.aboutBlock.ol).toHaveTextOk();
    });

});
