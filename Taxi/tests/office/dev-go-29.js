const Office = require('../../page/Office');
const re = require('../../../../utils/consts/re');

describe('Офис: общий текст', () => {

    const DATA = {
        sidebar: {
            vacancies: {
                text: 'Все вакансии',
                link: '/vacancies',
            },
        },
        date: '12 октября 2021',
        headers: [
            'А ещё и зарплата',
            'Гибкий график',
            'ДМС, терапевт и массажист в офисе',
            'Компенсация питания',
            'Обучение и участие в конференциях',
            'Библиотека',
            'Тренажёрные залы, спортивные клубы и турники в офисе',
            'Специальные предложения',
            'Помощь с ипотекой',
        ],
    };

    it('Открыть страницу офиса', () => {
        Office.goTo();
    });

    it('В сайдбаре отображается ссылка на вакансии', () => {
        expect(Office.sidebarBlock.vacancies).toHaveTextEqual(DATA.sidebar.vacancies.text);
        expect(Office.sidebarBlock.vacancies).toHaveAttributeEqual('href', DATA.sidebar.vacancies.link);
    });

    it('Перед заголовком отображается дата', () => {
        expect(Office.mainBlock.date).toHaveTextEqual(DATA.date);
    });

    it('Отображаются корректные заголовки', () => {
        expect(Office.mainBlock.headers).toHaveTextEqual(DATA.headers);
    });

    it('Отображаются корректные тексты', () => {
        expect(Office.mainBlock.texts).toHaveTextOk();
    });

    it('Отображаются корректные цитаты в сниппетах руководителей', () => {
        expect(Office.mainBlock.team.quote).toHaveTextOk();
    });

    it('В сниппетах руководителей отображаются корректные имена', () => {
        expect(Office.mainBlock.team.name).toHaveTextMatch(re.nameSurname);
    });

    it('В сниппетах руководителей отображаются корректные аватарки', () => {
        expect(Office.mainBlock.team.avatar).toHaveAttributeMatch('src', re.avatarPic);
        expect(Office.mainBlock.team.avatar).toHaveAttributeLinkRequestStatus('src', 200);
    });

    it('В сниппетах руководителей отображаются корректные должности', () => {
        expect(Office.mainBlock.team.position).toHaveTextOk();
    });

});
