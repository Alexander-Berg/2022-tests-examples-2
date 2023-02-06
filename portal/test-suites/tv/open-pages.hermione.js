'use strict';

specs('open-pages', function () {
    it('index', async function() {
        await this.browser.yaOpenMorda();

        await this.browser.yaInsertCSS(`.rows:before {
                background: darkcyan !important;
            }`);

        const value = await this.browser.yaInBrowser(function () {
            return document.querySelectorAll('.news__pane_current_yes .news__item').length;
        });

        value.should.equal(5);

        await this.browser.assertView('search', '.main__row_arrow');
    });
});
