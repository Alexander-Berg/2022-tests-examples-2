const Header = require('../../page/Header');
const Main = require('../../page/Main');

describe('Главная: заголовок', () => {

    // текст разбит спанами в разных нодах
    const TITLE = [
        'Всё о разработчиках Яндекс Go:',
        'о нас',
        ',',
        '22',
        'наших проектах14',
        'и вакансиях',
        '.',
        '21',
    ].join('\n');

    const LINKS = [
        {name: 'о нас', link: '/#team', block: Main.sections.team},
        {name: 'наших проектах', link: '/#projects', block: Main.sections.projects},
        {name: 'вакансиях', link: '/#vacancies', block: Main.sections.vacancies},
    ];

    it('Открыть главную страницу', () => {
        Main.goTo();
    });

    it('Отображается заголовок', () => {
        Header.headerBlock.title.text.scrollIntoView();
        expect(Header.headerBlock.title.text).toHaveTextEqual(TITLE);
    });

    LINKS.forEach(({name, link, block}, i) => {
        it(`Отображается ссылка ${name}`, () => {
            expect(Header.headerBlock.title.links[i]).toBeDisplayed();
            expect(Header.headerBlock.title.links[i]).toHaveTextEqual(name);
            expect(Header.headerBlock.title.links[i]).toHaveAttributeArrayIncludes('href', link);
        });

        it(`По клику на "${name}" страница скроллится к этому блоку`, () => {
            Header.headerBlock.title.links[i].click();

            const elem = $(block);
            expect(elem).toBeDisplayed();
        });

        // в конце теста скролл не нужен
        if (i !== LINKS.length - 1) {
            it('Скроллим страницу наверх', () => {
                Main.scroll({y: -99_999});
            });
        }
    });

});
