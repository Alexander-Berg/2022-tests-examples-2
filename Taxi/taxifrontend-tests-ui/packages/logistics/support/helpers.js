async function clearInputBackspace(inputSelector) {
    const selectorValue = await browser.$(inputSelector).getValue();
    const backSpaces = new Array(selectorValue.length).fill('Backspace');
    await browser.$(inputSelector).setValue(backSpaces);
}

async function fillAddress(inputSelector, suggestText, inputText) {
    await clearInputBackspace(inputSelector);
    await browser.$(inputSelector).setValue(inputText || suggestText);

    await browser.$(`//*[text()="${suggestText}"]`).waitForClickable({timeout: 20000});
    await browser.$(`//*[text()="${suggestText}"]`).click();
}

async function expectHaveSomeValue(inputSelector) {
    await expect((await browser.$(inputSelector).getValue()).length).toBeGreaterThanOrEqual(1);
}

async function waitSomeValue(inputSelector, timeout, timeoutMsg) {
    await browser.waitUntil(async () => (await $(inputSelector).getValue()) !== '', {
        timeout: timeout,
        timeoutMsg: timeoutMsg
    });
}

module.exports.fillAddress = fillAddress;
module.exports.expectHaveSomeValue = expectHaveSomeValue;
module.exports.waitSomeValue = waitSomeValue;
