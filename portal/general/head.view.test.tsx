import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { Head__content } from '@block/head/head.view';

describe('head', function() {
    it('содержит .ico фавиконку', function() {
        let head = execView(Head__content, {}, mockReq({}, {
            BrowserDesc: {
                OSFamily: 'Windows',
                BrowserEngine: 'Trident',
                BrowserEngineVersion: '4.0',
                isBrowser: 1,
                OSName: 'Windows 7',
                isMobile: 0,
                isTouch: 0,
                localStorageSupport: 1,
                BrowserVersion: '8.0',
                OSVersion: '6.1',
                BrowserName: 'MSIE',
                postMessageSupport: 1
            },
            JSON: {}
        }));

        expect(head).toMatch(/link\s+rel="shortcut icon" href="([^"]+?).ico"/);
    });
});
