import { execView } from '@lib/views/execView';
import { mockReq, Req3ServerMocked } from '@lib/views/mockReq';
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { BannerYabs } from './banner-yabs.view';

describe('banner-yabs', function() {
    let req: Req3ServerMocked;

    beforeEach(() => {
        req = mockReq();
    });

    it('returns awaps img banner', function() {
        let data = {
            type: 'awaps_marketing',
            data: {
                banner_id: 3486151,
                bnCounts: [],
                name: 'awaps',
                click_url: 'banner_url',
                height: 90,
                hidpi_image: 'img_src',
                html5_iframe_src: '',
                image: 'image_url',
                image_alt: 'Московские Сезоны',
                not_show_stat_url: '',
                pl_priority: 2,
                source: 'html5_hidpi_desktop_banner',
                stat_delay_sec: 2,
                width: 728
            }
        };

        let res = execView(BannerYabs, data, req);
        expect(res).toMatchSnapshot();

        expect(req.resources.add.mock.calls).toHaveLength(1);
    });
});
