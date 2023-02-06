describe('home._getVideoThumbUrl', function() {
    var baseAvatarsUrl = '//avatars.mds.yandex.net/get-video_frame/979386/ca65626a64ae1aefa66edee966b5f734';
    var brokenAvatarsUrl = '//avatars.mds.yandex.net/get-random/979386/ca65626a64ae1aefa66edee966b5f734';
    var baseThumbnailerUrl = '//video-tub-ru.yandex.net/i?id=fd9e8177f08a1d29d08e0866aa27ff2c-00-96';
    var baseSize = '320x180';

    function check(options) {
        home._getVideoThumbUrl(options).should.equal(options.result, options.message);
    }

    it('бросает ошибки', function() {
        [
            {
                url: baseAvatarsUrl,
                'catch': 'Bad size',
                message: 'No size'
            },
            {
                url: baseAvatarsUrl,
                size: 'x',
                'catch': 'Bad size',
                message: 'Empty width or height'
            },
            {
                url: '',
                'catch': 'Bad url',
                message: 'Empty url'
            },
            {
                'catch': 'Bad url',
                message: 'No url'
            },
            {
                url: brokenAvatarsUrl,
                size: baseSize,
                'catch': 'Namespace random not found',
                message: 'Not registered namespace'
            },
            {
                url: baseAvatarsUrl,
                size: '110x110',
                'catch': 'Alias s110x110 not found in video_frame namespace',
                message: 'No alias in namespace'
            }
        ].forEach(function(options) {
            expect(function() {
                home._getVideoThumbUrl(options);
            }).to.throw(Error, options.catch, options.message);
        });
    });

    it('формирует ссылку в аватарницу', function() {
        [
            {
                url: baseAvatarsUrl,
                size: baseSize,
                result: '//avatars.mds.yandex.net/get-video_frame/979386/ca65626a64ae1aefa66edee966b5f734/320x180',
                message: 'without slash'
            },
            {
                url: baseAvatarsUrl + '/',
                size: baseSize,
                result: '//avatars.mds.yandex.net/get-video_frame/979386/ca65626a64ae1aefa66edee966b5f734/320x180',
                message: 'ignores slash'
            },
            {
                url: baseAvatarsUrl + '/320x180',
                size: baseSize,
                result: '//avatars.mds.yandex.net/get-video_frame/979386/ca65626a64ae1aefa66edee966b5f734/320x180',
                message: 'do not dublicate alias'
            },
            {
                url: baseAvatarsUrl,
                size: baseSize,
                retinaScale: 2,
                result: '//avatars.mds.yandex.net/get-video_frame/979386/ca65626a64ae1aefa66edee966b5f734/640x360',
                message: 'select correct size for retinaScale=2'
            }
        ].forEach(check);

    });

    it('cформирует ссылку в тумбнейлер', function() {
        [
            {
                url: baseThumbnailerUrl,
                size: baseSize,
                result: '//video-tub-ru.yandex.net/i?id=fd9e8177f08a1d29d08e0866aa27ff2c-00-96&n=1040&w=320&h=180'
            },
            {
                url: baseThumbnailerUrl,
                size: baseSize,
                retinaScale: 2,
                result: '//video-tub-ru.yandex.net/i?id=fd9e8177f08a1d29d08e0866aa27ff2c-00-96&n=1040&w=640&h=360',
                message: 'select correct size for retinaScale=2'
            },
            {
                url: '//avatars.mds.yandex.net/i?id=82e2463bbb487b443d07d0f06f3515f90522-1097822-video_thumb_fresh',
                size: baseSize,
                result: '//avatars.mds.yandex.net/i?id=82e2463bbb487b443d07d0f06f3515f90522-1097822-video_thumb_fresh&n=1040&w=320&h=180'
            }
        ].forEach(check);
    });
});
