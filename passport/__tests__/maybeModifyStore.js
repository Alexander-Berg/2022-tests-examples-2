import {maybeModifyStore} from '../maybeModifyStore';

describe('maybeModifyStore', () => {
    it.each([
        [{query: {}, body: {}}, {locals: {store: {common: {experiments: {flags: []}}, auth: {}}, ua: {}}}, undefined],
        [
            {query: {}, body: {}},
            {locals: {store: {common: {experiments: {flags: ['auth-book-qr-exp']}}, auth: {}}, ua: {}}},
            true
        ],
        [
            {query: {}, body: {}},
            {locals: {store: {common: {experiments: {flags: ['auth-book-qr-exp']}}, auth: {}}, ua: {isMobile: true}}},
            false
        ],
        [
            {query: {}, body: {}},
            {locals: {store: {common: {experiments: {flags: ['auth-book-qr-exp']}}, auth: {}}, ua: {isTouch: true}}},
            false
        ],
        [
            {query: {}, body: {}},
            {locals: {store: {common: {experiments: {flags: ['auth-book-qr-exp']}}, auth: {}}, ua: {isTablet: true}}},
            true
        ],
        [
            {query: {}, body: {}},
            {
                locals: {
                    store: {
                        customs: {isWhiteLabel: true},
                        common: {experiments: {flags: ['auth-book-qr-exp']}},
                        auth: {}
                    },
                    ua: {}
                }
            },
            false
        ]
    ])('should return correct value isBookQREnabled for req %o res %o expected: %s', (req, res, expected) => {
        const next = jest.fn();

        maybeModifyStore(req, res, next);

        expect(res.locals.store.auth.isBookQREnabled).toEqual(expected);
        expect(next).toBeCalled();
    });
});
