const ListStatementsPage = require('../../page/ListStatementsPage');
const {assert} = require('chai');

const timeToWaitElem = 5000;
let video;

describe('Просмотр обучающего ролика', () => {
    it('Нажать на ссылку "Как это работает" в правом верхнем углу страницы', () => {
        ListStatementsPage.goTo();
        ListStatementsPage.howItWorksWindow.howItWorksButton.click();

        ({video} = ListStatementsPage.howItWorksWindow);
        video.waitForDisplayed({timeout: timeToWaitElem});

        assert.isTrue(ListStatementsPage.howItWorksWindow.text1.isDisplayed());
        assert.isTrue(ListStatementsPage.howItWorksWindow.text2.isDisplayed());
        assert.isTrue(ListStatementsPage.howItWorksWindow.text3.isDisplayed());
    });

    it('Нажать на кнопку воспроизведения видео', () => {
        video.click();
    });

    it('Просмотреть видео до конца', () => {
        const videoTimeInMs = browser.execute("return document.getElementsByTagName('video')[0].duration;") * 1000 + 2000;
        browser.pause(videoTimeInMs);

        // видео корректно доигралось
        assert.isTrue(browser.execute("return document.getElementsByTagName('video')[0].ended;"));
    });

    it('Нажать на кнопку крестика в правом верхнем углу', () => {
        ListStatementsPage.howItWorksWindow.closeButton.click();

        // закрылось окно видео
        video.waitForDisplayed({timeout: timeToWaitElem, reverse: true});
        // отобразился список ведомостей
        assert.isTrue(ListStatementsPage.getRowInTable().status.waitForDisplayed({timeout: timeToWaitElem}));
    });
});
