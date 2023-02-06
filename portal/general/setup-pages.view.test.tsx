import { execView } from '@lib/views/execView';
import { SetupPages } from '@block/setup-pages/setup-pages.view';
import { mockReq } from '@lib/views/mockReq';

describe('setup-pages', () => {
    describe('десктопный тюн', () => {
        it('без retpath', () => {
            expect(execView(SetupPages, mockReq({}, {
                MordaContent: 'big',
                MordaZone: 'ee',
                RetpathUnescaped: undefined as unknown as string
            }))).toEqual({
                all: 'https://yandex.ee/tune/?nosync=1',
                common: 'https://yandex.ee/tune/search?nosync=1',
                region: 'https://yandex.ee/tune/geo?nosync=1',
                places: 'https://yandex.ee/tune/places?nosync=1',
                lang: 'https://yandex.ee/tune/lang?nosync=1',
                tune: 'https://yandex.ee/tune/'
            });
        });

        it('с retpath', () => {
            expect(execView(SetupPages, mockReq({}, {
                RetpathUnescaped: 'https://ya.ru?foo=bar+baz',
                MordaContent: 'big',
                MordaZone: 'ee'
            }))).toEqual({
                all: 'https://yandex.ee/tune/?retpath=https%3A%2F%2Fya.ru%3Ffoo%3Dbar%2Bbaz&nosync=1',
                common: 'https://yandex.ee/tune/search?retpath=https%3A%2F%2Fya.ru%3Ffoo%3Dbar%2Bbaz&nosync=1',
                region: 'https://yandex.ee/tune/geo?retpath=https%3A%2F%2Fya.ru%3Ffoo%3Dbar%2Bbaz&nosync=1',
                places: 'https://yandex.ee/tune/places?retpath=https%3A%2F%2Fya.ru%3Ffoo%3Dbar%2Bbaz&nosync=1',
                lang: 'https://yandex.ee/tune/lang?retpath=https%3A%2F%2Fya.ru%3Ffoo%3Dbar%2Bbaz&nosync=1',
                tune: 'https://yandex.ee/tune/'
            });
        });

        it('гермиона', () => {
            expect(execView(SetupPages, mockReq({}, {
                DevInstance: 1,
                is_hermione: 1,
                MordaContent: 'big',
                MordaZone: 'ee',
                RetpathUnescaped: undefined as unknown as string
            }))).toEqual({
                all: 'https://yandex.ee/tune/?nosync=1',
                common: 'https://yandex.ee/tune/search?nosync=1',
                region: 'https://yandex.ee/tune/geo?nosync=1',
                places: 'https://yandex.ee/tune/places?nosync=1',
                lang: 'https://yandex.ee/tune/lang?nosync=1',
                tune: 'https://yandex.ee/tune/'
            });
        });

        it('девинстанс', () => {
            expect(execView(SetupPages, mockReq({}, {
                DevInstance: 1,
                MordaContent: 'big',
                MordaZone: 'ee',
                RetpathUnescaped: undefined as unknown as string
            }))).toEqual({
                all: 'https://l7test.yandex.ee/tune-rc/?nosync=1',
                common: 'https://l7test.yandex.ee/tune-rc/search?nosync=1',
                region: 'https://l7test.yandex.ee/tune-rc/geo?nosync=1',
                places: 'https://l7test.yandex.ee/tune-rc/places?nosync=1',
                lang: 'https://l7test.yandex.ee/tune-rc/lang?nosync=1',
                tune: 'https://l7test.yandex.ee/tune-rc/'
            });
        });
    });
});

describe('мобильный тюн', () => {
    it('без retpath', () => {
        expect(execView(SetupPages, mockReq({}, {
            MordaContent: 'touch',
            MordaZone: 'ee',
            RetpathUnescaped: undefined as unknown as string
        }))).toEqual({
            all: 'https://yandex.ee/tune/?nosync=1',
            common: 'https://yandex.ee/tune/common?nosync=1',
            region: 'https://yandex.ee/tune/geo?nosync=1',
            places: 'https://yandex.ee/tune/places?nosync=1',
            lang: 'https://yandex.ee/tune/lang?nosync=1',
            tune: 'https://yandex.ee/tune/'
        });
    });

    it('с retpath', () => {
        expect(execView(SetupPages, mockReq({}, {
            RetpathUnescaped: 'https://ya.ru?foo=bar+baz',
            MordaContent: 'touch',
            MordaZone: 'ee'
        }))).toEqual({
            all: 'https://yandex.ee/tune/?retpath=https%3A%2F%2Fya.ru%3Ffoo%3Dbar%2Bbaz&nosync=1',
            common: 'https://yandex.ee/tune/common?retpath=https%3A%2F%2Fya.ru%3Ffoo%3Dbar%2Bbaz&nosync=1',
            region: 'https://yandex.ee/tune/geo?retpath=https%3A%2F%2Fya.ru%3Ffoo%3Dbar%2Bbaz&nosync=1',
            places: 'https://yandex.ee/tune/places?retpath=https%3A%2F%2Fya.ru%3Ffoo%3Dbar%2Bbaz&nosync=1',
            lang: 'https://yandex.ee/tune/lang?retpath=https%3A%2F%2Fya.ru%3Ffoo%3Dbar%2Bbaz&nosync=1',
            tune: 'https://yandex.ee/tune/'
        });
    });

    it('гермиона', () => {
        expect(execView(SetupPages, mockReq({}, {
            DevInstance: 1,
            is_hermione: 1,
            MordaContent: 'touch',
            MordaZone: 'ee',
            RetpathUnescaped: undefined as unknown as string
        }))).toEqual({
            all: 'https://yandex.ee/tune/?nosync=1',
            common: 'https://yandex.ee/tune/common?nosync=1',
            region: 'https://yandex.ee/tune/geo?nosync=1',
            places: 'https://yandex.ee/tune/places?nosync=1',
            lang: 'https://yandex.ee/tune/lang?nosync=1',
            tune: 'https://yandex.ee/tune/'
        });
    });

    it('девинстанс', () => {
        expect(execView(SetupPages, mockReq({}, {
            DevInstance: 1,
            MordaContent: 'touch',
            MordaZone: 'ee',
            RetpathUnescaped: undefined as unknown as string
        }))).toEqual({
            all: 'https://l7test.yandex.ee/tune-rc/?nosync=1',
            common: 'https://l7test.yandex.ee/tune-rc/common?nosync=1',
            region: 'https://l7test.yandex.ee/tune-rc/geo?nosync=1',
            places: 'https://l7test.yandex.ee/tune-rc/places?nosync=1',
            lang: 'https://l7test.yandex.ee/tune-rc/lang?nosync=1',
            tune: 'https://l7test.yandex.ee/tune-rc/'
        });
    });
});
