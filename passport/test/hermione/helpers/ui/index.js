const {expect} = require('chai');

async function setInputValue(browser, selector, value) {
    const loginElement = await browser.$(selector);

    await loginElement.click();
    const selectorValue = await loginElement.getValue();
    const backSpaces = [...new Array(selectorValue.length).fill('Backspace')].concat(value);

    await browser.setValue(selector, backSpaces);
    expect(await browser.getValue(selector)).to.equal(value);
}

module.exports = {
    setInputValue
};
