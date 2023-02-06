'use strict';

specs('banner', function () {
    var mocks = [
        'hermione_banner_bf_media_image',
        'hermione_banner_bf_media_iframe',
        'hermione_banner_fl_tgo'
    ];

    var refreshMocks = [
        'hermione_banner_fl_tgo2',
        'hermione_banner_bf_media_image',
        'hermione_banner_bf_media_iframe'
    ];

    var watchTimeout = 'hermione_banner_watch';
    var tabTimeout = 'hermione_banner_tab';

    describe('Первая отрисовка + Рефреш по таймауту', function () {
        refreshMocks.map(refreshMock => {
            mocks.map(mock => {
                it(mock + ' -> ' + refreshMock, async function () {
                    await this.browser.yaOpenMorda({
                        getParams: {
                            usemock: [mock, watchTimeout].join(','),
                            usemock_refresh: refreshMock
                        }
                    });
                    await this.browser.yaHover('.headline');
                    await this.browser.assertView('banner', '.b-banner');
                    await this.browser.pause(3000);
                    await this.browser.$('.b-banner_loading_yes').then(elem => elem.waitForExist({reverse: true, timeout: 3000}));
                    await this.browser.$('.b-banner__wrapper').then(elem => elem.waitForExist({reverse: true, timeout: 3000}));
                    await this.browser.$('.b-banner__iframe_refreshed').then(elem => elem.waitForExist({timeout: 3000}));
                    const frame = await this.browser.$('.b-banner__iframe');
                    await this.browser.switchToFrame(frame);
                    await this.browser.yaIgnoreElement('.direct-desktop__logo');
                    await this.browser.switchToParentFrame();
                    await this.browser.assertView('refresh', '.b-banner');
                });
            });
        });
    });

    describe('Рефреш по табу', function () {
        refreshMocks.map(refreshMock => {
            mocks.map(mock => {
                it(mock + ' -> ' + refreshMock, async function () {
                    await this.browser.yaOpenMorda({
                        getParams: {
                            usemock: [mock, tabTimeout].join(','),
                            usemock_refresh: refreshMock
                        }
                    });

                    await this.browser.yaHover('.headline');
                    await this.browser.pause(3000);
                    await this.browser.$('.b-banner').then(elem => elem.click());
                    await this.browser.yaSwitchTab();
                    await this.browser.pause(4000);
                    await this.browser.yaSwitchTab();
                    await this.browser.yaHover('.headline');

                    await this.browser.$('.b-banner_loading_yes').then(elem => elem.waitForExist({reverse: true, timeout: 3000}));
                    await this.browser.$('.b-banner__wrapper').then(elem => elem.waitForExist({reverse: true, timeout: 3000}));
                    await this.browser.$('.b-banner__iframe_refreshed').then(elem => elem.waitForExist({timeout: 3000}));
                    const frame = await this.browser.$('.b-banner__iframe');
                    await this.browser.switchToFrame(frame);
                    await this.browser.yaIgnoreElement('.direct-desktop__logo');
                    await this.browser.switchToParentFrame();
                    await this.browser.assertView('refresh', '.b-banner');
                });
            });
        });
    });
});
