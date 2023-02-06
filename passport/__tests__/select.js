import select from '../select.js';

const state = {
    settings: {
        tld: 'com',
        ua: {
            isTouch: true
        }
    },
    common: {
        track_id: '00000',
        magic_csrf_token: '11111'
    }
};

describe('select', () => {
    it('returns proper props from store', () => {
        const props = select(state);

        expect(props).toEqual({
            tld: 'com',
            isTouch: true,
            trackId: '00000',
            magicCSRFToken: '11111'
        });
    });
});
