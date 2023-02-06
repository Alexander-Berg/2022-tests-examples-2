import config from '../config';

describe('dashboard config', () => {
    it('returns right object', () => {
        const obj = config('ru');

        expect(obj.disk).toEqual({
            main: 'https://disk.yandex.ru',
            feed: 'https://disk.yandex.ru/client/feed',
            pay: [
                'https://disk.yandex.ru/payment/10gb_1m',
                'https://disk.yandex.ru/payment/100gb_1m',
                'https://disk.yandex.ru/payment/1tb_1m'
            ]
        });
        expect(obj.music).toEqual({
            main: 'https://music.yandex.ru',
            startTrial: 'https://music.yandex.ru/apps',
            startCommon: 'https://music.yandex.ru/pay',
            settings: 'https://music.yandex.ru/settings/account'
        });
        expect(obj.money).toEqual({
            main: 'https://money.yandex.ru'
        });
        expect(obj.market).toEqual({
            main: 'https://market.yandex.ru',
            settings: 'https://market.yandex.ru/my/settings',
            orders: 'https://market.yandex.ru/my/orders',
            wishlist: 'https://market.yandex.ru/my/wishlist'
        });
        expect(obj.video).toEqual({
            main: 'https://yandex.ru/video',
            favorites: 'https://yandex.ru/video/favorites'
        });
        expect(obj.images).toEqual({
            main: 'https://yandex.ru/images'
        });
        expect(obj.maps).toEqual({
            main: 'https://yandex.ru/maps',
            bookmarks: 'https://yandex.ru/maps/?mode=bookmarks&bookmarks=true',
            bookmark:
                // eslint-disable-next-line max-len
                'https://yandex.ru/maps/?mode=bookmarks&bookmarks[id]=%bookmark_id%&bookmarks[uri]=%bookmark_uri%&&ll=%coords%&z=16'
        });
        expect(obj.afisha.main).toBe('https://afisha.yandex.ru');
        expect(obj.afisha.users).toBe('https://afisha.yandex.ru/users');
        expect(obj.collections.main).toBe('https://yandex.ru/collections');
    });
    test('methods', () => {
        const obj = config('ru');

        expect(obj.afisha.favorites('user')).toBe('https://afisha.yandex.ru/users/user');
        expect(obj.collections.favorites('user')).toBe('https://yandex.ru/collections/user/user');
    });
});
