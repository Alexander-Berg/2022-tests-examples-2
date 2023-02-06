'use strict';

specs('touch-news', function () {
    const selector = '[data-key="video"]';
    const link = 'a' + selector;
    const page = '.swiper__page' + selector;

    it('video', async function() {
        await this.browser.yaOpenMorda({getParams: {
            ab_flags: 'topnews_video'
        }});

        await this.browser.execute(function () {
            let row = $('.news');
            scrollTo(0, row.offset().top);
        });

        await this.browser.$(link).then(elem => elem.waitForDisplayed());
        await this.browser.$(link).then(elem => elem.click());
        await this.browser.$(`${page} .news__item:nth-of-type(1)`).then(elem => elem.waitForDisplayed());

        const res = await this.browser.execute((page) => {
            return $(`${page} .news__item`).length;
        }, page);
        res.should.equal(5);
    });
});