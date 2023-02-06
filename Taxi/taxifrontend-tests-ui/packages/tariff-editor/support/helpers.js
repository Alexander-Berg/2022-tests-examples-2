/**
 * Эмуляция ручного ввода, используется для полей, где не сработал setValue
 * @param selector
 * @param value
 * @returns {Promise<void>}
 */

async function type(selector, value) {
    await browser.$(selector).click();
    for (let char of value) {
        await browser.keys(char);
    }
}

/**
 * Обновляем страницу и ждем появление нужного селектора
 * @param time
 * @param selector
 * @returns {Promise<void>}
 */

async function waitExistSelectorAndReload(time, selector) {
    let isDisplayed = await browser.$(selector).isDisplayed();
    for (let i = 0; i < time; i += 3000) {
        if (isDisplayed) {
            break;
        } else {
            await browser.refresh();
            await browser.pause(3000);
            isDisplayed = await browser.$(selector).isDisplayed();
        }
    }
    await expect(await browser.$(selector)).toBeDisplayed();
}

module.exports = {type, waitExistSelectorAndReload};
