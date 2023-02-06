import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';

describe('b-sethome', function() {
    let baseReq = mockReq({}, {
        SetHome: {
            show: 1
        },
        set_start_page_link: 1
    });

    it('returns link for chrome', function() {
        let req;

        req = Object.assign({}, baseReq, {
            Chrome: 50,
            BrowserDesc: {
                OSFamily: 'Windows'
            }
        });

        expect(execView('b-sethome', req)).toEqual(expect.stringContaining(execView('b-sethome__links', req).chrome.ru));

        req = Object.assign({}, baseReq, {
            Chrome: 50,
            BrowserDesc: {
                OSFamily: 'MacOS'
            }
        });

        expect(execView('b-sethome', req)).toEqual(expect.stringContaining(execView('b-sethome__links', req).chrome.ru));

        req = Object.assign({}, baseReq, {
            Chrome: 50,
            BrowserDesc: {
                OSFamily: 'Windows'
            },
            options: {
                sethome_chrome_ru_url: 'https://chrome.google.com/sethome_chrome_ru_url/'
            }
        });

        expect(execView('b-sethome', req)).toEqual(expect.stringContaining('https://chrome.google.com/sethome_chrome_ru_url/'));
    });

    it('returns nothing', function() {
        expect(execView('b-sethome', Object.assign({}, baseReq, {
            opera_panel_promo: 1,
            set_start_page_link: 0
        }))).toEqual('');

        expect(execView('b-sethome', Object.assign({}, baseReq, {
            opera_panel_promo: 1,
            SetHome: {
                show: 0
            }
        }))).toEqual('');

        expect(execView('b-sethome', Object.assign({}, baseReq, {
            opera_panel_promo: 1,
            SetHome: {
                show: 1
            },
            options: {
                disable_sethome: 1
            }
        }))).toEqual('');
    });
});
