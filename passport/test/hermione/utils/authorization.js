const ZALOGIN_PAGE = 'https://zalogin-static.s3.mds.yandex.net/auth-page.html';

async function authorize(browser, passportHost, login, password) {
    // Inspired by authorize method in hermione-auth-commands

    // не передаем `retpath` как параметр к запросу, поскольку на url может быть наложена некоторая логика,
    // не применяемая при редиректе
    const passportUrl = `${passportHost}/passport?mode=auth`;
    const params = {passportUrl, login, password};

    const authParam = Buffer.from(decodeURIComponent(JSON.stringify(params))).toString('base64');

    await browser.url(`${ZALOGIN_PAGE}?auth_param=${authParam}`);
    await waitForVisibleWithRetries(browser, '.submit', 2000, 5);
    return browser.click('.submit');
}

async function waitForVisibleWithRetries(browser, selector, timeout, retries) {
    try {
        await browser.waitForVisible(selector, timeout);
    } catch (err) {
        if (retries > 0) {
            return waitForVisibleWithRetries(browser, selector, timeout, retries - 1);
        }
        throw err;
    }
}

module.exports = {
    authorize
};
