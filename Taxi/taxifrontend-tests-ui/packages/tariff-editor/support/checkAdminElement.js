const allureReporter = require('@wdio/allure-reporter').default;
const fs = require('fs');
/**
 * Сравнение скриншотов элемента страницы в тестинге и анстейбле
 *
 * @param {object} тег для элемента и селектор элемента
 * @param {string} путь до страницы с элементом, хост не нужно указывать
 * @param {string} тэг для названия файла скришота и шага теста, если элементов несколько
 * @param {function} шаги кейса, необязательно
 */

module.exports = async (elements, url, steps) => {
    // Рефреш на пятисотки
    async function checkErrorAndRefresh() {
        await browser.pause(500);
        if (await browser.$('.ModalError__error').isExisting()) {
            await console.log(
                'Получена ошибка: ' + (await browser.$('.ModalError__error-text').getText())
            );
            await console.log('Перезагружаем страницу...');
            await browser.refresh();
        }
    }

    await browser.url('https://tariff-editor.taxi.tst.yandex-team.ru' + url);

    await checkErrorAndRefresh();

    if (steps) {
        await steps();
    }

    const currentDate = Date.now();

    for (const tag of Object.keys(elements)) {
        const filename = tag + '-' + currentDate;
        const elem = elements[tag];
        await browser.$(elem).waitForDisplayed({timeout: 15000});
        await browser.$(elem).scrollIntoView();
        await browser.checkElement(await $(elem), filename);
    }

    await browser.url('https://tariff-editor.taxi.dev.yandex-team.ru' + url);

    await checkErrorAndRefresh();

    if (steps) {
        await steps();
    }

    // TODO удалять конкретную нотификацию, тк может удалить нужную или вообще не ту
    // Удаление нотификации "Api(api-t) не соответствует окружению unstable"
    await browser.execute('document.querySelector(".Notification__messenger")?.remove()');

    let testPassed = true;
    for (const tag of Object.keys(elements)) {
        const filename = tag + '-' + currentDate;
        const elem = elements[tag];
        await allureReporter.startStep(tag);

        await browser.$(elem).waitForDisplayed({timeout: 15000});
        await browser.$(elem).scrollIntoView();
        const {folders, misMatchPercentage} = await browser.checkElement(await $(elem), filename);

        async function readFileMaybe(filename) {
            if (fs.existsSync(filename)) {
                return fs.readFileSync(filename);
            }
            return null;
        }

        async function addAttachment(tag, folders) {
            const testingScreen = await readFileMaybe(folders.baseline);
            const unstableScreen = await readFileMaybe(folders.actual);
            const diffScreen = await readFileMaybe(folders.diff);
            await allureReporter.addAttachment(`${tag}_testing`, testingScreen);
            await allureReporter.addAttachment(`${tag}_unstable`, unstableScreen);
            if (diffScreen) {
                await allureReporter.addAttachment(`${tag}_diff`, diffScreen);
            }
        }

        if (misMatchPercentage <= 0.05) {
            // скриншоты в каждый шаг отчета
            if (process.env.ALL_SCREENS) {
                await addAttachment(tag, folders);
            }
            await allureReporter.endStep('passed');
        } else {
            await addAttachment(tag, folders);
            await allureReporter.endStep('failed');
            testPassed = false;
        }
    }
    // TODO добавить понятное сообщение об ошибке
    await expect(testPassed).toEqual(true);
};
