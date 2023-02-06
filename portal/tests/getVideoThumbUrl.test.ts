import { logError } from '@lib/log/logError';
import { getVideoThumbUrl, VideoThumbOptions } from '../getVideoThumbUrl';

jest.mock('../../log/logError.ts', () => {
    return {
        logError: jest.fn().mockImplementation(() => {
            throw new Error('logError called!');
        })
    };
});
const mockedLogError = logError as jest.Mock;

describe('home._getVideoThumbUrl', function() {
    let baseAvatarsUrl = '//avatars.mds.yandex.net/get-video_frame/979386/ca65626a64ae1aefa66edee966b5f734';
    let brokenAvatarsUrl = '//avatars.mds.yandex.net/get-random/979386/ca65626a64ae1aefa66edee966b5f734';
    let baseThumbnailerUrl = '//video-tub-ru.yandex.net/i?id=fd9e8177f08a1d29d08e0866aa27ff2c-00-96';
    let baseSize = '320x180';

    function check(options: VideoThumbOptions & { result: string; message: string }) {
        test(options.message, () => {
            expect(getVideoThumbUrl(options)).toEqual(options.result);
        });
    }

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('бросает ошибки', function() {
        [
            {
                url: baseAvatarsUrl,
                catch: 'Bad size',
                message: 'No size'
            },
            {
                url: baseAvatarsUrl,
                size: 'x',
                catch: 'Bad size',
                message: 'Empty width or height'
            },
            {
                url: '',
                catch: 'Bad url',
                message: 'Empty url'
            },
            {
                catch: 'Bad url',
                message: 'No url'
            },
            {
                url: brokenAvatarsUrl,
                size: baseSize,
                catch: 'Namespace random not found',
                message: 'Not registered namespace'
            },
            {
                url: baseAvatarsUrl,
                size: '110x110',
                catch: 'Alias s110x110 not found in video_frame namespace',
                message: 'No alias in namespace'
            }
        ].forEach(function(options) {
            test(options.message, () => {
                mockedLogError.mockImplementation(() => {});

                expect(getVideoThumbUrl(options as VideoThumbOptions)).toEqual(options.url || '');
                expect(mockedLogError.mock.calls).toHaveLength(1);
                expect(mockedLogError.mock.calls[0][0].message).toEqual('Get address tumb video');
            });
        });
    });

    // eslint-disable-next-line jest/expect-expect
    describe('формирует ссылку в аватарницу', function() {
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

    describe('cформирует ссылку в тумбнейлер', function() {
        [
            {
                url: baseThumbnailerUrl,
                size: baseSize,
                result: '//video-tub-ru.yandex.net/i?id=fd9e8177f08a1d29d08e0866aa27ff2c-00-96&n=1040&w=320&h=180',
                message: 'simple'
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
                result: '//avatars.mds.yandex.net/i?id=82e2463bbb487b443d07d0f06f3515f90522-1097822-video_thumb_fresh&n=1040&w=320&h=180',
                message: 'simple 2'
            }
        ].forEach(check);
    });
});
