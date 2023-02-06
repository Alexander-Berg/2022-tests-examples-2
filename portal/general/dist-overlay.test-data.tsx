import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { DistOverlay } from '@block/dist-overlay/dist-overlay.view';
import { Ads } from '@lib/utils/ads';

const makeReq = (theme: 'light' | 'dark') => {
    const req = mockReq({}, {
        Banners: {
            banners: {
                splashscreen: {
                    button_no: 'Нет, спасибо',
                    color: theme === 'dark' ? '000000' : 'ffffff',
                    button_yes: 'Установить',
                    product: 'browser',
                    url: 'https://yabs.yandex.ru/count/WWSejI_zO8u1xGy0r1a5A1_TSL4RBmK0ZW8GWY0nck11OG00000useqKG2P80c3c6N3WvjFiukUkiva1a06siVZHqe20W0AO0RQn-D5Ik068nABe8i012jW1hCQtdG7e0N3m0iBcyE09a0Fmmu1lvJigccxTksIf1uQt-70cIlTAi0U0W9Wqk0Ue1O3m2B3pgRRnizVPJFW8vj2loV0_oVWAWBKOgWiG0N9hc8Qt0026Esjr1ypm2mle39V0W80GF-NtgD7fhVVTW12MeOGVa13XwCI_qVQaeL3O4eU06E0IXu0OwHBgUt2PowKx9F0I30Ye4xAZa8gktwd3w1IC0jWLmOhsxAEFlFnZy90MN84Nc1VBqzCZg1S9m1Uq4h0OzQA7YWRG613u68hviBpGyBVDXG606P0P0Q0PgWEm6RWP____0T8P4dbXOdDVSsLoTcLoBt8rDZSjCkWPWC83y1c0mWE16l__0ryS5iY0c1hyy8W2i1havucBkFIju6xr6W40002m6sIu6mM270qnUJWwRcOqLbatJ5GtwHo07Vz_cHq00000003mFnu0RMJaNeQSJp9QsOfi4eKm37bSDl12dFaya4YbuR1VFKCuRglSUrSXM14GNDCCCyYiVx3axuT7zO40wknwavioQSG05m8ZByWN0HqPmDwv3SSu5SFQHID7g53PCGC0~1',
                    text: 'Попробуйте Яндекс.Браузер, который будет защищать ваш компьютер от вирусов и быстро загружать страницы и видео даже при медленном соединении.',
                    close_counter: '/close-counter',
                    title: 'Ваш браузер устарел. Хотите поменять браузер?',
                    icon_svg: 'https://avatars.mds.yandex.net/get-direct-picture/1674598/kS8bESbR92sYMpSOAVc1SQ/orig',
                    type: 'landin',
                    age_restriction: '0+',
                    bannerid: '72057605129702491:5401867807018760070',
                    button_color: theme === 'dark' ? '773377' : 'ffcc00',
                    linknext: '=WMiejI_zOB003Gi0j1AlTmSCi0509aW2OEOPSE3cq-pYvwwpcG6G0RQn-D7IW8200fW1jh7uqLAu0OZ4ekWYs06inhUT0UW1S903yCE0Rx030hW4_m6e1ge3i0U0W9Wqk0Ue1V470020y0YmywcsyRFNsKpu2ERGhydmFydu2e2r6DaBXhVuS2PAzqhe39UW3i24FO0Gbg647yWG2AWHm8Gzs1A7W1ZW4eU06EaIwdjmcSkbEoIO4mYe4xAZa8gktwd35UWKZ0BO5S6AzkoZZxpyOv0MN84Nc1VBqzCZm1Uq4h0OzQA7YWRu68hviBpGyBVDXG606Ha1e1cg0xWP____0UWPWC83y1c0mWE16l__0ryS5iY0c1hyy8W2zHe10000i1jak1i5wHo07Vz_cHq00000003mFn40NJEc6wJ4hn77khDLWUmOXaCZNMq0JpTjJWuABSMX6hOsOEG5-O8_HyO9n208h0hr0AC0~1'
                }
            }
        }
    });

    req.ads = new Ads(req);
    return req;
};

export const distOverlayDark = () => execView(DistOverlay, {}, makeReq('dark'));

export const distOverlayLight = () => execView(DistOverlay, {}, makeReq('light'));

const makeAltReq = () => {
    const req = mockReq({}, {
        Banners: {
            banners: {
                dist_overlay: {
                    icon: 'https://yastatic.net/s3/home/obi-wan__test/disticon.png',
                    title: 'Скачайте новый Яндекс.Браузер',
                    description: 'Яндекс.Браузер блокирует опасные сайты и при скачивании файлов проверяет их на вирусы. А также быстро загружает сайты и видео, даже если интернет медленный.',
                    agreement: 'Скачивая приложение, вы принимаете условия',
                    agreement_url: 'https://ya.ru',
                    button_text: 'Скачать',
                    button_url: 'https://yandex.ru/beta',
                    linknext: '//',
                    close_url: '//'
                }
            }
        }
    });

    req.ads = new Ads(req);
    return req;
};

export const distOverlayAlt = () => execView(DistOverlay, {}, makeAltReq());
