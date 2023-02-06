import { execView } from '@lib/views/execView';

// todo move to imports

describe('stream-thumbnail', function() {
    function setDPR(dpr: number) {
        (window as { devicePixelRatio: number }).devicePixelRatio = dpr;
    }

    beforeEach(function() {
        setDPR(1);
    });

    it('должен менять /orig на small размер для get-vh, если размер не указан', function() {
        let resOne = execView('StreamThumbnail', {
            thumbnail: 'https://avatars.mds.yandex.net/get-vh/1/2/orig'
        });

        expect(resOne).toEqual('background-image:url(https://avatars.mds.yandex.net/get-vh/1/2/200x150)');
    });

    it('должен менять /orig на small размер для get-vh, если указан некорректный размер', function() {
        let resOne = execView('StreamThumbnail', {
            thumbnail: 'https://avatars.mds.yandex.net/get-vh/1/2/orig',
            size: 'incorrect'
        });

        expect(resOne).toEqual('background-image:url(https://avatars.mds.yandex.net/get-vh/1/2/200x150)');
    });

    it('должен менять /orig на small размер для get-vh', function() {
        let resOne = execView('StreamThumbnail', {
            thumbnail: 'https://avatars.mds.yandex.net/get-vh/1/2/orig',
            size: 'small'
        });

        expect(resOne).toEqual('background-image:url(https://avatars.mds.yandex.net/get-vh/1/2/200x150)');
    });

    it('должен менять /orig на small размер для get-vh (авторетина + devicePixelRatio 1.6)', function() {
        setDPR(1.6);

        let resOne = execView('StreamThumbnail', {
            autoretina: true,
            thumbnail: 'https://avatars.mds.yandex.net/get-vh/1/2/orig',
            size: 'small'
        });

        expect(resOne).toEqual('background-image:url(https://avatars.mds.yandex.net/get-vh/1/2/400x300)');
    });

    it('должен менять /orig на small размер для get-vh (авторетина + devicePixelRatio 1.3)', function() {
        setDPR(1.22);

        let resOne = execView('StreamThumbnail', {
            autoretina: true,
            thumbnail: 'https://avatars.mds.yandex.net/get-vh/1/2/orig',
            size: 'small'
        });

        expect(resOne).toEqual('background-image:url(https://avatars.mds.yandex.net/get-vh/1/2/200x150)');
    });

    it('должен менять /orig на medium размер для get-vh', function() {
        let resOne = execView('StreamThumbnail', {
            thumbnail: 'https://avatars.mds.yandex.net/get-vh/1/2/orig',
            size: 'medium'
        });

        expect(resOne).toEqual('background-image:url(https://avatars.mds.yandex.net/get-vh/1/2/400x300)');
    });

    it('должен менять /orig на medium размер для get-vh (авторетина + devicePixelRatio 1.6)', function() {
        setDPR(1.6);

        let resOne = execView('StreamThumbnail', {
            autoretina: true,
            thumbnail: 'https://avatars.mds.yandex.net/get-vh/1/2/orig',
            size: 'medium'
        });

        expect(resOne).toEqual('background-image:url(https://avatars.mds.yandex.net/get-vh/1/2/936x524)');
    });

    it('должен менять /orig на medium размер для get-vh (авторетина + devicePixelRatio 1.3)', function() {
        setDPR(1.22);

        let resOne = execView('StreamThumbnail', {
            autoretina: true,
            thumbnail: 'https://avatars.mds.yandex.net/get-vh/1/2/orig',
            size: 'medium'
        });

        expect(resOne).toEqual('background-image:url(https://avatars.mds.yandex.net/get-vh/1/2/400x300)');
    });

    it('должен менять /orig на large размер для get-vh', function() {
        let resOne = execView('StreamThumbnail', {
            thumbnail: 'https://avatars.mds.yandex.net/get-vh/1/2/orig',
            size: 'large'
        });

        expect(resOne).toEqual('background-image:url(https://avatars.mds.yandex.net/get-vh/1/2/936x524)');
    });

    it('должен менять /orig на large размер для get-vh (авторетина + devicePixelRatio 1.6)', function() {
        setDPR(1.6);

        let resOne = execView('StreamThumbnail', {
            autoretina: true,
            thumbnail: 'https://avatars.mds.yandex.net/get-vh/1/2/orig',
            size: 'large'
        });

        expect(resOne).toEqual('background-image:url(https://avatars.mds.yandex.net/get-vh/1/2/1920x1080)');
    });

    it('должен менять /orig на large размер для get-vh (авторетина + devicePixelRatio 1.3)', function() {
        setDPR(1.22);

        let resOne = execView('StreamThumbnail', {
            autoretina: true,
            thumbnail: 'https://avatars.mds.yandex.net/get-vh/1/2/orig',
            size: 'large'
        });

        expect(resOne).toEqual('background-image:url(https://avatars.mds.yandex.net/get-vh/1/2/936x524)');
    });

    it('должен менять /orig для get-ott', function() {
        let resOne = execView('StreamThumbnail', { thumbnail: 'https://avatars.mds.yandex.net/get-ott/1/2/orig' });

        expect(resOne).toEqual('background-image:url(https://avatars.mds.yandex.net/get-ott/1/2/200x150)');
    });

    describe('Hе изменяет исходный url ', function() {
        let error: jest.SpyInstance;

        beforeEach(function() {
            error = jest.spyOn(home, 'error').mockReturnValue(undefined);
        });

        afterEach(function() {
            error.mockRestore();
        });

        it('если он не содержит /orig', function() {
            let resOne = execView('StreamThumbnail', { thumbnail: 'https://avatars.mds.yandex.net/get-some/1/2/100x50' });

            expect(error.mock.calls).toHaveLength(1);

            expect(resOne).toEqual('background-image:url(https://avatars.mds.yandex.net/get-some/1/2/100x50)');
        });

        it('если не смог обработать урл', function() {
            let resOne = execView('StreamThumbnail', { thumbnail: 'https://avatars.mds.yandex.net/get-some-orig/1/2/orig' });

            expect(error.mock.calls).toHaveLength(1);

            expect(resOne).toEqual('background-image:url(https://avatars.mds.yandex.net/get-some-orig/1/2/orig)');
        });
    });
});
