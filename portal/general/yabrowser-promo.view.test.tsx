import { execView } from '@lib/views/execView';
import { mockReq, Req3ServerMocked } from '@lib/views/mockReq';

// todo move to imports

describe('yabrowser-promo', function() {
    let req: Req3ServerMocked;
    describe('из yabs', function() {
        beforeEach(function() {
            req = mockReq({}, {
                BrowserDesc: {
                    BrowserEngine: 'Unknown',
                    BrowserName: 'Unknown',
                    OSFamily: 'Unknown',
                    isBrowser: 0,
                    isMobile: 0,
                    isTouch: 0
                },
                DevInstance: 1,
                yabrowserPromoMockData: {
                    id: '',
                    img: {
                        height: '60',
                        url: 'icon_url',
                        width: '60'
                    },
                    linknext: 'linknext_url',
                    text1: 'Браузер с удобным поиском',
                    text2: '',
                    text3: '',
                    url: 'yabro_url'
                }
            });
        });

        it('рисует две ссылки - иконка и текст', function() {
            const data = {
                yabrowserPromoMockData: {
                    id: '',
                    img: {
                        height: '60',
                        url: 'icon_url',
                        width: '60'
                    },
                    linknext: 'linknext_url',
                    text1: 'Браузер с удобным поиском',
                    text2: '',
                    text3: '',
                    url: 'yabro_url'
                }
            };

            let html = execView('YabrowserPromo', data, req);

            expect(html).toEqual(expect.stringContaining('padding-left:30px'));
            expect(html).toEqual(expect.stringContaining('icon_url'));
            expect(html).toEqual(expect.stringContaining('stat:dist.searchlink.browser.link-yabro_url'));
            expect(html).toEqual(expect.stringContaining('stat:dist.searchlink.browser.link-yabro_url'));
            expect(html).toEqual(expect.stringContaining('Браузер с удобным поиском'));
        });

        it('рисует ссылку без иконки', function() {
            const data = {
                yabrowserPromoMockData: {
                    id: '',
                    linknext: 'linknext_url',
                    text1: 'Браузер с удобным поиском',
                    text2: '',
                    text3: '',
                    url: 'yabro_url'
                }
            };

            expect(execView('YabrowserPromo', data, req)).toMatchSnapshot();
        });
    });
});
