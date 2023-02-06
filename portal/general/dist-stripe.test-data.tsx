import { Ads } from '@lib/utils/ads';
import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { DistStripe } from './dist-stripe.view';

const get = (designType: string, skin: string, isColored?: boolean) => {
    const req = mockReq({}, {
        Banners: {
            banners: {
                popup: {
                    color: isColored ? 'e57bce' : '',
                    icon_svg: '[% mockSvg %]',
                    button_yes: 'Скачать',
                    channel: '',
                    text: 'Удобный и быстрый Яндекс Браузер с переводом видео',
                    url: 'url',
                    type: 'landing',
                    age_restriction: '0+',
                    button_color: '',
                    linknext: 'link',
                    design_type: designType
                }
            }
        }
    });

    const ads = new Ads(req);
    req.ads = ads;

    const style = (
        <style>
            {
                `body {
                    font: 'YS Text','Helvetica Neue',Arial,sans-serif;
                }
                .dist-stripe__icon {
                    background: #000 !important;
                }`
            }
        </style>
    );
    const html = (
        <>
            {style}
            {execView(DistStripe, {}, req)}
        </>
    );

    return {
        html,
        skin
    };
};

export const light = () => get('stripe-default', '');
export const dark = () => get('stripe-default', 'night');
export const colored = () => get('stripe-default', '', true);
export const big = () => get('stripe-big', '');
