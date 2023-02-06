const createStore = require('../createStore');

describe('authSilent', () => {
    describe('createStore', () => {
        const req = {
            _controller: {
                getTld: jest.fn().mockReturnValue('ru'),
                getUrl: jest.fn().mockReturnValue({hostname: 'https://passport.yandex.ru'})
            }
        };
        const next = jest.fn();

        beforeEach(() => {
            next.mockReset();
        });

        it('Should run next()', () => {
            const res = {locals: {}};

            createStore(req, res, next);

            expect(next).toBeCalled();
        });
        it('Should save retpath to store from validateRetpath', () => {
            const retpath = 'test/ret/path';
            const res = {locals: {result: {validateRetpath: {retpath}}}};

            createStore(req, res, next);

            expect(new URL(res.locals.store.main.url).searchParams.get('url')).toEqual(retpath);
        });
        it('Should save default retpath to store if validateRetpath not exist', () => {
            const res = {locals: {}};

            createStore(req, res, next);

            expect(decodeURIComponent(new URL(res.locals.store.main.url).searchParams.get('url'))).toEqual(
                '[https://passport.yandex.ru]/profile'
            );
        });
        it('should add BrowserName to mainURL', () => {
            const res = {locals: {ua: {BrowserName: 'TestBrowser'}}};

            createStore(req, res, next);

            expect(decodeURIComponent(new URL(res.locals.store.main.url).searchParams.get('BrowserName'))).toEqual(
                'TestBrowser'
            );
        });
    });
});
