const Office = require('../../page/Office');

describe('Офис: галерея: оверлей', () => {

    let currentPic;

    it('Открыть страницу офиса', () => {
        Office.goTo();
    });

    it('Отображается галерея', () => {
        Office.galleryBlock.block.scrollIntoView({block: 'center'});
        expect(Office.galleryBlock.block).toHaveElemVisible();
    });

    it('В галерее отображается текущая картинка', () => {
        expect(Office.galleryBlock.pics.current).toHaveElemVisible();
        currentPic = Office.galleryBlock.pics.current.getAttribute('src');
    });

    it('Нажать на картинку', () => {
        Office.galleryBlock.pics.current.click();
    });

    it('Отобразился оверлей галереи', () => {
        expect(Office.galleryOverlay.block).toHaveElemExist();
    });

    it('В оверлее отображаются стрелки пагинации', () => {
        expect(Office.galleryOverlay.arrows.left).toHaveElemVisible();
        expect(Office.galleryOverlay.arrows.right).toHaveElemVisible();
    });

    it('В оверлее отображаются картинки', () => {
        expect(Office.galleryBlock.pics.current).toHaveElemVisible();
        expect(Office.galleryBlock.pics.all).toHaveAttributeLinkRequestStatus('src', 200, {js: true});
    });

    it('Нажать на стрелку вперёд', () => {
        Office.galleryOverlay.arrows.right.click();
    });

    it('Ссылка текущей картинки изменилась', () => {
        expect(Office.galleryBlock.pics.current).not.toHaveAttributeArrayIncludes('src', currentPic);
    });

    it('Нажать на стрелку назад', () => {
        Office.galleryOverlay.arrows.left.click({js: true});
    });

    it('Вернулась предыдущая картинка', () => {
        expect(Office.galleryBlock.pics.current).toHaveAttributeArrayIncludes('src', currentPic);
    });

    it('Нажать на крестик', () => {
        Office.galleryOverlay.close.click();
    });

    it('Оверлей галереи скрылся', () => {
        expect(Office.galleryOverlay.block).not.toHaveElemExist();
    });

    it('Отображается обычная галерея', () => {
        expect(Office.galleryBlock.block).toHaveElemVisible();
    });

});
