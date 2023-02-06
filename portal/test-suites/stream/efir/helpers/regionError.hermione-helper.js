'use strict';

const {PAGEDATA} = require('../PAGEDATA');

const regionErrorTest = function (path = PAGEDATA.url.path) {
    describe('Страница недоступности в регионе', function () {
        it('Показывается заглушка', async function() {
            await this.browser.yaOpenMorda({
                path: path,
                usemock: PAGEDATA.mocks.regionError,
                expectations: {
                    ignoreErrorsSource: /console-api/,
                    ignoreErrorsMessage: /(\/\/an\.yandex\.ru.*video-category-id)|(\/carousels_videohub.json)|(\/episodes.json)/
                }
            });

            await this.browser.execute(function () {
                document.documentElement.className += ' font_loaded';
            });

            await this.browser.$(PAGEDATA.classNames.screens.errorRegion).then(elem => elem.waitForDisplayed());
            await this.browser.yaAssertViewport('errorMessage', {});
        });

    });

};

module.exports = {
    regionErrorTest
};
