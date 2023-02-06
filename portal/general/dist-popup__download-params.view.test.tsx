import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import {
    DistPopup__downloadParams,
    DistPopup__downloadParamsData
} from '@block/dist-popup/__download-params/dist-popup__download-params.view';

describe('dist-popup__download-params', function() {
    const req = mockReq();

    it('for type!=download doing nothing', function() {
        const data = {
            popup: {},
            js: {}
        } as DistPopup__downloadParamsData;

        const params = execView(DistPopup__downloadParams, data, req);

        expect(params).toHaveProperty('popup');
        expect(params).toHaveProperty('js');
    });

    describe('yabs', function() {
        it('type=download', function() {
            let data = {
                popup: {
                    from_yabs: true,
                    type: 'download',
                    install_text: 'sample of install text',
                    counters: {},
                    install_yes: 'sample of install_yes',
                    legal: {
                        text: 'legal text',
                        link: 'legal link',
                        linkText: 'legal linkText'
                    },
                    position: 'right-top',
                    guide_image: 'sample url of guide_image'
                },
                js: {
                    counters: {}
                }
            } as unknown as DistPopup__downloadParamsData;

            expect(execView(DistPopup__downloadParams, data, req).js).toEqual({
                text: data.popup.install_text,
                counters: {
                    click: data.popup.install_yes
                },
                mods: {
                    image: 'yes',
                    position: data.popup.position
                },
                attrs: {
                    style: 'background-image: url(' + data.popup.guide_image + ');'
                }
            });
        });
    });
});
