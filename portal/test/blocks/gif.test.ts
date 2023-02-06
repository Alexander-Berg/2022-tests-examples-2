import {
    IDivData,
    FixedSize,
    TemplateBlock,
    WrapContentSize, GifBlock
} from '../../src';

import {Template, TemplateCard, Templates} from '../../src/template';

describe('Gif tests', (): void => {
    it('should create simple gif block', (): void => {
        const divData: IDivData = {
            log_id: 'gifka',
            states: [
                {
                    state_id: 1,
                    div: new GifBlock({
                        gif_url: 'ya.ru'
                    })
                }
            ]
        };

        expect(divData).toMatchSnapshot();
    });

    it('should create reach gif block', (): void => {
        const divData: IDivData = {
            log_id: 'gifka',
            states: [
                {
                    state_id: 1,
                    div: new GifBlock({
                        gif_url: 'ya.ru',
                        action: {
                            log_id: 'log',
                            url: 'ya.ru',
                            referer: 'ya.com'
                        },
                        scale: "fill",
                        alpha: 0.1,
                        visibility_actions: [
                            {
                                url: 'ya.ru',
                                log_id: 'log'
                            }
                        ],
                        preload_required: 1,
                        aspect: {
                            ratio: 1
                        },
                        border: {
                            corner_radius: 1,
                            stroke: {width: 1, color: '#cc0'}
                        },
                        preview: 'testpreview'
                    })
                }
            ]
        };

        expect(divData).toMatchSnapshot();
    });


    it('should create card with gif template', (): void => {
        type NewBlocks = 'gif_block'
        const templates: Templates<NewBlocks> = new Templates<NewBlocks>([
            {
                type: 'gif_block',
                block: new GifBlock({
                    gif_url: new Template('url'),
                    height: new WrapContentSize(),
                    width: new FixedSize({value: 100})
                })
            }
        ]);

        const divData: IDivData = {
            log_id: 'gif/banner',
            states: [
                {
                    state_id: 1,
                    div: new TemplateBlock('gif_block', {
                        url: 'ya_ru',
                        border: {
                            corner_radius: 1,
                            stroke: {width: 1, color: '#cc0'}
                        }
                    })
                }
            ]
        };
        const card = new TemplateCard(templates, divData);

        expect(card).toMatchSnapshot();
    });
});
