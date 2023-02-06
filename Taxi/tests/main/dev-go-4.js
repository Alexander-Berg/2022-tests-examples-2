const Main = require('../../page/Main');

describe('Главная: над чем работаем', () => {

    const BLOCKS = {
        title: [
            'Яндекс Go',
            'Yango',
            'Яндекс.Про',
            'Яндекс.Еда',
            'Яндекс.Лавка и Deli',
            'Самокаты',
            'Доставка',
            'SupportAI',
            'SignalQ',
            'Диспатч',
            'Динамическое ценообразование',
            'Технологическая платформа',
            'ML',
            'Антифрод',
        ],
    };

    const DATA = {
        title: `Над чем работаем${BLOCKS.title.length}`,
    };

    it('Открыть главную страницу', () => {
        Main.goTo();
    });

    it(`Отображается заголовок "${DATA.title}"`, () => {
        Main.projectsBlock.title.scrollIntoView();
        expect(Main.projectsBlock.title).toHaveTextEqual(DATA.title);
    });

    it('Отображаются корректные названия блоков', () => {
        expect(Main.projectsBlock.blocks.title).toHaveTextEqual(BLOCKS.title);
    });

    it(`Текст первого блока "${BLOCKS.title[0]}" отображается по умолчанию`, () => {
        expect(Main.projectsBlock.blocks.getChild(1)).toBeDisplayed();
    });

    it(`Сворачиваем блок "${BLOCKS.title[0]}"`, () => {
        Main.projectsBlock.blocks.getChild(1).click();
    });

    it(`Текст блока "${BLOCKS.title[0]}" не отображается`, () => {
        expect(Main.projectsBlock.blocks.getChild(1)).not.toBeDisplayed();
    });

    BLOCKS.title.forEach((elem, i) => {
        const childNum = ++i;

        it(`Текст блока "${elem}" не отображается`, () => {
            expect(Main.projectsBlock.blocks.getChild(childNum)).not.toBeDisplayed();
        });

        it(`Разворачиваем блок "${elem}"`, () => {
            Main.projectsBlock.blocks.getChild(childNum).click({js: true});
        });

        it(`Текст блока "${elem}" отображается`, () => {
            expect(Main.projectsBlock.blocks.getChild(childNum)).toBeDisplayed();
        });

        it(`Текст блока "${elem}" корректный`, () => {
            expect(Main.projectsBlock.blocks.getChild(childNum)).toHaveTextOk();
        });
    });

});
