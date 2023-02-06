import { makeStyle } from '@lib/utils/makeStyle';
import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { BannerSlider } from './banner-slider.view';
import Req from './mocks/Req.json';

interface GetData {
    skin?: string;
    cardsOnly?: string;
    noBody?: string;
}
const get = (mock: Partial<Req3Server>, data?: GetData) => {
    const settingsJs = home.settingsJs([]);
    const req: Req3Server = mockReq({}, {
        settingsJs,
        ...mock,
        ab_flags: {
            fl_carousel: {
                value: '1'
            },
            arrows_inside: {
                value: '1'
            },
            'banner-slider_cards-only': {
                value: data?.cardsOnly || '0'
            },
            'banner-slider_no-body': {
                value: data?.noBody || '0'
            }
        },
        blocks_status: {
            enabled_blocks_count: 3,
            zen_enabled: 0
        }
    });
    const style = makeStyle({
        width: '640px',
        padding: '10px 40px',
        'background-color': '#f3f3f2'
    });
    const banner = execView(BannerSlider, {}, req);
    const script = <script>{settingsJs.getRawScript(req)}</script>;

    return {
        html: (
            <div class={'media-grid__media-content-main'}>
                <style>
                    {
                        `${req.cls.full('.banner-slider__ad-icon')} {
                            background: #4eb0da !important;
                        }`
                    }
                </style>
                {script}
                <div style={style} class={'test-container'}>
                    {banner}
                </div>
            </div>
        ),
        skin: data?.skin || ''
    };
};

export const slider = () => get(Req as unknown as Partial<Req3Server>);
export const sliderDark = () => get(Req as unknown as Partial<Req3Server>, { skin: 'night' });
export const sliderCardsOnly = () => get(Req as unknown as Partial<Req3Server>, { cardsOnly: '1' });
export const sliderCardsOnlyDark = () => get(Req as unknown as Partial<Req3Server>, { skin: 'night', cardsOnly: '1' });
export const sliderNoBody = () => get(Req as unknown as Partial<Req3Server>, { cardsOnly: '1', noBody: '1' });
export const sliderNoBodyDark = () => get(Req as unknown as Partial<Req3Server>, { skin: 'night', cardsOnly: '1', noBody: '1' });
