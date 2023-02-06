'use strict';

specs('meta name=description', function () {
    it('На странице есть <meta name="description">', async function () {
        await this.browser.yaOpenMorda({
            expectations: {
                ignoreErrorsMessage: /Incorrect layoutName/
            }
        });
        await this.browser.$('meta[name="description"]').then(elem => elem.waitForExist());
    });
});
