'use strict';

specs('open-pages', function () {
    /* Моргает тест
     * message: element (".arrowed-list") still not visible after 10000ms
     */
    it('index', async function() {
        await this.browser.yaOpenMorda({
            path: '/partner-strmchannels/v1',
            getParams: {
                allow_all: 1,
                distr_id: 1111
            }
        });

        await this.browser.$('.arrowed-list').then(elem => elem.waitForDisplayed());
        const link = await this.browser.$('.tvtitle__main').then(elem => elem.getAttribute('href'));
        await link.should.have.string('/efir');
    });
});
