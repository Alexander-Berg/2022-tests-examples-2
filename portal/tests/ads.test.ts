import { mockReq } from '@lib/views/mockReq';
import { logError } from '@lib/log/logError';
import { Ads } from '../ads';

jest.mock('../../log/logError.ts', () => {
    return {
        logError: jest.fn().mockImplementation(() => {
            throw new Error('logError called!');
        })
    };
});
const mockedLogError = logError as jest.Mock;

describe('home.ads', function() {
    let Banners = {
        pixelBase: 'https://pixel.base/path/',
        banners: {
            banner: {
                ad_nmb: '123',
                bnCounts: ['123'],
                click_url: '',
                height: 90,
                hidpi_image: '',
                html5_iframe_src: '',
                image: '',
                image_alt: '',
                linknext: '+banner',
                width: 180
            },
            popup: {
                linknext: '+popup'
            },
            teaser: {
                linknext: '+teaser'
            },
            qwe: {
                linknext: '+qwe'
            },
            zxc: {
                linknext: '+zxc'
            }
        },
        displayed: {
            'smart-banner': '+smart-banner',
            asd: '+asd'
        }
    };

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('баннеры отключены', function() {
        let ads = new Ads(mockReq({}, {
            Banners: {}
        }));

        test('отрицает наличие', function() {
            expect(ads.hasBanner('banner')).toEqual(false);
        });

        test('не возвращает баннер', function() {
            expect(ads.banner('banner')).toBeUndefined();
        });

        test('ничего не репортит', function() {
            expect(ads.report()).toEqual('<!--[home.ads] No pixel base-->');
        });
    });

    describe('есть только yabs', function() {
        let banner = {
            ad_nmb: '123',
            bnCounts: ['123'],
            click_url: '',
            height: 90,
            hidpi_image: '',
            html5_iframe_src: '',
            image: '',
            image_alt: '',
            width: 180
        };
        let ads = new Ads(mockReq({}, {
            Banners: {
                banners: {
                    banner
                },
                pixelBase: null,
                displayed: null
            }
        }));

        test('показывает наличие баннера', function() {
            expect(ads.hasBanner('banner')).toEqual(true);
        });

        test('отрицает наличие элементов yabs', function() {
            expect(ads.hasBanner('popup')).toEqual(false);
        });

        test('возвращает баннер', function() {
            expect(ads.banner('banner')).toEqual(banner);
        });

        test('не возвращает элементы yabs', function() {
            expect(ads.banner('popup')).toBeUndefined();
        });

        test('ничего не репортит', function() {
            expect(ads.report()).toEqual('<!--[home.ads] No pixel base-->');
        });
    });

    describe('hasBanner', function() {
        let ads: Ads;

        beforeEach(function() {
            ads = new Ads(mockReq({}, {
                Banners
            }));
        });

        test('без id', function() {
            mockedLogError.mockImplementation(() => {});
            // @ts-expect-error incorrect args
            expect(ads.hasBanner()).toEqual(false);
            expect(mockedLogError.mock.calls).toMatchSnapshot();
        });

        test('report', function() {
            mockedLogError.mockImplementation(() => {});
            expect(ads.hasBanner('report')).toEqual(false);
            expect(mockedLogError.mock.calls).toMatchSnapshot();
        });

        test('неизвестный id', function() {
            expect(ads.hasBanner('rty' as keyof Req3BannersMap)).toEqual(false);
        });

        test('известный id', function() {
            expect(ads.hasBanner('qwe' as keyof Req3BannersMap)).toEqual(true);
        });
    });

    describe('banner', function() {
        let ads: Ads;

        beforeEach(function() {
            ads = new Ads(mockReq({}, {
                Banners
            }));
        });

        test('возвращает существующий баннер', function() {
            expect(ads.banner('popup')).toEqual(Banners.banners.popup);
        });

        test('не возвращает несуществующий баннер', function() {
            expect(ads.banner('fake-banner' as keyof Req3BannersMap)).toBeUndefined();
        });

        test('засчитывает показ', function() {
            expect(ads.banner('qwe' as keyof Req3BannersMap)).toEqual(Banners.banners.qwe);
            expect(ads.banner('banner')).toEqual(Banners.banners.banner);

            const report = ads.report();
            expect(report).toContain('+qwe');
            expect(report).toContain('+banner');
        });

        test('не засчитывает показ не показаных баннеров', function() {
            expect(ads.banner('banner')).toEqual(Banners.banners.banner);

            let report = ads.report();
            expect(report).not.toContain('+qwe');
            expect(report).not.toContain('+zxc');
        });
    });

    describe('report', function() {
        let report: string;

        beforeEach(function() {
            let ads = new Ads(mockReq({}, {
                Banners
            }));
            report = ads.report();
        });

        test('репортит показы из перла', function() {
            expect(report).toContain(Banners.pixelBase);
            expect(report).toContain('+smart-banner');
            expect(report).toContain('+asd');
        });

        test('возвращает скрытую картинку', function() {
            expect(report).toMatch(/<img.+src="/);
            expect(report).toContain('style="display:none;position:absolute;"');
        });

        test('содержит параметр wmode', function() {
            expect(report).toMatch(/\bsrc="[^"]+\?wmode=0\b/);
        });

        test('не репортит пиксель без показов', function() {
            let ads = new Ads(mockReq({}, {
                Banners: {
                    pixelBase: 'https://pixel.base/path/',
                    banners: {
                        banner: {
                            linknext: '+banner'
                        } as unknown as Req3BannerYabs
                    }
                }
            }));
            report = ads.report();
            expect(report).toEqual('<!--[home.ads] No banners displayed-->');
        });

        test('повторный репорт возвращает пустую строчку', function() {
            let ads = new Ads(mockReq({}, {
                Banners
            }));
            expect(ads.report()).toBeTruthy();
            mockedLogError.mockImplementation(() => {});
            expect(ads.report()).toEqual('');
            expect(mockedLogError.mock.calls).toMatchSnapshot();
        });
    });

    describe('ручной режим репорта через {report:false} и getShowUrl', function() {
        let ads: Ads;

        beforeEach(function() {
            ads = new Ads(mockReq({}, {
                Banners
            }));
        });

        test('не возвращает несуществующий баннер', function() {
            expect(ads.banner('fake-banner' as keyof Req3BannersMap, { report: false })).toBeUndefined();
        });

        test('getShowUrl возвращает пустую строчку для несуществующего баннера', function() {
            expect(ads.getShowUrl('fake-banner' as keyof Req3BannersMap)).toEqual('');
        });

        test('не добавляет в report баннер, для которого передан report:false', function() {
            let popup = Banners.banners.popup;

            expect(ads.banner('popup', { report: false })).toEqual(popup);
            expect(ads.report()).not.toContain('popup.linknext');
        });

        test('возвращает ссылку с показом баннера', function() {
            expect(ads.getShowUrl('popup')).toEqual(Banners.pixelBase + Banners.banners.popup.linknext);
        });

        test('getShowUrl возвращает ссылку с показом баннера, вырезая linknext из _displayed', function() {
            let popup = Banners.banners.popup;

            ads.banner('popup');
            expect(ads.getShowUrl('popup')).toEqual(Banners.pixelBase + popup.linknext);
            expect(ads.report()).not.toContain(popup.linknext);
        });

        test('getShowUrl возвращает пустую строку для баннера, linknext которого уже был отгружен через report', function() {
            let popup = Banners.banners.popup;

            ads.banner('popup');
            expect(ads.report()).toContain(popup.linknext);
            mockedLogError.mockImplementation(() => {});
            expect(ads.getShowUrl('popup')).toEqual('');
            expect(mockedLogError.mock.calls).toMatchSnapshot();
        });
    });
});
