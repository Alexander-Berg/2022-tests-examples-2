module.exports = async (page, scenario, vp) => {
    await page.setExtraHTTPHeaders({
        'Accept-Language': 'en;q=0.9'
    });
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36');
    // await require('./loadCookies')(page, scenario);
};
