const re = require('../../../../utils/consts/re');
const Vacancy = require('../../page/Vacancy');

describe('Вакансии: выбранная вакансия: описание', () => {

    const DATA = {
        sidebar: {
            text: 'Все вакансии',
            link: '/vacancies',
        },
        hr: {
            name: 'Юрий Мещеряков',
            position: 'Руководитель отдела подбора персонала Яндекс Go',
            image: '/avatars/ymshch.jpg',
            text:
                'У нас многоступенчатый отбор — так получается объективнее и быстрее.'
                + ' Сейчас вы отправите резюме, и если всё сложится, то в ближайшие 3-5 дней мы пришлём вам приглашение.'
                + ' Что ждёт вас дальше, читайте на странице для подготовки к интервью.',
            link: '/interview',
        },
    };

    Vacancy.checkPaths.forEach(path => {
        describe(path, () => {

            it('Открыть страницу вакансии', () => {
                Vacancy.goTo(path);
            });

            it('В сайдбаре отображается ссылка на все вакансии', () => {
                expect(Vacancy.sidebarBlock.vacancies).toHaveTextEqual(DATA.sidebar.text);
                expect(Vacancy.sidebarBlock.vacancies).toHaveAttributeEqual('href', DATA.sidebar.link);
            });

            it('Перед названием вакансии отображаются теги вакансии', () => {
                expect(Vacancy.headerBlock.tags).toHaveTextOk();
            });

            it('Отображается название вакансии', () => {
                expect(Vacancy.headerBlock.title).toHaveTextOk();
            });

            it('Отображается аватарка нанимающего', () => {
                expect(Vacancy.headerBlock.team.avatar).toHaveAttributeMatch('src', re.avatarPic);
                expect(Vacancy.headerBlock.team.avatar).toHaveAttributeLinkRequestStatus('src', 200);
            });

            it('Отображается имя нанимающего', () => {
                expect(Vacancy.headerBlock.team.name).toHaveTextMatch(re.nameSurname);
            });

            it('Отображается должность нанимающего', () => {
                expect(Vacancy.headerBlock.team.position).toHaveTextOk();
            });

            it('Отображается текст вакансии', () => {
                Vacancy.descriptionBlock.text.scrollIntoView({block: 'end'});
                expect(Vacancy.descriptionBlock.text).toHaveTextOk();
            });

            it('В конце отображается аватарка руководителя подбора персонала', () => {
                expect(Vacancy.quoteBlock.avatar).toHaveAttributeEqual('src', DATA.hr.image);
                expect(Vacancy.quoteBlock.avatar).toHaveAttributeLinkRequestStatus('src', 200);
            });

            it('Отображается имя руководителя подбора персонала', () => {
                expect(Vacancy.quoteBlock.name).toHaveTextEqual(DATA.hr.name);
            });

            it('Отображается должность руководителя подбора персонала', () => {
                expect(Vacancy.quoteBlock.position).toHaveTextEqual(DATA.hr.position);
            });

            it('Отображается текст руководителя подбора персонала', () => {
                expect(Vacancy.quoteBlock.text).toHaveTextEqual(DATA.hr.text);
            });

            it('В тексте отображается корректная ссылка', () => {
                expect(Vacancy.quoteBlock.link).toHaveAttributeEqual('href', DATA.hr.link);
            });

        });
    });

});
