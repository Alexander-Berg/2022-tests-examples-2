import {
    ContainerBlock,
    FixedSize,
    IDivData,
    ImageBlock,
    SeparatorBlock,
    Template,
    TemplateCard,
    Templates,
    templateHelper,
    rewriteVars
} from '../../src';

describe('ContainerBlock test', (): void => {

    it('should create block with templates', (): void => {
        const tMap = rewriteVars({
            product_grid: new ContainerBlock({
                paddings: new Template('grid_paddings'),
                items: [
                    new ImageBlock({
                        width: new Template('top_image_width'),
                        height: new FixedSize({value: 40}),
                        image_url: new Template('top_image_url')
                    }),
                    new SeparatorBlock({
                        height: new Template('gap_height'),
                        delimiter_style: {
                            orientation: 'horizontal',
                            color: new Template('gap_color'),
                        }
                    }),
                    new ImageBlock({
                        width: new Template('bottom_image_width'),
                        height: new FixedSize({value: 40}),
                        image_url: new Template('bottom_image_url')
                    })
                ]
            })
        });

        const helper = templateHelper(tMap);

        const divData: IDivData = {
            log_id: 'id',
            states: [
                {
                    state_id: 1,
                    div: helper.product_grid({
                        top_image_url: 'https://image.url/top',
                        top_image_width: new FixedSize({value: 40}),
                        bottom_image_url: 'https://image.url/bottom',
                        bottom_image_width: new FixedSize({value: 40}),
                        gap_height: new FixedSize({value: 10}),
                        gap_color: '#000',
                        grid_paddings: {
                            left: 6,
                            right: 6,
                            top: 16,
                            bottom: 16,
                        },
                    })
                }
            ]
        };

        expect(new TemplateCard(new Templates(tMap), divData)).toMatchSnapshot();
    });

});
