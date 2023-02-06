const Office = require('../../page/Office');

describe('Офис: галерея: отображение', () => {

    const PICS_COUNT = 8;

    const DATA = {
        page: {
            default: `1/${PICS_COUNT}`,
            second: `2/${PICS_COUNT}`,
            last: `${PICS_COUNT}/${PICS_COUNT}`,
        },
    };

    let currentPic;

    it('Открыть страницу офиса', () => {
        Office.goTo();
    });

    it('Отображается галерея', () => {
        Office.galleryBlock.block.scrollIntoView({block: 'center'});
        expect(Office.galleryBlock.block).toHaveElemVisible();
    });

    it('В галерее отображаются картинки', () => {
        expect(Office.galleryBlock.pics.current).toHaveElemVisible();
        expect(Office.galleryBlock.pics.all).toHaveAttributeLinkRequestStatus('src', 200, {js: true});
        currentPic = Office.galleryBlock.pics.current.getAttribute('src');
    });

    it('Под галереей отображаются стрелки пагинации', () => {
        expect(Office.galleryBlock.arrows.left).toHaveElemVisible();
        expect(Office.galleryBlock.arrows.right).toHaveElemVisible();
    });

    it('Между стрелками отображается текст пагинации', () => {
        expect(Office.galleryBlock.page).toHaveTextEqual(DATA.page.default);
    });

    // вперёд 1/8 => 2/8
    it('Нажать на стрелку вперёд', () => {
        Office.galleryBlock.arrows.right.click();
    });

    it(`Текст пагинации сменился на "${DATA.page.second}"`, () => {
        expect(Office.galleryBlock.page).toHaveTextEqual(DATA.page.second);
    });

    it('Ссылка текущей картинки изменилась', () => {
        expect(Office.galleryBlock.pics.current).not.toHaveAttributeArrayIncludes('src', currentPic);
        currentPic = Office.galleryBlock.pics.current.getAttribute('src');
    });

    // назад 2/8 => 1/8
    it('Нажать на стрелку назад', () => {
        Office.galleryBlock.arrows.left.click();
    });

    it(`Текст пагинации сменился на "${DATA.page.default}"`, () => {
        expect(Office.galleryBlock.page).toHaveTextEqual(DATA.page.default);
    });

    it('Ссылка текущей картинки изменилась', () => {
        expect(Office.galleryBlock.pics.current).not.toHaveAttributeArrayIncludes('src', currentPic);
        currentPic = Office.galleryBlock.pics.current.getAttribute('src');
    });

    // назад 1/8 => 8/8
    it('Нажать на стрелку назад', () => {
        Office.galleryBlock.arrows.left.click();
    });

    it(`Текст пагинации сменился на "${DATA.page.last}"`, () => {
        expect(Office.galleryBlock.page).toHaveTextEqual(DATA.page.last);
    });

    it('Ссылка текущей картинки изменилась', () => {
        expect(Office.galleryBlock.pics.current).not.toHaveAttributeArrayIncludes('src', currentPic);
        currentPic = Office.galleryBlock.pics.current.getAttribute('src');
    });

    it('В галерее по-прежнему отображаются картинки', () => {
        expect(Office.galleryBlock.pics.current).toHaveElemVisible();
        expect(Office.galleryBlock.pics.all).toHaveAttributeLinkRequestStatus('src', 200, {js: true});
    });

});
